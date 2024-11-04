from random import randint
from typing import Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
from app.models import QueryHistory
from app.schemas import QueryCreate, QueryHistoryResponse, QueryResponse
from app.validators import validate_cadastral_number

router = APIRouter()


@router.post('/query', response_model=QueryResponse)
async def create_new_query(
        query: QueryCreate,
        session: AsyncSession = Depends(get_async_session)
):
    async with httpx.AsyncClient() as client:
        params = {'cadastral_number': query.cadastral_number}
        response = await client.get('http://127.0.0.1:8000/result', params=params)
        result = response.json()
        is_successful = result.get("result", False)
        current_latitude = query.latitude if query.latitude is not None else None
        current_longitude = query.longitude if query.longitude is not None else None

        db_query = QueryHistory(
            cadastral_number=query.cadastral_number,
            latitude=current_latitude,
            longitude=current_longitude,
            result=is_successful
        )

        session.add(db_query)
        await session.commit()
        await session.refresh(db_query)

        return db_query


@router.get('/ping')
async def server_startup_check():
    return {'message': 'Server is running'}


@router.get('/history', response_model=list[QueryHistoryResponse])
async def get_query_history(
        cadastral_number: Optional[str] = Query(
            None, description="Кадастровый номер для фильтрации истории"),
        page: int = Query(ge=1, default=1),
        size: int = Query(ge=1, le=100, default=10),
        session: AsyncSession = Depends(get_async_session)
):
    if cadastral_number:
        try:
            validate_cadastral_number(cadastral_number)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    query = select(QueryHistory)
    if cadastral_number:
        query = query.where(QueryHistory.cadastral_number == cadastral_number)

    query = query.order_by(desc(QueryHistory.created_at)).offset((page - 1) * size).limit(size)

    result = await session.execute(query)
    records = result.scalars().all()

    if not records:
        raise HTTPException(status_code=404, detail="Записи не найдены")

    return records


@router.get('/result')
async def get_result(cadastral_number: str = Query(...)):
    result = bool(randint(0, 1))
    return JSONResponse(content={'result': result})
