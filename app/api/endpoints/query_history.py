import asyncio
from random import randint
from typing import Optional

import httpx
from fastapi import APIRouter, Depends, Header, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import validate_cadastral_number
from app.core.database import get_async_session
from app.core.user import current_user
from app.models import QueryHistory, User
from app.schemas.query_history import (QueryCreate, QueryHistoryResponse,
                                       QueryResponse)

router = APIRouter()

TIMEOUT = 60


@router.post('/query', response_model=QueryResponse)
async def create_new_query(
        query: QueryCreate,
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_user),
        authorization: str = Header(None)
):
    """
    Создает новый запрос с указанным кадастровым номером и координатами.

    Аргументы:
        query (QueryCreate): Данные для создания запроса
         (кадастровый номер, координаты).
        session (AsyncSession): Асинхронная сессия для работы с базой данных.
        user (User): Текущий пользователь, делавший запрос.

    Возвращает:
        QueryResponse: Ответ с результатом запроса.

    Исключения:
        httpx.ReadTimeout: Возникает, если запрос к внешнему сервису занимает
         слишком много времени (время ожидания превышает заданный таймаут).
    """
    async with httpx.AsyncClient() as client:
        params = {'cadastral_number': query.cadastral_number}
        headers = {
            "Authorization": authorization
        }
        try:
            response = await client.get(
                'http://127.0.0.1:8000/result',
                params=params,
                headers=headers,
                timeout=TIMEOUT
            )
            result = response.json()
        except httpx.ReadTimeout:
            print("The request timed out.")
            result = {}
        is_successful = result.get("result", False)
        current_latitude = (
            query.latitude if query.latitude is not None else None
        )
        current_longitude = (
            query.longitude if query.longitude is not None else None
        )

        # Создание нового объекта истории запроса
        db_query = QueryHistory(
            cadastral_number=query.cadastral_number,
            latitude=current_latitude,
            longitude=current_longitude,
            result=is_successful,
            user_id=user.id
        )

        session.add(db_query)
        await session.commit()
        await session.refresh(db_query)

        return db_query


@router.get('/ping')
async def server_startup_check():
    """
    Проверка состояния сервера.

    Возвращает:
        dict: Сообщение о том, что сервер работает.
    """
    return {'message': 'Server is running'}


@router.get('/history', response_model=list[QueryHistoryResponse])
async def get_query_history(
        cadastral_number: Optional[str] = Query(
            None, description="Кадастровый номер для фильтрации истории"),
        page: int = Query(ge=1, default=1),
        size: int = Query(ge=1, le=100, default=10),
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_user),
):
    """
    Получает историю запросов с фильтрацией по кадастровому номеру
     и постраничной навигацией.

    Аргументы:
        cadastral_number (Optional[str]): Кадастровый номер для фильтрации
         (если передан).
        page (int): Номер страницы для пагинации.
        size (int): Количество записей на странице.
        session (AsyncSession): Асинхронная сессия для работы с базой данных.
        user (User): Текущий пользователь, для которого мы получаем историю.

    Возвращает:
        List[QueryHistoryResponse]: Список записей истории запросов.

    Исключения:
        HTTPException: Возникает, если записи не найдены или
         кадастровый номер некорректен.
    """
    if cadastral_number:
        try:
            validate_cadastral_number(cadastral_number)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    query = select(QueryHistory).filter(QueryHistory.user_id == user.id)
    if cadastral_number:
        query = query.where(QueryHistory.cadastral_number == cadastral_number)

    query = query.order_by(desc(QueryHistory.created_at)).offset(
        (page - 1) * size).limit(size)

    result = await session.execute(query)
    records = result.scalars().all()

    if not records:
        raise HTTPException(status_code=404, detail="Записи не найдены")

    return records


@router.get('/result')
async def get_result(
        cadastral_number: str = Query(...),
        user: User = Depends(current_user)
):
    """
    Генерирует случайный результат для кадастрового номера и имитирует
     задержку выполнения.

    Аргументы:
        cadastral_number (str): Кадастровый номер для запроса результата.

    Возвращает:
        JSONResponse: Ответ с результатом запроса (случайный `True`
         или `False`).
    """
    result = bool(randint(0, 1))
    await asyncio.sleep(randint(1, 60))  # Имитируем задержку
    return JSONResponse(content={'result': result})
