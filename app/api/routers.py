from fastapi import APIRouter

from app.api.endpoints import query_history_router, user_router, admin_router

main_router = APIRouter()
main_router.include_router(query_history_router)
main_router.include_router(user_router)
main_router.include_router(admin_router)