from pydantic import BaseModel
from service.ai_service import gerar_resposta
from repository.manual_repository import buscar_manual

class ChatRequest(BaseModel):
    pergunta: str

def registrar_rotas(app):

    @app.post("/chat")
    def chat(request: ChatRequest):
        resposta = gerar_resposta(pergunta=request.pergunta, texto_manual=buscar_manual())
        return {"resposta": resposta}