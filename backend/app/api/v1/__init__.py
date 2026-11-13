from fastapi import APIRouter

from app.api.v1.animais import router as animais_router
from app.api.v1.associacoes import router as associacoes_router
from app.api.v1.fazendas import router as fazendas_router
from app.api.v1.lotes import router as lotes_router
from app.api.v1.movimentacoes import router as movimentacoes_router
from app.api.v1.parametros import router as parametros_router
from app.api.v1.manejos import router as manejos_router
from app.api.v1.fechamentos import router as fechamentos_router


api_router = APIRouter()

api_router.include_router(fazendas_router)
api_router.include_router(animais_router)
api_router.include_router(lotes_router)
api_router.include_router(associacoes_router)
api_router.include_router(movimentacoes_router)
api_router.include_router(parametros_router)
api_router.include_router(manejos_router)
api_router.include_router(fechamentos_router)

__all__ = ["api_router"]
