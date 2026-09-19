from fastapi import APIRouter,Depends
from app.core.database import DbSession
from app.core.deps import CurrentUser,check_admin
from app.services.admin_service import (add_category_service,get_all_categories_service,add_product_service,get_all_products_service, update_category_service,
    delete_category_service,update_product_service,get_all_users_service,change_role_service,is_active_user_service, delete_product_service)
from app.models.user import UserOrm
from app.schemas.user import UserOutSchema
from app.schemas.product import ProductOutSchema,ProductInSchema,ProductUpdateSchema
from app.schemas.category import CategoryInSchema,CategoryOutSchema,CategoryUpdateSchema


router=APIRouter(dependencies=[Depends(check_admin)])


@router.get('/users',response_model=list[UserOutSchema])
def get_all_users(db:DbSession):
    return get_all_users_service(db)

@router.patch('/users/{user_id}/role')
def change_role(user_id:int,new_role:str,db:DbSession,admin:CurrentUser):
    return change_role_service(user_id,new_role,db,admin)

@router.patch('/users/{user_id}/is_active')
def is_active_user(user_id:int,is_active:bool,db:DbSession,admin:CurrentUser):
    return is_active_user_service(user_id,is_active,db,admin)

@router.get('/products',response_model=list[ProductOutSchema])
def get_all_products(db:DbSession):
    return get_all_products_service(db)

@router.post('/products',response_model=ProductOutSchema)
def add_product(product:ProductInSchema,db:DbSession):
    return add_product_service(product,db)

@router.patch('/products/{product_id}')
def update_product(product_id:int,data:ProductUpdateSchema,db:DbSession):
    return update_product_service(product_id,data,db)

@router.delete('/products/{product_id}')
def delete_product(product_id:int,db:DbSession):
    return delete_product_service(product_id,db)

@router.get('/categories',response_model=list[CategoryOutSchema])
def get_all_categories(db:DbSession):
    return get_all_categories_service(db)

@router.post('/categories',response_model=CategoryOutSchema)
def add_category(category:CategoryInSchema,db:DbSession):
    return add_category_service(category,db)

@router.patch('/categories/{category_id}',response_model=CategoryOutSchema)
def update_category(category_id:int,data:CategoryUpdateSchema,db:DbSession):
    return update_category_service(category_id,data,db)

@router.delete('/categories/{category_id}')
def delete_category(category_id:int,db:DbSession):
    return delete_category_service(category_id,db)