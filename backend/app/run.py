"""Entrada suportada para logs sem dados sensiveis, inclusive no startup."""

import uvicorn

from app.core.safe_logging import LOG_CONFIG


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app", host="0.0.0.0", port=8000,
        log_config=LOG_CONFIG, access_log=False, proxy_headers=False,
    )
