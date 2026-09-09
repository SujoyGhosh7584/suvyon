from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.ai.providers.base import ModelInfo
from app.ai.registry import allowed_models
from app.core.config import settings
from app.services import auth_service as auth_module
from app.services.auth_service import AuthService
from app.services.github_service import GitHubService
from app.services.oauth_service import OAuthService
from app.services.user_service import UserService


def test_oauth_exchange_ticket_is_short_lived_and_single_use():
    service = OAuthService()
    user_id = uuid4()
    ticket = service.create_exchange_ticket(user_id)

    assert service.consume_exchange_ticket(ticket) == user_id
    with pytest.raises(ValueError, match="invalid or expired"):
        service.consume_exchange_ticket(ticket)


def test_free_mode_filters_models_with_a_declared_price(monkeypatch):
    monkeypatch.setattr(settings, "ZERO_COST_MODE", True)
    provider = SimpleNamespace(
        list_models=lambda: [
            ModelInfo("test", "free", "Free", 1000),
            ModelInfo("test", "paid", "Paid", 1000, cost_per_1k_input=0.01),
        ]
    )

    assert [model.model_id for model in allowed_models(provider)] == ["free"]


def test_oauth_login_creates_verified_user_without_storing_provider_token(monkeypatch):
    class UserRepository:
        def __init__(self):
            self.user = None

        def get_by_email(self, email):
            return self.user

        def get_by_id(self, user_id):
            return self.user if self.user and self.user.id == user_id else None

        def create(self, user):
            user.id = uuid4()
            self.user = user

        def commit(self):
            pass

        def refresh(self, user):
            pass

        def rollback(self):
            pass

    class OAuthRepository:
        def __init__(self):
            self.account = None

        def get_by_identity(self, provider, provider_user_id):
            return self.account

        def get_by_user_provider(self, user_id, provider):
            return self.account

        def create(self, account):
            self.account = account

    users, oauth = UserRepository(), OAuthRepository()
    monkeypatch.setattr(auth_module, "hash_password", lambda value: "unusable-social-password")
    service = AuthService(users, SimpleNamespace(), oauth)
    user = service.oauth_login(provider="github", profile={
        "provider_user_id": "123",
        "email": "DEV@example.com",
        "full_name": "Dev",
        "avatar_url": "https://example.com/avatar.png",
    })

    assert user.email == "dev@example.com"
    assert user.is_verified is True
    assert oauth.account.provider_user_id == "123"
    assert not hasattr(oauth.account, "access_token")


@pytest.mark.parametrize(
    ("path", "expected"),
    [
        ("src/app.py", True),
        ("README.md", True),
        ("node_modules/pkg/index.js", False),
        ("dist/app.js", False),
        ("assets/logo.png", False),
    ],
)
def test_repository_context_only_accepts_small_source_files(path, expected):
    assert GitHubService._allowed_path(path, 1000) is expected
    assert GitHubService._allowed_path(path, 200_000) is False


@pytest.mark.parametrize(
    "path",
    [".env", "secrets/private.key", ".github/workflows/deploy.yml", "package-lock.json", "../escape.py"],
)
def test_repository_changes_reject_sensitive_or_unsafe_paths(path):
    assert GitHubService._allowed_change_path(path, 100) is False


def test_account_deletion_removes_user_in_one_committed_transaction():
    class Session:
        def __init__(self):
            self.executed = []

        def execute(self, statement):
            self.executed.append(statement)

    class Repository:
        def __init__(self):
            self.session = Session()
            self.deleted = None
            self.committed = False

        def delete(self, user):
            self.deleted = user

        def commit(self):
            self.committed = True

        def rollback(self):
            raise AssertionError("delete should not roll back")

    repository = Repository()
    user = SimpleNamespace(email="user@example.com", workspaces=[])

    UserService(repository).delete_account(user=user)

    assert repository.deleted is user
    assert repository.committed is True
    assert len(repository.session.executed) == 1
