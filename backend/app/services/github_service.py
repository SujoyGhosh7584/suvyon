import base64
from datetime import datetime, timedelta, timezone
import json
import re
import secrets
from urllib.parse import quote
from uuid import UUID

import httpx
from jose import JWTError, jwt
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.ai.providers.base import LLMMessage
from app.ai.router import route_chat
from app.core.config import settings
from app.core.token_blacklist import blacklist_token, is_blacklisted
from app.models.github_project import GitHubChangeProposal, GitHubInstallation, GitHubProject
from app.models.user import User
from app.models.workspace import Workspace
from app.services.api_key_service import ApiKeyService

_TEXT_EXTENSIONS = {
    ".py", ".ts", ".tsx", ".js", ".jsx", ".json", ".md", ".txt", ".yml", ".yaml",
    ".toml", ".ini", ".cfg", ".html", ".css", ".scss", ".sql", ".sh", ".ps1", ".java",
    ".go", ".rs", ".rb", ".php", ".cs", ".cpp", ".c", ".h", ".kt", ".swift", ".vue",
}
_SKIP_PARTS = {"node_modules", "dist", "build", ".git", ".next", "vendor", "coverage"}
_DENIED_CHANGE_NAMES = {
    ".env", ".env.local", "package-lock.json", "yarn.lock", "pnpm-lock.yaml",
    "poetry.lock", "pdm.lock", "cargo.lock", "composer.lock",
}


class GitHubService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.api_keys: dict[str, str] = {}

    def use_user_api_keys(self, user_id: UUID) -> None:
        self.api_keys = ApiKeyService(self.session).decrypted_for_user(user_id)

    def _app_jwt(self) -> str:
        if not settings.GITHUB_APP_ID or not settings.GITHUB_APP_PRIVATE_KEY:
            raise RuntimeError("GitHub App credentials are not configured.")
        now = datetime.now(timezone.utc)
        private_key = settings.GITHUB_APP_PRIVATE_KEY.replace("\\n", "\n")
        return jwt.encode(
            {"iat": now - timedelta(seconds=30), "exp": now + timedelta(minutes=9), "iss": settings.GITHUB_APP_ID},
            private_key,
            algorithm="RS256",
        )

    def _headers(self, token: str) -> dict[str, str]:
        return {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "Suvyon",
        }

    def _request(self, method: str, path: str, *, token: str, **kwargs) -> dict:
        response = httpx.request(
            method,
            f"https://api.github.com{path}",
            headers=self._headers(token),
            timeout=30,
            **kwargs,
        )
        if response.is_error:
            detail = response.json().get("message", response.text) if response.content else response.reason_phrase
            raise RuntimeError(f"GitHub API error ({response.status_code}): {detail}")
        return response.json() if response.content else {}

    def create_install_state(self, user_id: UUID, workspace_id: UUID) -> str:
        return jwt.encode(
            {
                "sub": str(user_id), "workspace_id": str(workspace_id), "type": "github_install",
                "jti": secrets.token_urlsafe(24),
                "exp": datetime.now(timezone.utc) + timedelta(minutes=15),
            },
            settings.SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )

    def consume_install_state(self, state: str) -> tuple[UUID, UUID]:
        try:
            payload = jwt.decode(state, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
            if payload.get("type") != "github_install" or is_blacklisted(payload["jti"]):
                raise JWTError("Invalid state")
            result = UUID(payload["sub"]), UUID(payload["workspace_id"])
        except (JWTError, KeyError, ValueError) as exc:
            raise ValueError("GitHub installation state is invalid or expired.") from exc
        blacklist_token(payload["jti"])
        return result

    def installation_url(self, state: str) -> str:
        if not settings.GITHUB_APP_SLUG:
            raise RuntimeError("GitHub App is not configured.")
        return f"https://github.com/apps/{quote(settings.GITHUB_APP_SLUG)}/installations/new?state={quote(state)}"

    def save_installation(self, user_id: UUID, workspace_id: UUID, installation_id: int) -> GitHubInstallation:
        user = self.session.get(User, user_id)
        workspace = self.session.get(Workspace, workspace_id)
        if user is None or workspace is None or workspace.owner_id != user_id:
            raise ValueError("The installation workspace is no longer available.")
        data = self._request("GET", f"/app/installations/{installation_id}", token=self._app_jwt())
        existing = self.session.execute(
            select(GitHubInstallation).where(
                GitHubInstallation.user_id == user_id,
                GitHubInstallation.installation_id == installation_id,
            )
        ).scalar_one_or_none()
        installation = existing or GitHubInstallation(user_id=user_id, installation_id=installation_id)
        installation.account_login = (data.get("account") or {}).get("login")
        if not existing:
            self.session.add(installation)
        self.session.commit()
        self.session.refresh(installation)
        return installation

    def _installation_token(self, installation: GitHubInstallation) -> str:
        data = self._request(
            "POST", f"/app/installations/{installation.installation_id}/access_tokens", token=self._app_jwt()
        )
        return data["token"]

    def list_repositories(self, user_id: UUID) -> list[dict]:
        installations = self.session.execute(
            select(GitHubInstallation).where(GitHubInstallation.user_id == user_id)
        ).scalars().all()
        result: list[dict] = []
        for installation in installations:
            data = self._request(
                "GET", "/installation/repositories?per_page=100", token=self._installation_token(installation)
            )
            for repo in data.get("repositories", []):
                result.append({
                    "installation_id": installation.id,
                    "github_repo_id": repo["id"],
                    "full_name": repo["full_name"],
                    "default_branch": repo.get("default_branch") or "main",
                    "is_private": bool(repo.get("private")),
                })
        return result

    def revoke_user_installations(self, user_id: UUID) -> None:
        installations = self.session.execute(
            select(GitHubInstallation).where(GitHubInstallation.user_id == user_id)
        ).scalars().all()
        for installation in installations:
            references = self.session.scalar(
                select(func.count()).select_from(GitHubInstallation).where(
                    GitHubInstallation.installation_id == installation.installation_id,
                    GitHubInstallation.user_id != user_id,
                )
            )
            if not references:
                self._request(
                    "DELETE",
                    f"/app/installations/{installation.installation_id}",
                    token=self._app_jwt(),
                )

    def connect_project(self, *, user_id: UUID, workspace_id: UUID, installation_id: UUID, github_repo_id: int) -> GitHubProject:
        available = next(
            (item for item in self.list_repositories(user_id) if item["installation_id"] == installation_id and item["github_repo_id"] == github_repo_id),
            None,
        )
        if not available:
            raise ValueError("That repository is not available to this GitHub installation.")
        existing = self.session.execute(
            select(GitHubProject).where(
                GitHubProject.workspace_id == workspace_id,
                GitHubProject.github_repo_id == github_repo_id,
            )
        ).scalar_one_or_none()
        if existing:
            return existing
        project = GitHubProject(user_id=user_id, workspace_id=workspace_id, **available)
        self.session.add(project)
        self.session.commit()
        self.session.refresh(project)
        return project

    def list_projects(self, user_id: UUID, workspace_id: UUID) -> list[GitHubProject]:
        stmt = select(GitHubProject).where(
            GitHubProject.user_id == user_id, GitHubProject.workspace_id == workspace_id
        ).order_by(GitHubProject.created_at.desc())
        return list(self.session.execute(stmt).scalars().all())

    def get_project(self, project_id: UUID, user_id: UUID, workspace_id: UUID) -> GitHubProject | None:
        stmt = select(GitHubProject).where(
            GitHubProject.id == project_id,
            GitHubProject.user_id == user_id,
            GitHubProject.workspace_id == workspace_id,
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def remove_project(self, project: GitHubProject) -> None:
        self.session.delete(project)
        self.session.commit()

    def _project_token(self, project: GitHubProject) -> str:
        installation = self.session.get(GitHubInstallation, project.installation_id)
        if installation is None:
            raise ValueError("GitHub installation no longer exists.")
        return self._installation_token(installation)

    def _tree(self, project: GitHubProject) -> tuple[str, list[dict]]:
        token = self._project_token(project)
        ref = self._request("GET", f"/repos/{project.full_name}/git/ref/heads/{quote(project.default_branch, safe='')}", token=token)
        sha = ref["object"]["sha"]
        tree = self._request("GET", f"/repos/{project.full_name}/git/trees/{sha}?recursive=1", token=token)
        files = [item for item in tree.get("tree", []) if item.get("type") == "blob" and self._allowed_path(item.get("path", ""), item.get("size", 0))]
        return sha, files

    @staticmethod
    def _allowed_path(path: str, size: int) -> bool:
        parts = set(path.split("/"))
        suffix = "." + path.rsplit(".", 1)[-1].lower() if "." in path else ""
        return not (parts & _SKIP_PARTS) and suffix in _TEXT_EXTENSIONS and size <= 120_000

    @staticmethod
    def _allowed_change_path(path: str, size: int) -> bool:
        normalized = path.strip().replace("\\", "/")
        name = normalized.rsplit("/", 1)[-1].lower()
        lowered = normalized.lower()
        if (
            not normalized
            or normalized.startswith("/")
            or ".." in normalized.split("/")
            or lowered.startswith(".github/workflows/")
            or name in _DENIED_CHANGE_NAMES
            or name.endswith((".pem", ".key", ".p12", ".pfx"))
        ):
            return False
        return GitHubService._allowed_path(normalized, size)

    def _read_file(self, project: GitHubProject, path: str, token: str | None = None, ref: str | None = None) -> tuple[str, str | None]:
        data = self._request(
            "GET",
            f"/repos/{project.full_name}/contents/{quote(path, safe='/')}?ref={quote(ref or project.default_branch, safe='')}",
            token=token or self._project_token(project),
        )
        if data.get("encoding") != "base64":
            return "", data.get("sha")
        return base64.b64decode(data.get("content", "")).decode("utf-8", errors="replace"), data.get("sha")

    def context(self, project: GitHubProject, query: str, limit: int = 14) -> tuple[str, list[str]]:
        _, tree = self._tree(project)
        terms = {term for term in re.findall(r"[a-zA-Z0-9_]+", query.lower()) if len(term) > 2}
        def score(item: dict) -> tuple[int, int]:
            path = item["path"].lower()
            hits = sum(4 for term in terms if term in path)
            if path.endswith(("readme.md", "package.json", "pyproject.toml", "requirements.txt")):
                hits += 5
            return hits, -len(path)
        selected = sorted(tree, key=score, reverse=True)[:limit]
        token = self._project_token(project)
        blocks, paths, total = [], [], 0
        for item in selected:
            content, _ = self._read_file(project, item["path"], token=token)
            if not content:
                continue
            content = content[:20_000]
            if total + len(content) > 70_000:
                break
            paths.append(item["path"])
            blocks.append(f"FILE: {item['path']}\n{content}")
            total += len(content)
        return "\n\n".join(blocks), paths

    def answer(self, project: GitHubProject, question: str) -> tuple[str, list[str]]:
        context, paths = self.context(project, question)
        response = route_chat([
            LLMMessage(role="system", content="Answer only from the supplied repository files. Cite filenames in backticks. Clearly say when evidence is missing."),
            LLMMessage(role="user", content=f"Repository: {project.full_name}\nQuestion: {question}\n\n{context}"),
        ], api_keys=self.api_keys)
        return response.content, paths

    def documentation(self, project: GitHubProject, instructions: str) -> tuple[str, list[str]]:
        context, paths = self.context(project, f"README architecture setup API {instructions}", limit=22)
        response = route_chat([
            LLMMessage(role="system", content="Create accurate Markdown documentation from repository evidence. Cite relevant file paths and do not invent commands or capabilities."),
            LLMMessage(role="user", content=f"Repository: {project.full_name}\nInstructions: {instructions}\n\n{context}"),
        ], api_keys=self.api_keys)
        return response.content, paths

    def propose(self, project: GitHubProject, user_id: UUID, instruction: str) -> GitHubChangeProposal:
        base_sha, _ = self._tree(project)
        context, _ = self.context(project, instruction, limit=18)
        response = route_chat([
            LLMMessage(role="system", content=(
                "Propose a small safe repository change. Return only JSON: "
                '{"title":"...","description":"...","changes":[{"path":"...","content":"complete file content","reason":"..."}]}. '
                "Return at most 5 complete text files. Never edit secrets, lock files, generated files, or .github/workflows."
            )),
            LLMMessage(role="user", content=f"Repository: {project.full_name}\nRequest: {instruction}\n\n{context}"),
        ], api_keys=self.api_keys)
        raw = response.content.strip()
        if raw.startswith("```"):
            raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw, flags=re.I | re.S)
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError("The model did not return a valid change proposal. Please try a smaller request.") from exc
        changes = data.get("changes") or []
        if not 1 <= len(changes) <= 5:
            raise ValueError("A proposal must contain between 1 and 5 file changes.")
        for change in changes:
            path = str(change.get("path", "")).strip().replace("\\", "/")
            content = str(change.get("content", ""))
            if not self._allowed_change_path(path, len(content.encode("utf-8"))):
                raise ValueError(f"Unsafe proposed path: {path or 'empty'}")
            change["path"] = path
            change["content"] = content
        proposal = GitHubChangeProposal(
            project_id=project.id,
            user_id=user_id,
            instruction=instruction,
            title=str(data.get("title") or "Suvyon proposed change")[:255],
            description=str(data.get("description") or instruction),
            changes=changes,
            base_sha=base_sha,
            status="pending",
        )
        self.session.add(proposal)
        self.session.commit()
        self.session.refresh(proposal)
        return proposal

    def get_proposal(self, proposal_id: UUID, project: GitHubProject, user_id: UUID) -> GitHubChangeProposal | None:
        stmt = select(GitHubChangeProposal).where(
            GitHubChangeProposal.id == proposal_id,
            GitHubChangeProposal.project_id == project.id,
            GitHubChangeProposal.user_id == user_id,
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def create_pull_request(self, project: GitHubProject, proposal: GitHubChangeProposal) -> str:
        if proposal.status != "pending":
            raise ValueError("This proposal is no longer pending.")
        token = self._project_token(project)
        branch = f"suvyon/{str(proposal.id)[:8]}"
        try:
            current_ref = self._request(
                "GET",
                f"/repos/{project.full_name}/git/ref/heads/{quote(project.default_branch, safe='')}",
                token=token,
            )
            if current_ref["object"]["sha"] != proposal.base_sha:
                raise ValueError(
                    "The default branch changed after this proposal was generated. Generate a fresh proposal."
                )
            self._request("POST", f"/repos/{project.full_name}/git/refs", token=token, json={"ref": f"refs/heads/{branch}", "sha": proposal.base_sha})
            for change in proposal.changes:
                try:
                    _, current_sha = self._read_file(
                        project, change["path"], token=token, ref=project.default_branch
                    )
                except RuntimeError as exc:
                    if "GitHub API error (404)" not in str(exc):
                        raise
                    current_sha = None
                payload = {
                    "message": f"Suvyon: {proposal.title}",
                    "content": base64.b64encode(change["content"].encode()).decode(),
                    "branch": branch,
                }
                if current_sha:
                    payload["sha"] = current_sha
                self._request("PUT", f"/repos/{project.full_name}/contents/{quote(change['path'], safe='/')}", token=token, json=payload)
            pull = self._request("POST", f"/repos/{project.full_name}/pulls", token=token, json={
                "title": proposal.title, "body": proposal.description, "head": branch, "base": project.default_branch,
            })
            proposal.status = "opened"
            proposal.pull_request_url = pull["html_url"]
            self.session.commit()
            return proposal.pull_request_url
        except Exception:
            self.session.rollback()
            proposal.status = "failed"
            self.session.commit()
            raise
