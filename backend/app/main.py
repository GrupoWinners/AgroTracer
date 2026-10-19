
from fastapi import FastAPI

app = FastAPI(
    title="AgroTracer API",
    description="API backend do projeto AgroTracer",
    version="0.1.0",
)


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}
