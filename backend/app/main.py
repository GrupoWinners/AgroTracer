from fastapi import FastAPI

app = FastAPI(
    title="AgroTracer API",
    version="0.1.0",
)


@app.get("/health")
def verificar_saude():
    return {"status": "ok"}
