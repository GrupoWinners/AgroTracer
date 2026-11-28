"""Envelope de validação para rotas da Sprint 3."""

from fastapi.exceptions import RequestValidationError
from fastapi.routing import APIRoute
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    code: str
    message: str
    correlation_id: str
    field_errors: dict[str, str] = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    error: ErrorDetail


class ValidationRoute(APIRoute):
    def get_route_handler(self):
        original = super().get_route_handler()

        async def handler(request):
            try:
                return await original(request)
            except RequestValidationError as erro:
                return JSONResponse(status_code=422, content={
                    "error": {
                        "code": "DADOS_INVALIDOS",
                        "message": "Verifique os campos informados.",
                        "field_errors": {
                            ".".join(map(str, item["loc"])): item["msg"]
                            for item in erro.errors()
                        },
                        "correlation_id": request.state.correlation_id,
                    },
                })
        return handler
