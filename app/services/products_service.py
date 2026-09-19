from fastapi import HTTPException,status
from sqlalchemy import select
from app.models.product import ProductOrm


def get_active_products_service(db):
    return db.scalars(select(ProductOrm).where(ProductOrm.is_active==True)).all()


def get_product_for_id_service(product_id,db):
    ex_product = db.scalar(select(ProductOrm).where(ProductOrm.id==product_id,ProductOrm.is_active==True))
    if not ex_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Product not found'
        )
    return ex_product