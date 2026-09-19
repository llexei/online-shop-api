from fastapi import APIRouter,HTTPException,status
from sqlalchemy import select
from app.core.database import DbSession
from app.services.cart_service import get_active_categories_service
from app.models.category import CategoryOrm
from app.schemas.category import CategoryOutSchema


router=APIRouter()


@router.get('/',response_model=list[CategoryOutSchema])
def get_active_categories(db:DbSession):
    return get_active_categories_service(db)
