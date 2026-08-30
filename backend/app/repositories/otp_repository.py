from datetime import datetime

from sqlalchemy import func, select, update

from app.models.otp_code import OtpCode
from app.repositories.base_repository import BaseRepository


class OtpRepository(BaseRepository[OtpCode]):
    model = OtpCode

    def get_latest(self, email: str, purpose: str) -> OtpCode | None:
        statement = (
            select(OtpCode)
            .where(
                func.lower(OtpCode.email) == email.lower(),
                OtpCode.purpose == purpose,
            )
            .order_by(OtpCode.created_at.desc())
        )
        return self.session.execute(statement).scalars().first()

    def get_latest_active(self, email: str, purpose: str) -> OtpCode | None:
        statement = (
            select(OtpCode)
            .where(
                func.lower(OtpCode.email) == email.lower(),
                OtpCode.purpose == purpose,
                OtpCode.consumed_at.is_(None),
            )
            .order_by(OtpCode.created_at.desc())
        )
        return self.session.execute(statement).scalars().first()

    def consume_active(self, email: str, purpose: str, consumed_at: datetime) -> None:
        statement = (
            update(OtpCode)
            .where(
                func.lower(OtpCode.email) == email.lower(),
                OtpCode.purpose == purpose,
                OtpCode.consumed_at.is_(None),
            )
            .values(consumed_at=consumed_at, updated_at=consumed_at)
        )
        self.session.execute(statement)
