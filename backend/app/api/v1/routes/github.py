from typing import Annotated
from urllib.parse import quote
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import RedirectResponse

from app.api.dependencies import get_github_service, get_workspace_service
from app.api.security import get_current_verified_user
from app.core.config import settings
from app.models.user import User
from app.schemas.github import (
    ApproveProposalRequest,
    ChangeProposalRequest,
    ChangeProposalResponse,
    GitHubProjectConnect,
    GitHubProjectResponse,
    GitHubRepositoryOption,
    RepositoryAnswer,
    RepositoryDocumentationRequest,
    RepositoryQuestion,
)
from app.services.github_service import GitHubService
from app.services.workspace_service import WorkspaceService

router = APIRouter(tags=["GitHub"])


def _workspace(workspace_id, user, service):
    workspace = service.get_workspace(workspace_id=workspace_id, owner_id=user.id)
    if workspace is None:
        raise HTTPException(status_code=404, detail="Workspace not found.")
    return workspace


def _project(project_id, workspace_id, user, service):
    project = service.get_project(project_id, user.id, workspace_id)
    if project is None:
        raise HTTPException(status_code=404, detail="GitHub project not found.")
    return project


@router.get("/workspaces/{workspace_id}/github/install")
def install_github_app(
    workspace_id: UUID,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    workspace_service: Annotated[WorkspaceService, Depends(get_workspace_service)],
    github_service: Annotated[GitHubService, Depends(get_github_service)],
) -> dict[str, str]:
    _workspace(workspace_id, current_user, workspace_service)
    try:
        state_value = github_service.create_install_state(current_user.id, workspace_id)
        return {"url": github_service.installation_url(state_value)}
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc))


@router.get("/github/install/callback")
def github_install_callback(
    installation_id: Annotated[int, Query()],
    state_value: Annotated[str, Query(alias="state")],
    github_service: Annotated[GitHubService, Depends(get_github_service)],
) -> RedirectResponse:
    try:
        user_id, workspace_id = github_service.consume_install_state(state_value)
        github_service.save_installation(user_id, workspace_id, installation_id)
        return RedirectResponse(
            f"{settings.FRONTEND_URL.rstrip('/')}/app/w/{workspace_id}/github?connected=1"
        )
    except Exception as exc:
        return RedirectResponse(
            f"{settings.FRONTEND_URL.rstrip('/')}/app?github_error={quote(str(exc)[:300])}"
        )


@router.get("/github/repositories", response_model=list[GitHubRepositoryOption])
def available_repositories(
    current_user: Annotated[User, Depends(get_current_verified_user)],
    github_service: Annotated[GitHubService, Depends(get_github_service)],
):
    return github_service.list_repositories(current_user.id)


@router.get("/workspaces/{workspace_id}/github/projects", response_model=list[GitHubProjectResponse])
def list_projects(
    workspace_id: UUID,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    workspace_service: Annotated[WorkspaceService, Depends(get_workspace_service)],
    github_service: Annotated[GitHubService, Depends(get_github_service)],
):
    _workspace(workspace_id, current_user, workspace_service)
    return github_service.list_projects(current_user.id, workspace_id)


@router.post("/workspaces/{workspace_id}/github/projects", response_model=GitHubProjectResponse, status_code=201)
def connect_project(
    workspace_id: UUID,
    request: GitHubProjectConnect,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    workspace_service: Annotated[WorkspaceService, Depends(get_workspace_service)],
    github_service: Annotated[GitHubService, Depends(get_github_service)],
):
    _workspace(workspace_id, current_user, workspace_service)
    try:
        return github_service.connect_project(
            user_id=current_user.id,
            workspace_id=workspace_id,
            installation_id=request.installation_id,
            github_repo_id=request.github_repo_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.delete("/workspaces/{workspace_id}/github/projects/{project_id}", status_code=204)
def disconnect_project(
    workspace_id: UUID,
    project_id: UUID,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    workspace_service: Annotated[WorkspaceService, Depends(get_workspace_service)],
    github_service: Annotated[GitHubService, Depends(get_github_service)],
) -> None:
    _workspace(workspace_id, current_user, workspace_service)
    github_service.remove_project(_project(project_id, workspace_id, current_user, github_service))


@router.post("/workspaces/{workspace_id}/github/projects/{project_id}/ask", response_model=RepositoryAnswer)
def ask_project(
    workspace_id: UUID,
    project_id: UUID,
    request: RepositoryQuestion,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    workspace_service: Annotated[WorkspaceService, Depends(get_workspace_service)],
    github_service: Annotated[GitHubService, Depends(get_github_service)],
):
    _workspace(workspace_id, current_user, workspace_service)
    project = _project(project_id, workspace_id, current_user, github_service)
    content, files = github_service.answer(project, request.question)
    return RepositoryAnswer(content=content, files=files)


@router.post("/workspaces/{workspace_id}/github/projects/{project_id}/documentation", response_model=RepositoryAnswer)
def document_project(
    workspace_id: UUID,
    project_id: UUID,
    request: RepositoryDocumentationRequest,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    workspace_service: Annotated[WorkspaceService, Depends(get_workspace_service)],
    github_service: Annotated[GitHubService, Depends(get_github_service)],
):
    _workspace(workspace_id, current_user, workspace_service)
    project = _project(project_id, workspace_id, current_user, github_service)
    content, files = github_service.documentation(project, request.instructions)
    return RepositoryAnswer(content=content, files=files)


@router.post("/workspaces/{workspace_id}/github/projects/{project_id}/proposals", response_model=ChangeProposalResponse)
def propose_change(
    workspace_id: UUID,
    project_id: UUID,
    request: ChangeProposalRequest,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    workspace_service: Annotated[WorkspaceService, Depends(get_workspace_service)],
    github_service: Annotated[GitHubService, Depends(get_github_service)],
):
    _workspace(workspace_id, current_user, workspace_service)
    project = _project(project_id, workspace_id, current_user, github_service)
    try:
        return github_service.propose(project, current_user.id, request.instruction)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.post("/workspaces/{workspace_id}/github/projects/{project_id}/proposals/{proposal_id}/approve", response_model=ChangeProposalResponse)
def approve_change(
    workspace_id: UUID,
    project_id: UUID,
    proposal_id: UUID,
    request: ApproveProposalRequest,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    workspace_service: Annotated[WorkspaceService, Depends(get_workspace_service)],
    github_service: Annotated[GitHubService, Depends(get_github_service)],
):
    _workspace(workspace_id, current_user, workspace_service)
    project = _project(project_id, workspace_id, current_user, github_service)
    proposal = github_service.get_proposal(proposal_id, project, current_user.id)
    if proposal is None:
        raise HTTPException(status_code=404, detail="Change proposal not found.")
    github_service.create_pull_request(project, proposal)
    return proposal
