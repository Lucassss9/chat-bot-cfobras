from pydantic import BaseModel
from service.chat_service import processar_chat

class ChatRequest(BaseModel):
    pergunta: str
    usuario_id: int

def registrar_rotas(app):

    @app.post("/chat")
    def chat(request: ChatRequest):
        resposta = processar_chat(pergunta=request.pergunta, usuario_id=request.usuario_id)
        return {"resposta": resposta}