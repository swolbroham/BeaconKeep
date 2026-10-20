from app.db.base import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import SmallInteger, BigInteger, String, Text, CheckConstraint, DateTime, func
from datetime import datetime

class Monitor(Base):
    __tablename__ = "monitors"
    id: Mapped[int] = mapped_column(BigInteger, primary_key = True)
    name: Mapped[str | None] = mapped_column(String(64))
    url: Mapped[str] = mapped_column(Text)
    check_interval_seconds: Mapped[int] = mapped_column(default = 60)
    timeout_seconds: Mapped[int] = mapped_column(default = 5)
    expected_status_code: Mapped[int] = mapped_column(SmallInteger, default = 200)
    is_enabled: Mapped[bool] = mapped_column(default = True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


    __table_args__ = (
        CheckConstraint(
            "check_interval_seconds >= 5 AND check_interval_seconds <= 3600",
            name = "ck_monitors_check_interval_range"
            ), 
        CheckConstraint(
            "timeout_seconds >= 1 AND timeout_seconds < check_interval_seconds", 
            name = "ck_monitors_timeout_range"
            ),
        CheckConstraint(
            "200 <= expected_status_code AND expected_status_code <= 599",
            name = "ck_monitors_expected_status_code_range"
            )
        )

    