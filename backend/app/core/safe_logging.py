"""Logs por allowlist: nunca serializar mensagem, args ou traceback bruto."""

import json
import logging
from logging.config import dictConfig
from uuid import UUID


ROTAS = set()


class SafeFormatter(logging.Formatter):
    def format(self, record):
        evento = getattr(record, "evento", None)
        dados = {
            "level": logging.getLevelName(record.levelno),
            "event": evento if evento in (
                "request_completed", "request_failed",
            ) else "diagnostic_redacted",
        }
        correlation = getattr(record, "correlation_id", None)
        try:
            if str(UUID(correlation, version=4)) == correlation:
                dados["correlation_id"] = correlation
        except (ValueError, TypeError, AttributeError):
            pass
        rota = getattr(record, "route_template", None)
        if rota in ROTAS:
            dados["route"] = rota
        status = getattr(record, "status_code", None)
        if type(status) is int and 100 <= status <= 599:
            dados["status"] = status
        duracao = getattr(record, "duration_ms", None)
        if type(duracao) in (int, float) and 0 <= duracao < 86400000:
            dados["duration_ms"] = round(duracao, 3)
        return json.dumps(dados, ensure_ascii=True)


LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"safe": {"()": SafeFormatter}},
    "handlers": {"safe": {
        "class": "logging.StreamHandler", "formatter": "safe",
        "stream": "ext://sys.stderr",
    }},
    "root": {"handlers": ["safe"], "level": "INFO"},
    "loggers": {
        nome: {"handlers": [], "propagate": True, "level": "INFO"}
        for nome in ("uvicorn", "uvicorn.error", "uvicorn.access")
    },
}


def configurar_logs():
    dictConfig(LOG_CONFIG)
    # Bibliotecas podem ter handlers proprios configurados antes do startup.
    for logger in logging.root.manager.loggerDict.values():
        if isinstance(logger, logging.Logger):
            for handler in logger.handlers:
                handler.setFormatter(SafeFormatter())
