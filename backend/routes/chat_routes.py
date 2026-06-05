from pydantic import BaseModel
from fastapi import Depends
from sqlalchemy.orm import Session
from service.chat_service import processar_chat
from config.connection import get_db

class ChatRequest(BaseModel):
    pergunta: str
    usuario_id: int

def registrar_rotas(app):

    @app.post("/chat")
    def chat(request: ChatRequest, db: Session = Depends(get_db)):
        resposta = processar_chat(pergunta=request.pergunta, usuario_id=request.usuario_id, db=db)
        return {"resposta": resposta}