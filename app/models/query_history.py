from decimal import Decimal
from typing import Optional

from sqlalchemy import (DECIMAL, Boolean, CheckConstraint, ForeignKey,
                        ForeignKeyConstraint, String)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class QueryHistory(Base):
    """
    Модель для хранения истории запросов с информацией
     о кадастровом номере и координатах.

    Атрибуты:
        cadastral_number (str): Кадастровый номер, максимальная длина —
         25 символов.
        latitude (Optional[Decimal]): Широта объекта. Значение должно быть
         в пределах от -90 до 90.
        longitude (Optional[Decimal]): Долгота объекта. Значение должно быть
         в пределах от -180 до 180.
        result (bool): Результат запроса, по умолчанию `False`.
        user_id (int): Идентификатор пользователя, которому принадлежит
         данный запрос. Это поле является внешним ключом, ссылающимся на
         таблицу `user`.

    Связи:
        user (User): Объект пользователя, который сделал запрос.
         Связь с моделью `User`.

    Ограничения:
        - `cadastral_number`: ограничение длины поля до 25 символов.
        - `latitude`: проверка на диапазон значений от -90 до 90 градусов
         (широта).
        - `longitude`: проверка на диапазон значений от -180 до 180 градусов
         (долгота).
        - `user_id`: внешний ключ, ссылающийся на таблицу `user`.
         При удалении пользователя записи с его `user_id` будут также удалены.
    """
    cadastral_number: Mapped[str] = mapped_column(String(25), index=True)
    latitude: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(8, 6))
    longitude: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(9, 6))
    result: Mapped[bool] = mapped_column(Boolean, default=False)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))

    user = relationship('User', back_populates='query_history')

    __table_args__ = (
        ForeignKeyConstraint(
            ['user_id'], ['user.id'], ondelete='CASCADE'
        ),
        CheckConstraint(
            '-90 <= latitude AND latitude <= 90', name='latitude_range'),
        CheckConstraint(
            '-180 <= longitude AND longitude <= 180', name='longitude_range'),
    )
