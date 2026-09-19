from sqlalchemy import ForeignKey,DateTime,Numeric,func
from sqlalchemy.orm import Mapped,mapped_column
from datetime import datetime,timezone
from decimal import Decimal
from app.core.database import Base


class OrderOrm(Base):
    __tablename__='orders'
    id:Mapped[int]=mapped_column(primary_key=True)
    user_id:Mapped[int]=mapped_column(ForeignKey('users.id'))
    status:Mapped[str]
    total_price:Mapped[int]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),server_default=func.now())

class OrderItemOrm(Base):
    __tablename__='order_items'
    id:Mapped[int]=mapped_column(primary_key=True)
    order_id:Mapped[int]=mapped_column(ForeignKey('orders.id'))
    product_id:Mapped[int]=mapped_column(ForeignKey('products.id'))
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    quantity:Mapped[int]