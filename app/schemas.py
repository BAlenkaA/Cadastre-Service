from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict, field_validator

from app.validators import validate_cadastral_number


class QueryBase(BaseModel):
    cadastral_number: str = Field(
        ...,
        min_length=15,
        max_length=25,
        description='Введите кадастровый номер в формате XX:XX:XXXXXX:X, где X - цифра.',
        example='12:34:567890:10'
    )

    @field_validator('cadastral_number')
    def check_format_compliance(cls, value):
        return validate_cadastral_number(value)


class QueryCreate(QueryBase):
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
        if value is not None and (value <= -90 or value >= 90):
            raise ValueError('Широта должна быть в диапазоне от -90 до 90.')
        return value


    @field_validator('longitude')
    def check_longitude_range(cls, value):
        if value is not None and (value <= -180 or value >= 180):
            raise ValueError('Долгота должна быть в диапазоне от -180 до 180.')
        return value


class QueryResponse(QueryBase):
    result: bool


class QueryHistoryResponse(QueryCreate):
    id: int
    created_at: datetime
    result: bool

    model_config = ConfigDict(
        from_attributes=True
    )
