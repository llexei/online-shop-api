from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.redis import get_redis
from app.core.logging import setup_logging
from app.api import auth,cart,categories,products,orders,admin

setup_logging()
app=FastAPI()
redis=next(get_redis())


app.add_middleware(
    CORSMiddleware,
    allow_origins=[],
    allow_credentials=True,
    allow_methods=['*']
)


app.include_router(auth.router,prefix='/api/auth',tags=['auth'])
app.include_router(cart.router,prefix='/api/cart',tags=['cart'])
app.include_router(categories.router,prefix='/api/categories',tags=['categories'])
app.include_router(products.router,prefix='/api/products',tags=['products'])
app.include_router(orders.router,prefix='/api/orders',tags=['orders'])
app.include_router(admin.router,prefix='/api/admin',tags=['admin'])


if __name__ == '__main__':
    import uvicorn
    uvicorn.run('main:app',reload=True)
