from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from infrastructure.api.routers.agent.chat import router as chat_router
from infrastructure.api.routers.agent.upload import router as upload_router
from infrastructure.api.routers.agent.learn import router as learn_router
from src.infrastructure.api.routers import chat, upload, learn 
app = FastAPI(title="EscalafonIA System", version="2.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, prefix="/api", tags=["Chat"])
app.include_router(upload_router, prefix="/api", tags=["Ingesta PDF"])
app.include_router(learn_router, prefix="/api", tags=["Aprendizaje Texto"])

@app.get("/health")
def health():
    return {"status": "ok"}
