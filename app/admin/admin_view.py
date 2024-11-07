from fastapi import HTTPException, status, APIRouter, Depends
from sqladmin import ModelView

from app.core.user import fastapi_users, auth_backend
from app.models import User


class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.email, User.is_active, User.is_verified, User.is_superuser]
    name = "Пользователь"
    name_plural = "Пользователи"
    category = "Аккаунты"
    column_searchable_list = [User.is_active]

    def is_accessible(self, user: User = Depends(fastapi_users.current_user())) -> bool:
        """
        Метод, который проверяет, является ли пользователь суперпользователем.
        Если нет, доступ будет закрыт.
        """
        if not user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="У вас нет прав доступа к административной панели"
            )
        return True


router = APIRouter()

router.include_router(fastapi_users.get_auth_router(auth_backend), prefix='/admin', tags=['admin'])