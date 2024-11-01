import re


def validate_cadastral_number(value: str) -> str:
    if not re.match(r'\d{2}:\d{2}:\d{6,7}:\d{1,}', value):
        raise ValueError('Кадастровый номер не соответствует формату')
    return value
