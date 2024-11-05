from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.validators import validate_cadastral_number


class QueryBase(BaseModel):
    """
    Базовая модель для запроса с кадастровым номером.

    Атрибуты:
        cadastral_number (str): Кадастровый номер, должен быть длиной
         от 15 до 25 символов и соответствовать формату 'XX:XX:XXXXXX:X'.
    """
    cadastral_number: str = Field(
        ...,
        min_length=15,
        max_length=25,
        description='Введите кадастровый номер в формате XX:XX:XXXXXX:X, где X - цифра.'
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"cadastral_number": "12:34:567890:10"}
            ]
        }
    )

    @field_validator('cadastral_number')
    def check_format_compliance(cls, value):
        """
        Валидатор для проверки соответствия кадастрового номера формату 'XX:XX:XXXXXX:X'.

        Аргументы:
            value (str): Кадастровый номер для проверки.

        Возвращает:
            str: Кадастровый номер, если он соответствует формату.

        Исключения:
            ValueError: Если кадастровый номер не соответствует формату.
        """
        return validate_cadastral_number(value)


class QueryCreate(QueryBase):
    """
    Модель для создания нового запроса с координатами.

    Атрибуты:
        latitude (Optional[Decimal]): Широта в диапазоне от -90 до 90 градусов.
        longitude (Optional[Decimal]): Долгота в диапазоне от -180 до 180 градусов.
    """
    latitude: Optional[Decimal] = Field(
        None,
        max_digits=8,
        decimal_places=6,
        description="Широта должна быть от -90 до 90 градусов."
    )
    longitude: Optional[Decimal] = Field(
        None,
        max_digits=9,
        decimal_places=6,
        description="Долгота должна быть от -180 до 180 градусов."
    )

    @field_validator('latitude')
    def check_latitude_range(cls, value):
        """
        Валидатор для проверки диапазона широты.

        Аргументы:
            value (Optional[Decimal]): Значение широты для проверки.

        Возвращает:
            Optional[Decimal]: Широта, если она в допустимом диапазоне.

        Исключения:
            ValueError: Если широта выходит за пределы диапазона -90 до 90.
        """
        if value is not None and (value <= -90 or value >= 90):
            raise ValueError('Широта должна быть в диапазоне от -90 до 90.')
        return value

    @field_validator('longitude')
    def check_longitude_range(cls, value):
        """
        Валидатор для проверки диапазона долготы.

        Аргументы:
            value (Optional[Decimal]): Значение долготы для проверки.

        Возвращает:
            Optional[Decimal]: Долгота, если она в допустимом диапазоне.

        Исключения:
            ValueError: Если долгота выходит за пределы диапазона -180 до 180.
        """
        if value is not None and (value <= -180 or value >= 180):
            raise ValueError('Долгота должна быть в диапазоне от -180 до 180.')
        return value


class QueryResponse(QueryBase):
    """
    Модель ответа на запрос с кадастровым номером.

    Атрибуты:
        result (bool): Результат выполнения запроса.
    """
    result: bool


class QueryHistoryResponse(QueryCreate):
    """
    Модель для истории запросов, включая идентификатор, дату создания и результат.

    Атрибуты:
        id (int): Идентификатор записи истории.
        created_at (datetime): Дата и время создания записи.
        result (bool): Результат выполнения запроса.
    """
    id: int
    created_at: datetime
    result: bool

    model_config = ConfigDict(
        from_attributes=True
    )
