from random import randint, uniform

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
import httpx
import asyncio

from .database import get_async_session
from .models import QueryHistory
from .schemas import QueryCreate, QueryDB

api_router = APIRouter()


@api_router.post('/query', response_model=QueryDB)
async def create_new_query(
        query: QueryCreate,
        session: AsyncSession = Depends(get_async_session)
):
    async with httpx.AsyncClient() as client:
        current_latitude = round(uniform(-90, 90), 6)
        current_longitude = round(uniform(-180, 180), 6)
        response = await get_result()
        result = response.json()
        is_successful = result.get("result", False)

        db_query = QueryHistory(
            cadastral_number=query.cadastral_number,
            latitude=current_latitude,
            longitude=current_longitude,
            result=is_successful)

        try:
            session.add(db_query)
            await session.commit()
            await session.refresh(db_query)
        except IntegrityError as e:
            await session.rollback()
            if 'unique_lat_long' in str(e):
                raise HTTPException(status_code=400, detail="Сочетание широты и долготы уже существует.")
            raise HTTPException(status_code=400, detail="Кадастровый номер уже существует.")

        return db_query


@api_router.get('/ping')
async def server_startup_check():
    return {'message': 'Server is running'}


@api_router.get('/history', response_model=list[QueryDB])
async def get_query_history(session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(QueryHistory))
    return result.scalars().all()


@api_router.get('/result')
async def get_result():
    await asyncio.sleep(randint(1, 30))
    result = bool(randint(0, 1))
    response = httpx.Response(200, json={"result": result})
    return response
