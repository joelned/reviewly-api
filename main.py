from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Reviewly API", version="0.1.0")


class SubmissionRequest(BaseModel):
    title: str
    description: str
    language: str


class SubmissionResponse(BaseModel):
    id: int
    title: str
    description: str
    language: str


@app.get("/")
def root():
    return {"message": "Reviewly is running"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/submissions")
def create_submissions(submissions: SubmissionRequest):
    return SubmissionResponse(id=1, **submissions.model_dump)
