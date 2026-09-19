from sqlalchemy import Numeric,ForeignKey,DateTime,func
from sqlalchemy.orm import Mapped,mapped_column
from datetime import datetime,timezone
from decimal import Decimal
from app.core.database import Base


class ProductOrm(Base):
    __tablename__='products'
    id:Mapped[int]=mapped_column(primary_key=True)
    name:Mapped[str]
    description:Mapped[str|None]=mapped_column(nullable=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    stock:Mapped[int]=mapped_column(default=0)
    category_id=mapped_column(ForeignKey('categories.id'))
    is_active:Mapped[bool]=mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),server_default=func.now())
