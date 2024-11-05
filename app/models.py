from decimal import Decimal
from typing import Optional

from sqlalchemy import DECIMAL, Boolean, CheckConstraint, String
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class QueryHistory(Base):
    """
    Модель для хранения истории запросов с информацией о кадастровом номере и координатах.

    Атрибуты:
        cadastral_number (str): Кадастровый номер, максимальная длина — 25 символов.
        latitude (Optional[Decimal]): Широта объекта. Значение должно быть в пределах от -90 до 90.
        longitude (Optional[Decimal]): Долгота объекта. Значение должно быть в пределах от -180 до 180.
        result (bool): Результат запроса, по умолчанию `False`.
    """
    cadastral_number: Mapped[str] = mapped_column(String(25), index=True)
    latitude: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(8, 6))
    longitude: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(9, 6))
    result: Mapped[bool] = mapped_column(Boolean, default=False)

    __table_args__ = (
        CheckConstraint('-90 <= latitude AND latitude <= 90', name='latitude_range'),
        CheckConstraint('-180 <= longitude AND longitude <= 180', name='longitude_range'),
    )
