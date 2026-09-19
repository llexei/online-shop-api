from fastapi import APIRouter,dependencies,Depends
from app.core.database import DbSession
from app.core.limiting import rate_limit
from app.services.products_service import get_active_products_service,get_product_for_id_service
from app.schemas.product import ProductOutSchema


router=APIRouter(dependencies=[Depends(rate_limit(60,60))])


@router.get('/',response_model=list[ProductOutSchema])
def get_active_products(db:DbSession):
    return get_active_products_service(db)

@router.get('/{product_id}',response_model=ProductOutSchema)
def get_product_for_id(product_id:int,db:DbSession):
    return get_product_for_id_service(product_id,db)