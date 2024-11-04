import asyncio

import pytest
from fastapi import status
from httpx import AsyncClient
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import QueryBase, QueryCreate


def test_invalid_cadastral_number_format():
    """
    Тесты валидации cadastral_number.
    """
    query = QueryBase(cadastral_number="12:34:567890:10")
    assert query.cadastral_number == "12:34:567890:10"

    with pytest.raises(ValidationError) as exc_info:
        QueryBase(cadastral_number="short")
    assert "String should have at least 15 characters" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        QueryBase(cadastral_number="invalid_format_")
    assert "Value error, Кадастровый номер не соответствует формату" in str(exc_info.value)


def test_latitude_validation():
    """
    Тесты валидации поля latitude.
    """
    query = QueryCreate(cadastral_number="12:34:567890:10", latitude=-70.0)
    assert query.latitude == -70.0
    assert query.longitude is None

    with pytest.raises(ValidationError) as exc_info:
        QueryCreate(cadastral_number="12:34:567890:10", latitude=90.0)
    assert "Широта должна быть в диапазоне от -90 до 90." in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        QueryCreate(cadastral_number="12:34:567890:10", latitude=100.0)
    errors = exc_info.value.errors()
    assert any(err['loc'] == ('latitude',) and err['type'] == 'decimal_whole_digits' for err in errors)


def test_longitude_validation():
    """
    Тесты валидации поля longitude.
    """
    query = QueryCreate(cadastral_number="12:34:567890:10", longitude=-73.0)
    assert query.latitude is None
    assert query.longitude == -73.0

    with pytest.raises(ValidationError) as exc_info:
        QueryCreate(cadastral_number="12:34:567890:10", longitude=200.0)
    assert "Долгота должна быть в диапазоне от -180 до 180." in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        QueryCreate(cadastral_number="12:34:567890:10", longitude=-1100.0)
    errors = exc_info.value.errors()
    assert any(err['loc'] == ('longitude',) and err['type'] == 'decimal_whole_digits' for err in errors)


@pytest.mark.asyncio(loop_scope="session")
async def test_create_new_query(async_client: AsyncClient, session: AsyncSession):
    """
    Тест на создание нового запроса.
    """
    query_data = {
        "cadastral_number": "12:34:567890:1011"
    }
    response = await async_client.post("/query", json=query_data)

    assert response.status_code == 200
    data = response.json()
    assert "cadastral_number" in data
    assert data["cadastral_number"] == "12:34:567890:1011"


@pytest.mark.asyncio(loop_scope="session")
async def test_server_startup_check(async_client: AsyncClient, session: AsyncSession):
    response = await async_client.get("/ping")

    assert response.status_code == 200

    data = response.json()
    assert data == {'message': 'Server is running'}


@pytest.mark.asyncio(loop_scope="session")
async def test_get_query_history(async_client: AsyncClient, session: AsyncSession):
    """
    Тесты на получение истории запросов.
    """
    response = await async_client.get("/history")

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)


@pytest.mark.asyncio(loop_scope="session")
async def test_get_query_history_with_cadastral_number(async_client: AsyncClient, session):
    """
    Тест для получения истории запросов с фильтрацией по кадастровому номеру.
    Проверяет, что возвращается корректный статус и данные.
    """
    cadastral_number = "12:34:567890:10"

    response = await async_client.get("/history", params={"cadastral_number": cadastral_number})

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert all(record['cadastral_number'] == cadastral_number for record in data)


@pytest.mark.asyncio(loop_scope="session")
async def test_get_query_history_invalid_cadastral_number(async_client: AsyncClient, session: AsyncSession):
    """
    Тест для проверки обработки некорректного кадастрового номера.
    Проверяет, что возвращается статус 400 и соответствующее сообщение об ошибке.
    """
    response = await async_client.get("/history", params={"cadastral_number": "invalid_format"})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Кадастровый номер не соответствует формату" in response.json()["detail"]


@pytest.mark.asyncio(loop_scope="session")
async def test_get_query_history_no_records(async_client: AsyncClient, session):
    """
    Тест для проверки обработки случая, когда записи не найдены.
    Проверяет, что возвращается статус 404 и сообщение "Записи не найдены".
    """
    cadastral_number = "00:00:000000:00"  # Предполагается, что в базе нет записей с таким номером
    response = await async_client.get("/history", params={"cadastral_number": cadastral_number})

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Записи не найдены"


@pytest.mark.asyncio(loop_scope="session")
async def test_get_query_history_pagination(async_client: AsyncClient, session):
    """
    Тест для проверки пагинации.
    Проверяет, что при запросе с параметрами page и size возвращается корректное количество записей.
    """

    response = await async_client.get("/history", params={"page": 1, "size": 5})

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) <= 5