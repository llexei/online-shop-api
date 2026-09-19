from fastapi import HTTPException,status
from sqlalchemy import select
from app.core.constants import ALLOWED_ROLES
from app.models.category import CategoryOrm
from app.models.product import ProductOrm
from app.models.user import UserOrm
from app.schemas.category import CategoryUpdateSchema
from app.schemas.product import ProductUpdateSchema


def exist(par:str,db,payload,id):
    exists=db.scalar(select(CategoryOrm.id).where(getattr(CategoryOrm,par)==payload[par],CategoryOrm.id!=id))
    if exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'{par} already exists'
        )



def get_all_categories_service(db):
    categories = db.scalars(select(CategoryOrm)).all()
    if not categories:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Categories not found'
        )
    return categories


def add_category_service(category,db):
    now_category=db.scalar(select(CategoryOrm).where((CategoryOrm.name==category.name)|(CategoryOrm.slug==category.slug)))
    if now_category:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Category name or slug has already used'
        )
    
    new_category=CategoryOrm(
        name=category.name,
        slug=category.slug,
        is_active=category.is_active
    )

    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category


def update_category_service(category_id,data,db):
    category=db.get(CategoryOrm,category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Category not found'
        )
    
    payload=data.model_dump(exclude_unset=True)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='No fields to update'
        )

    fields=['name','slug']
    for field in fields:
        if field in payload:
            exist(field,db,payload,category_id)

    for f,v in payload.items():
        setattr(category,f,v)
    db.commit()
    db.refresh(category)
    return category


def delete_category_service(category_id,db):
    category=db.get(CategoryOrm,category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Category not found'
        )
    has_products=db.scalars(select(ProductOrm).where(ProductOrm.category_id==category_id)).all()
    if has_products:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Category has products'
        )
    db.delete(category)
    db.commit()
    return {'msg':'Ok'}


def add_product_service(product,db):
    category=db.get(CategoryOrm,product.category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Category not found'
        )
    
    data = product.model_dump(exclude_unset=True)
    new_product = ProductOrm(**data)
    
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product


def update_product_service(product_id,data,db):
    product=db.get(ProductOrm,product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Product not found'
        )
    
    payload=data.model_dump(exclude_unset=True)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='No fields to update'
        )

    for f,v in payload.items():
        setattr(product,f,v)
    db.commit()
    db.refresh(product)
    return product

    
def get_all_products_service(db):
    products= db.scalars(select(ProductOrm)).all()
    if not products:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Products not found'
        )
    return products


def get_all_users_service(db):
    users=db.scalars(select(UserOrm)).all()
    if not users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Users not found'
        )
    return users


def change_role_service(user_id,new_role,db,admin):
    if new_role not in ALLOWED_ROLES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Invalid role'
        )
    
    user=db.get(UserOrm,user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found'
        )
    if user.id==admin.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin can't change self role"
        )

    user.role=new_role

    db.commit()
    db.refresh(user)
    return {'msg':'Ok'}


def is_active_user_service(user_id,is_active,db,admin):
    user=db.get(UserOrm,user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found'
        )
    if user.id==admin.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin can't change self is_active"
        )
    user.is_active=is_active

    db.commit()
    db.refresh(user)
    return {'msg':'Ok'}


def delete_product_service(product_id,db):
    product=db.get(ProductOrm,product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Product not found'
        )
    
    db.delete(product)
    db.commit()
    return {'msg':'Ok'}