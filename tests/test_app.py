import pytest
from fastapi import status
from httpx import AsyncClient
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.query_history import QueryBase, QueryCreate


def test_invalid_cadastral_number_format():
    """
    Тесты на валидацию кадастрового номера (cadastral_number).

    Проверяет, что при передаче некорректных значений кадастрового номера:
    - Если номер слишком короткий, возникает ошибка с соответствующим сообщением.
    - Если номер имеет неправильный формат, возникает ошибка с соответствующим сообщением.
    """
    # Проверка корректного формата кадастрового номера
    query = QueryBase(cadastral_number="12:34:567890:10")
    assert query.cadastral_number == "12:34:567890:10"

    # Проверка некорректного короткого кадастрового номера
    with pytest.raises(ValidationError) as exc_info:
        QueryBase(cadastral_number="short")
    assert "String should have at least 15 characters" in str(exc_info.value)

    # Проверка некорректного формата кадастрового номера
    with pytest.raises(ValidationError) as exc_info:
        QueryBase(cadastral_number="invalid_format_")
    assert "Value error, Кадастровый номер не соответствует формату" in str(exc_info.value)


def test_latitude_validation():
    """
    Тесты на валидацию поля latitude (широты).

    Проверяет, что:
    - Значение широты в пределах от -90 до 90 сохраняется корректно.
    - Значение широты вне этого диапазона вызывает ошибку валидации.
    """
    # Проверка корректного значения широты
    query = QueryCreate(cadastral_number="12:34:567890:10", latitude=-70.0)
    assert query.latitude == -70.0
    assert query.longitude is None

    # Проверка значения широты, превышающего допустимый диапазон
    with pytest.raises(ValidationError) as exc_info:
        QueryCreate(cadastral_number="12:34:567890:10", latitude=90.0)
    assert "Широта должна быть в диапазоне от -90 до 90." in str(exc_info.value)

    # Проверка значения широты, вызывающего ошибку валидации для некорректных значений
    with pytest.raises(ValidationError) as exc_info:
        QueryCreate(cadastral_number="12:34:567890:10", latitude=100.0)
    errors = exc_info.value.errors()
    assert any(err['loc'] == ('latitude',) and err['type'] == 'decimal_whole_digits' for err in errors)


def test_longitude_validation():
    """
    Тесты на валидацию поля longitude (долготы).

    Проверяет, что:
    - Значение долготы в пределах от -180 до 180 сохраняется корректно.
    - Значение долготы вне этого диапазона вызывает ошибку валидации.
    """
    # Проверка корректного значения долготы
    query = QueryCreate(cadastral_number="12:34:567890:10", longitude=-73.0)
    assert query.latitude is None
    assert query.longitude == -73.0

    # Проверка значения долготы, превышающего допустимый диапазон
    with pytest.raises(ValidationError) as exc_info:
        QueryCreate(cadastral_number="12:34:567890:10", longitude=200.0)
    assert "Долгота должна быть в диапазоне от -180 до 180." in str(exc_info.value)

    # Проверка значения долготы, вызывающего ошибку валидации для некорректных значений
    with pytest.raises(ValidationError) as exc_info:
        QueryCreate(cadastral_number="12:34:567890:10", longitude=-1100.0)
    errors = exc_info.value.errors()
    assert any(err['loc'] == ('longitude',) and err['type'] == 'decimal_whole_digits' for err in errors)


@pytest.mark.asyncio(loop_scope="session")
async def test_server_startup_check(async_client: AsyncClient, session: AsyncSession):
    """
    Тест на проверку старта сервера.

    Отправляется GET запрос на эндпоинт /ping, чтобы проверить, что сервер работает.
    Проверяется, что статус ответа 200 и содержимое соответствует ожидаемому сообщению о работе сервера.
    """
    response = await async_client.get("/ping")

    assert response.status_code == 200

    data = response.json()
    assert data == {'message': 'Server is running'}


@pytest.mark.asyncio(loop_scope="session")
async def test_create_new_query(
        async_client: AsyncClient,
        session: AsyncSession,
        auth_token: str
):
    """
    Тест на создание нового запроса.

    Отправляется POST запрос с кадастровым номером для создания нового запроса.
    Проверяется, что запрос был успешно создан, статус 200 и кадастровый номер в ответе.
    """
    query_data = {
        "cadastral_number": "12:34:567890:1011"
    }
    response = await async_client.post(
        "/query",
        json=query_data,
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "cadastral_number" in data
    assert data["cadastral_number"] == "12:34:567890:1011"


@pytest.mark.asyncio(loop_scope="session")
async def test_get_query_history(
        async_client: AsyncClient,
        session: AsyncSession,
        auth_token: str,
        query_history: list
):
    """
    Тест на получение истории запросов.

    Отправляется GET запрос на эндпоинт /history без фильтрации.
    Проверяется, что возвращается список записей истории запросов и количество элементов в ответе соответствует ожиданиям.
    """
    response = await async_client.get(
        "/history",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert isinstance(data, list)
    assert len(data) == 4


@pytest.mark.asyncio(loop_scope="session")
async def test_get_query_history_with_cadastral_number(
        async_client: AsyncClient,
        session: AsyncSession,
        auth_token: str,
        query_history: list
):
    """
    Тест для получения истории запросов с фильтрацией по кадастровому номеру.

    Отправляется GET запрос на эндпоинт /history с фильтром по кадастровому номеру.
    Проверяется, что возвращаются только записи с указанным кадастровым номером.
    """
    cadastral_number = "12:34:567890:1011"

    response = await async_client.get(
        "/history",
        params={"cadastral_number": cadastral_number},
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert all(record['cadastral_number'] == cadastral_number for record in data)
    assert len(data) == 2


@pytest.mark.asyncio(loop_scope="session")
async def test_get_query_history_invalid_cadastral_number(
        async_client: AsyncClient,
        session: AsyncSession,
        auth_token: str,
        query_history: list
):
    """
    Тест для проверки обработки некорректного кадастрового номера.

    Отправляется GET запрос с некорректным кадастровым номером.
    Проверяется, что возвращается статус 400 и соответствующее сообщение об ошибке.
    """
    response = await async_client.get(
        "/history",
        params={"cadastral_number": "invalid_format"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Кадастровый номер не соответствует формату" in response.json()["detail"]


@pytest.mark.asyncio(loop_scope="session")
async def test_get_query_history_no_records(
        async_client: AsyncClient,
        session: AsyncSession,
        auth_token: str,
        query_history: list
):
    """
    Тест для проверки обработки случая, когда записи не найдены.

    Отправляется GET запрос с кадастровым номером, для которого нет записей.
    Проверяется, что возвращается статус 404 и сообщение "Записи не найдены".
    """
    cadastral_number = "00:00:000000:00"
    response = await async_client.get(
        "/history",
        params={"cadastral_number": cadastral_number},
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Записи не найдены"


@pytest.mark.asyncio(loop_scope="session")
async def test_get_query_history_pagination(
        async_client: AsyncClient,
        session: AsyncSession,
        auth_token: str,
        query_history: list
):
    """
    Тест для проверки пагинации.

    Отправляется GET запрос на эндпоинт /history с параметрами page и size для проверки пагинации.
    Проверяется, что количество записей в ответе соответствует ожиданиям.
    """
    response = await async_client.get(
        "/history",
        params={"page": 1, "size": 3},
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) <= 3
