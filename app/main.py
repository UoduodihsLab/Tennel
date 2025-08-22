import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from tortoise.contrib.fastapi import register_tortoise

from app.api.routers.accounts import router as accounts_router
from app.api.routers.auth import router as auth_router
from app.api.routers.channels import router as channels_router
from app.api.routers.medias import router as medias_router
from app.api.routers.schedules import router as schedules_router
from app.api.routers.tasks import router as tasks_router
from app.api.routers.users import router as users_router
from app.core.lifespan import lifespan
from app.core.logging_config import setup_logging
from app.db.tortoise_config import TORTOISE_ORM
from app.exceptions import NotFoundRecordError, AlreadyExistError

setup_logging()

app = FastAPI(
    lifespan=lifespan,
    title='Tennel',
    version='0.0.1',
    debug=True,
)


@app.exception_handler(NotFoundRecordError)
async def not_found_exception_handler(request: Request, exc: NotFoundRecordError):
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={'detail': str(exc)})


@app.exception_handler(AlreadyExistError)
async def existing_exception_handler(request: Request, exc: AlreadyExistError):
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={'detail': str(exc)})


app.include_router(users_router)
app.include_router(auth_router)
app.include_router(accounts_router)
app.include_router(channels_router)
app.include_router(tasks_router)
app.include_router(medias_router)
app.include_router(schedules_router)

register_tortoise(
    app,
    config=TORTOISE_ORM,
    add_exception_handlers=True,
)

if __name__ == '__main__':
    uvicorn.run('app.main:app', host='127.0.0.1', port=8000, reload=True)
