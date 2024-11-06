import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.main import app
from app.models import QueryHistory, User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@pytest_asyncio.fixture(scope='session')
async def session() -> AsyncSession:
    """
    Фикстура для создания и использования сессии базы данных.

    Возвращает:
        AsyncSession: Асинхронная сессия для взаимодействия с базой данных.

    После выполнения тестов сессия откатывает все изменения (не сохраняются данные).
    """
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture(scope='session')
async def async_client() -> AsyncClient:
    """
    Фикстура для создания асинхронного HTTP клиента для тестов с использованием FastAPI.

    Возвращает:
        AsyncClient: Клиент для выполнения HTTP-запросов к тестовому приложению FastAPI.

    Используется для отправки запросов к API в рамках тестов.
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture(scope='session')
async def user(session: AsyncSession):
    """
    Фикстура для создания пользователя в базе данных и получения его объекта.

    Возвращает:
        User: Созданный пользователь с заполненными полями, включая хешированный пароль.

    После выполнения тестов удаляет созданного пользователя из базы данных.
    """
    user_data = {
        "email": "testuser@example.com",
        "password": "pass1234",
    }

    hashed_password = pwd_context.hash(user_data["password"])

    user = User(
        email=user_data["email"],
        hashed_password=hashed_password,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)

    yield user

    await session.delete(user)
    await session.commit()


@pytest_asyncio.fixture(scope="session")
async def auth_token(async_client: AsyncClient, user: User):
    """
    Фикстура для логина пользователя и получения JWT токена.

    Аргументы:
        async_client (AsyncClient): Клиент для выполнения HTTP-запросов.
        user (User): Тестовый пользователь, который должен быть аутентифицирован.

    Возвращает:
        str: JWT токен для авторизации в дальнейшем.

    Этот токен используется в заголовках запросов для проверки защищенных эндпоинтов.
    """
    response = await async_client.post(
        "/auth/jwt/login",
        data={"username": user.email, "password": "pass1234"},
    )
    assert response.status_code == 200, "Не удалось получить токен"
    token = response.json().get("access_token")
    assert token, "Токен не найден"

    return token


@pytest_asyncio.fixture(scope='session')
async def query_history(session: AsyncSession, user: User):
    """
        Фикстура для добавления нескольких записей в таблицу `QueryHistory` для тестового пользователя.

        Аргументы:
            session (AsyncSession): Сессия для взаимодействия с базой данных.
            user (User): Тестовый пользователь, для которого создаются записи истории запросов.

        Возвращает:
            list: Список объектов `QueryHistory`, созданных для тестового пользователя.

        Используется для тестирования эндпоинтов, которые работают с историей запросов пользователя.
        """
    query_data = [
        {"cadastral_number": "12:34:567890:1011", "latitude": 55.7558, "longitude": 37.6176, "result": True},
        {"cadastral_number": "12:34:567890:1012", "latitude": 59.9343, "longitude": 30.3351, "result": False},
        {"cadastral_number": "12:34:567890:1013", "latitude": 48.8566, "longitude": 2.3522, "result": True}
    ]

    query_history_records = [
        QueryHistory(
            cadastral_number=data["cadastral_number"],
            latitude=data["latitude"],
            longitude=data["longitude"],
            result=data["result"],
            user_id=user.id
        )
        for data in query_data
    ]

    session.add_all(query_history_records)
    await session.commit()

    return query_history_records
