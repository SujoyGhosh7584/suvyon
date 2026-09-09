from pathlib import Path
import shutil

from sqlalchemy import delete
from sqlalchemy.exc import SQLAlchemyError

from app.models.user import User
from app.models.otp_code import OtpCode
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserUpdateProfile


class UserService:
    def __init__(self, user_repository: UserRepository) -> None:
        self._user_repository = user_repository

    def update_profile(self, *, user: User, data: UserUpdateProfile) -> User:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(user, field, value)

        try:
            self._user_repository.commit()
            return user
        except SQLAlchemyError:
            self._user_repository.rollback()
            raise

    def delete_account(self, *, user: User) -> None:
        workspace_ids = [workspace.id for workspace in user.workspaces]
        try:
            self._user_repository.session.execute(
                delete(OtpCode).where(OtpCode.email == user.email)
            )
            self._user_repository.delete(user)
            self._user_repository.commit()
        except SQLAlchemyError:
            self._user_repository.rollback()
            raise

        upload_root = Path("uploads").resolve()
        for workspace_id in workspace_ids:
            workspace_uploads = (upload_root / str(workspace_id)).resolve()
            if workspace_uploads.parent == upload_root and workspace_uploads.exists():
                shutil.rmtree(workspace_uploads, ignore_errors=True)
