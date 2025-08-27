import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from tortoise.contrib.fastapi import register_tortoise

from app.api.routers.account import router as account_router
from app.api.routers.auth import router as auth_router
from app.api.routers.channel import router as channel_router
from app.api.routers.media import router as media_router
from app.api.routers.schedule import router as schedule_router
from app.api.routers.task import router as task_router
from app.api.routers.admin import router as admin_router
from app.api.routers.user import router as user_router
from app.core.lifespan import lifespan
from app.core.logging_config import setup_logging
from app.db.tortoise_config import TORTOISE_ORM
from app.exceptions import NotFoundRecordError, AlreadyExistError
from app.core.config import settings

setup_logging()

app = FastAPI(
    lifespan=lifespan,
    title='Tennel',
    version='0.0.1',
    debug=settings.DEBUG,
)

app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'], allow_headers=['*'])


@app.exception_handler(NotFoundRecordError)
async def not_found_exception_handler(request: Request, exc: NotFoundRecordError):
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={'detail': str(exc)})


@app.exception_handler(AlreadyExistError)
async def existing_exception_handler(request: Request, exc: AlreadyExistError):
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={'detail': str(exc)})


app.include_router(admin_router)
app.include_router(user_router)
app.include_router(auth_router)
app.include_router(account_router)
app.include_router(channel_router)
app.include_router(task_router)
app.include_router(media_router)
app.include_router(schedule_router)

register_tortoise(
    app,
    config=TORTOISE_ORM,
    add_exception_handlers=True,
)

# if __name__ == '__main__':
#     uvicorn.run('app.main:app', host='127.0.0.1', port=8000, reload=True)
