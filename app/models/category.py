from sqlalchemy.orm import Mapped,mapped_column
from app.core.database import Base


class CategoryOrm(Base):
    __tablename__='categories'
    id:Mapped[int]=mapped_column(primary_key=True)
    name:Mapped[str]=mapped_column(unique=True)
    slug:Mapped[str]=mapped_column(unique=True)
    is_active:Mapped[bool]