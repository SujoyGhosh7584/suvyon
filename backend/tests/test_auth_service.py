from types import SimpleNamespace

import pytest

from app.exceptions.auth import InactiveUserError
from app.services import auth_service as auth_module
from app.services.auth_service import AuthService


def test_login_normalizes_email_and_rejects_inactive_user(monkeypatch):
    observed = {}
    user = SimpleNamespace(hashed_password="hash", is_active=False)

    class Repository:
        def get_by_email(self, email):
            observed["email"] = email
            return user

    monkeypatch.setattr(auth_module, "verify_password", lambda password, hashed: True)
    service = AuthService(Repository(), SimpleNamespace())

    with pytest.raises(InactiveUserError):
        service.login(email="  USER@Example.COM ", password="password")

    assert observed["email"] == "user@example.com"
