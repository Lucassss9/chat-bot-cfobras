from typing import Optional

from pydantic import BaseModel
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from repository.pergunta_sem_resposta_repository import listar_perguntas
from repository import conversa_repository as conversas
from service.chat_service import processar_chat
from config.connection import get_db
from config.auth import usuario_atual


class ChatRequest(BaseModel):
    pergunta: str
    id_conversa: Optional[int] = None


class TituloRequest(BaseModel):
    titulo: str


def _para_dict(c):
    return {
        "id": c.id,
        "titulo": c.titulo,
        "criado_em": c.criado_em.isoformat() if c.criado_em else None,
        "atualizado_em": c.atualizado_em.isoformat() if c.atualizado_em else None,
    }


def registrar_rotas(app):

    @app.post("/chat")
    def chat(request: ChatRequest,
             db: Session = Depends(get_db),
             usuario_id: str = Depends(usuario_atual)):
        if request.id_conversa is None:
            conversa = conversas.criar(int(usuario_id), db)
        else:
            conversa = conversas.buscar(request.id_conversa, int(usuario_id), db)
            if conversa is None:
                raise HTTPException(status_code=404, detail="Conversa não encontrada")

        conversas.titular_pela_primeira_pergunta(conversa, request.pergunta, db)

        resposta, escalou = processar_chat(pergunta=request.pergunta,
                                          usuario_id=usuario_id,
                                          db=db,
                                          id_conversa=conversa.id)

        conversas.marcar_uso(conversa, db)
        return {"resposta": resposta, "escalou": escalou,
                "id_conversa": conversa.id, "titulo": conversa.titulo}

    @app.get("/conversa")
    def listar_conversas(db: Session = Depends(get_db),
                         usuario_id: str = Depends(usuario_atual)):
        return [_para_dict(c) for c in conversas.listar(int(usuario_id), db)]

    @app.post("/conversa")
    def nova_conversa(db: Session = Depends(get_db),
                      usuario_id: str = Depends(usuario_atual)):
        return _para_dict(conversas.criar(int(usuario_id), db))

    @app.get("/conversa/{conversa_id}/mensagens")
    def mensagens(conversa_id: int,
                  db: Session = Depends(get_db),
                  usuario_id: str = Depends(usuario_atual)):
        if conversas.buscar(conversa_id, int(usuario_id), db) is None:
            raise HTTPException(status_code=404, detail="Conversa não encontrada")

        return [{"papel": m.papel, "texto": m.texto,
                 "data_hora": m.data_hora.isoformat() if m.data_hora else None}
                for m in conversas.mensagens_da_conversa(conversa_id, int(usuario_id), db)]

    @app.put("/conversa/{conversa_id}")
    def renomear_conversa(conversa_id: int,
                          dados: TituloRequest,
                          db: Session = Depends(get_db),
                          usuario_id: str = Depends(usuario_atual)):
        conversa = conversas.renomear(conversa_id, int(usuario_id), dados.titulo, db)
        if conversa is None:
            raise HTTPException(status_code=404, detail="Conversa não encontrada")
        return _para_dict(conversa)

    @app.delete("/conversa/{conversa_id}")
    def apagar_conversa(conversa_id: int,
                        db: Session = Depends(get_db),
                        usuario_id: str = Depends(usuario_atual)):
        if not conversas.apagar(conversa_id, int(usuario_id), db):
            raise HTTPException(status_code=404, detail="Conversa não encontrada")
        return {"mensagem": "Conversa apagada."}

    @app.get("/chat/perguntas-sem-respostas")
    def perguntas(db: Session = Depends(get_db), usuario_id: str = Depends(usuario_atual)):
        return listar_perguntas(usuario_id=usuario_id, db=db)