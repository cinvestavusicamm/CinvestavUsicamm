from pydantic import BaseModel
from typing import List


class ChatRequest(BaseModel):
    prompt: str


class ChatResponse(BaseModel):
    reply: str


class EvaluateRequest(BaseModel):
    texto: str


class EvaluateResponse(BaseModel):
    score: float
    summary: str


class QuestionRequest(BaseModel):
    tema: str


class QuestionResponse(BaseModel):
    questions: List[str]
