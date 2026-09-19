from sqlalchemy import DateTime,func
from sqlalchemy.orm import mapped_column,Mapped
from datetime import datetime, timezone
from app.core.database import Base


class UserOrm(Base):
    __tablename__='users'
    id:Mapped[int]=mapped_column(primary_key=True)
    username:Mapped[str]=mapped_column(unique=True)
    email:Mapped[str]=mapped_column(unique=True)
    hashed_password:Mapped[str]=mapped_column(nullable=False)
    role:Mapped[str]=mapped_column(default='user')
    is_active:Mapped[bool]=mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),server_default=func.now())
