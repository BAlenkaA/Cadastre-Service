import re
from decimal import Decimal

from pydantic import BaseModel, Field, ConfigDict, field_validator


class QueryCreate(BaseModel):
    cadastral_number: str = Field(
        ...,
        min_length=15,
        max_length=25,
        description='Введите кадастровый номер в формате XX:XX:XXXXXX:X, где X - цифра.',
        example='12:34:567890:10'
    )

    @field_validator('cadastral_number')
    def check_format_compliance(cls, value):
        if not re.match(r'\d{2}:\d{2}:\d{6,7}:\d{1,}', value):
            raise ValueError('Кадастровый номер не соответствует формату')
        return value


class QueryDB(QueryCreate):
    id: int
    latitude: Decimal = Field(..., max_digits=8, decimal_places=6)
    longitude: Decimal = Field(..., max_digits=9, decimal_places=6)
    result: bool

    model_config = ConfigDict(
        from_attributes=True
    )
