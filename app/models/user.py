from typing import List

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy.orm import Mapped, relationship

from app.core.database import Base


class User(SQLAlchemyBaseUserTable[int], Base):
    """
    Базовая модель пользователя для системы с использованием FastAPI-Users.
    Эта модель расширяет стандартную модель пользователя из библиотеки
     `fastapi-users`, добавляя информацию о запросах пользователя и
      статусах пользователя.

    Атрибуты:
        id (int): Уникальный идентификатор пользователя (основной ключ).
        email (str): Адрес электронной почты пользователя.
         Должен быть уникальным.
        password (str): Захешированный пароль пользователя.
        is_active (bool): Флаг, показывающий, активен ли пользователь.
         По умолчанию `True`.
        is_verified (bool): Флаг, показывающий, подтверждён ли пользователь.
         По умолчанию `False`.
        is_superuser (bool): Флаг, показывающий, имеет ли пользователь
         права суперпользователя. По умолчанию `False`.

    Связи:
        query_history (List[QueryHistory]): История запросов пользователя.
         Связь один ко многим с моделью `QueryHistory`.
        Каждый пользователь может иметь несколько записей в истории
         запросов. Эта связь реализована через атрибут `user_id`
         в модели `QueryHistory`.
        Каскадное удаление (`cascade='all, delete-orphan'`) гарантирует, что:
         - Все записи истории запросов пользователя будут удалены
          при удалении пользователя.
         - При удалении конкретной записи в истории запросов (например,
          в случае отсоединения от пользователя),
           она будет удалена из базы данных.

    Примечания:
        - Модель использует базовый класс `SQLAlchemyBaseUserTable`,
          который уже включает в себя стандартные поля для пользователей,
          такие как `id`, `email`, `password`, а также флаги для активации,
          проверки и суперпользовательских прав.
        - Атрибут `query_history` позволяет получить все запросы,
          связанные с данным пользователем.

    """
    query_history: Mapped[List['QueryHistory']] = relationship(
        'QueryHistory', back_populates="user", cascade='all, delete-orphan')
