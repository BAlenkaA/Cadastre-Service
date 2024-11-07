from fastapi import FastAPI
from sqladmin import Admin

from app.admin.admin_view import UserAdmin
from app.api.routers import main_router
from app.core.config import settings

app = FastAPI(title=settings.title)

admin = Admin(app)

admin.add_view(UserAdmin)

app.include_router(main_router)
