from fastapi import APIRouter,dependencies,Depends
from app.core.deps import CurrentUser
from app.core.database import DbSession
from app.core.limiting import rate_limit
from app.services.cart_service import get_cart_service,add_item_to_cart_service,update_item_service,delete_item_service,clear_cart_service
from app.models.cart import CartItemOrm
from app.schemas.cart import CartItemOutSchema,CartItemInSchema,CartItemUpdateSchema


router=APIRouter()


@router.get('/',response_model=list[CartItemOutSchema],dependencies=[Depends(rate_limit(5,60))])
def get_cart(user:CurrentUser,db:DbSession):
    return get_cart_service(user,db)

@router.post('/items',response_model=CartItemOutSchema)
def add_item_to_cart(user:CurrentUser,db:DbSession,data:CartItemInSchema):
    return add_item_to_cart_service(user,db,data)

@router.patch('/items/{item_id}',response_model=CartItemOutSchema)
def update_item(item_id:int,user:CurrentUser,db:DbSession,data:CartItemUpdateSchema):
    return update_item_service(item_id,user,db,data)

@router.delete('/items/{item_id}')
def delete_item(item_id:int,user:CurrentUser,db:DbSession):
    return delete_item_service(item_id,user,db)

@router.delete('/',dependencies=[Depends(rate_limit(10,60))])
def clear_cart(user:CurrentUser,db:DbSession):
    result= clear_cart_service(user,db)
    db.commit()
    return result