import uvicorn
from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise

from app.api.routers.auth import router as auth_router
from app.api.routers.users import router as user_router
from app.core.lifespan import lifespan
from app.core.logging_config import setup_logging
from app.db.tortoise_config import TORTOISE_ORM

setup_logging()

app = FastAPI(
    lifespan=lifespan,
    title='Tennel',
    version='0.0.1'
)

app.include_router(user_router)
app.include_router(auth_router)

register_tortoise(
    app,
    config=TORTOISE_ORM,
    add_exception_handlers=True,
)

if __name__ == '__main__':
    uvicorn.run('app.main:app', host='127.0.0.1', port=8000, reload=True)
