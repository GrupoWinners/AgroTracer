from fastapi import APIRouter

from app.api.v1.fazendas import router as fazendas_router

api_router = APIRouter()
api_router.include_router(fazendas_router)

__all__ = ["api_router"]
