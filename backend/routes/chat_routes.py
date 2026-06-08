from pydantic import BaseModel
from fastapi import Depends
from sqlalchemy.orm import Session
from repository.pergunta_sem_resposta_repository import listar_perguntas
from service.chat_service import processar_chat
from config.connection import get_db
from config.auth import usuario_atual

class ChatRequest(BaseModel):
    pergunta: str

def registrar_rotas(app):

    @app.post("/chat")
    def chat(request: ChatRequest, db: Session = Depends(get_db), usuario_id: str = Depends(usuario_atual)):
        resposta = processar_chat(pergunta=request.pergunta, usuario_id=usuario_id, db=db)
        return {"resposta": resposta}

    @app.get("/chat/perguntas-sem-respostas")
    def perguntas(db: Session = Depends(get_db), usuario_id: str = Depends(usuario_atual)):
        return listar_perguntas(usuario_id=usuario_id, db=db)