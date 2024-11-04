from fastapi import FastAPI

from app.config import settings

from .api import router

app = FastAPI(title=settings.title)

app.include_router(router)
