from fastapi import APIRouter,dependencies,Depends
from app.core.deps import CurrentUser,CheckStaff
from app.core.database import DbSession
from app.core.limiting import rate_limit
from app.services.order_service import create_order_service,get_orders_service,update_status_service,cancel_order_service,get_order_id_service
from app.schemas.order import OrderOutSchema,UpdateStatusSchema


router=APIRouter(dependencies=[Depends(rate_limit(30,60))])


@router.post('/',response_model=OrderOutSchema)
def create_order(user:CurrentUser,db:DbSession):
    return create_order_service(user,db)

@router.get('/',response_model=list[OrderOutSchema])
def get_orders(user:CurrentUser,db:DbSession):
    return get_orders_service(user,db)

@router.get('/{order_id}',response_model=OrderOutSchema)
def get_order_id(order_id:int,user:CurrentUser,db:DbSession):
    return get_order_id_service(order_id,user,db)

@router.patch('/{order_id}/status')
def update_status(order_id:int,data:UpdateStatusSchema,user:CheckStaff,db:DbSession):
    return update_status_service(order_id,data.status,user,db)

@router.post('/{order_id}/cancelled')
def cancel_order(order_id:int,user:CurrentUser,db:DbSession):
    return cancel_order_service(order_id,user,db)