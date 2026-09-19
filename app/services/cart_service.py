from fastapi import HTTPException,status
from sqlalchemy import select
from app.models.cart import CartItemOrm
from app.models.category import CategoryOrm
from app.models.product import ProductOrm


def get_cart_service(user,db):
    return db.scalars(select(CartItemOrm).where(CartItemOrm.user_id==user.id)).all()


def add_item_to_cart_service(user,db,data):
    product=db.get(ProductOrm,data.product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Product with this id has not found'
        )

    cart_item=db.scalar(select(CartItemOrm).where(CartItemOrm.user_id==user.id,CartItemOrm.product_id==data.product_id))

    if cart_item:  
        if cart_item.quantity+data.quantity>product.stock:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Not enough stock'
            )
        
        cart_item.quantity+=data.quantity

    else:
        if data.quantity>product.stock:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Not enough stock'
            )
        cart_item=CartItemOrm(
            user_id=user.id,
            product_id=data.product_id,
            quantity=data.quantity
        )
        db.add(cart_item)

    db.commit()
    db.refresh(cart_item)
    return cart_item


def update_item_service(item_id,user,db,data):
    item=db.get(CartItemOrm, item_id)
    if not item or item.user_id!=user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Cart item not found"
        )

    product=db.get(ProductOrm, item.product_id)
    if not product or not product.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
            )

    if data.quantity > product.stock:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Not enough stock'
        )

    item.quantity=data.quantity

    db.commit()
    db.refresh(item)
    return item


def delete_item_service(item_id,user,db):
    item=db.get(CartItemOrm,item_id)
    if not item or item.user_id!=user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Cart item not found"
        )
    
    db.delete(item)
    db.commit()
    return({'msg':'The product has been deleted'})


def clear_cart_service(user,db):
    items=db.scalars(select(CartItemOrm).where(CartItemOrm.user_id==user.id)).all()
    for item in items:
        db.delete(item)
    return {'msg':'The cart has been cleared'}


def get_active_categories_service(db):
    categories = db.scalars(select(CategoryOrm).where(CategoryOrm.is_active==True)).all()
    if not categories:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Categories not found'
        )
    return categories