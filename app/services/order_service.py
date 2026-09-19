import logging

from fastapi import HTTPException,status
from sqlalchemy import select
from app.core.constants import STAFF_ROLES,ALLOWED_STATUS
from app.core.deps import check_role
from app.services.cart_service import clear_cart_service
from app.models.cart import CartItemOrm
from app.models.product import ProductOrm
from app.models.order import OrderItemOrm,OrderOrm
from app.tasks.email_tasks import send_order_email

logger = logging.getLogger(__name__)


def restore_stock(order, db):
    items = db.scalars(select(OrderItemOrm).where(OrderItemOrm.order_id == order.id)).all()
    for item in items:
        product = db.get(ProductOrm, item.product_id)
        product.stock += item.quantity

    
def create_order_service(user,db):
    try:
        items=db.scalars(select(CartItemOrm).where(CartItemOrm.user_id==user.id)).all()
        if not items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Cart is empty'
            )

        product_ids = [item.product_id for item in items]
        products = db.scalars(select(ProductOrm).where(ProductOrm.id.in_(product_ids))).all()
        products_by_id = {p.id: p for p in products}
        total=0

        for item in items:
            product = products_by_id.get(item.product_id)
            if not product or not product.is_active:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail='Product has not active'
                ) 
            if item.quantity>product.stock:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail='Not enough stock'
                )
            
            total+=(product.price*item.quantity)
            
        order=OrderOrm(
            user_id=user.id,
            status='pending',
            total_price=total
        )

        db.add(order)
        db.flush()

        for item in items:
            product=products_by_id[item.product_id]

            order_item=OrderItemOrm(
                order_id=order.id,
                product_id=item.product_id,
                price=product.price,
                quantity=item.quantity
            )

            db.add(order_item)
            product.stock-=item.quantity
        clear_cart_service(user,db)

    except Exception:
        db.rollback()
        raise 
    logger.info('order create order_id=%s,user_id=%s,total=%s',order.id,order.user_id,order.total_price)
    db.commit()
    db.refresh(order)
    send_order_email.delay(order.id)
    logger.info('letter has been placed in the queue. user_id=%s',order.user_id)
    return order
    

def get_orders_service(user,db):
    if user.role in STAFF_ROLES:
        orders=db.scalars(select(OrderOrm)).all()

    else:
        orders=db.scalars(select(OrderOrm).where(OrderOrm.user_id==user.id)).all()

    return orders


def get_order_id_service(order_id,user,db):
    order=db.get(OrderOrm,order_id)
    if not order or order.user_id!=user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Order not found'
        )
    return order


def update_status_service(order_id,new_status,user,db):
    order=get_order_id_service(order_id,user,db)

    if new_status not in ALLOWED_STATUS.get(order.status, set()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid status transition"
        )
    if new_status == "cancelled" and order.status in {"pending", "assembled"}:
        restore_stock(order, db)

    order.status=new_status

    db.commit()
    db.refresh(order)
    return {'msg':'Ok'}


def cancel_order_service(order_id,user,db):
    order=get_order_id_service(order_id,user,db)

    if order.user_id!=user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Forbidden'
        )
    if order.status!='pending':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Can cancel only pending order'
        )
    
    restore_stock(order,db)
    order.status='cancelled'

    db.commit()
    db.refresh(order)
    return {'msg':'Ok'}