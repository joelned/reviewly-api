from fastapi import FastAPI
from app.routers import auth

app = FastAPI(title="Reviewly API", version="0.1.0")

app.include_router(auth.router)


@app.get("/")
def root():
    return {"message": "Reviewly is running"}


@app.get("/health")
def health():
    return {"status": "ok"}
