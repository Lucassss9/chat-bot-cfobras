from repository.manual_repository import buscar_manual
from service.ai_service import gerar_resposta
from repository.pergunta_sem_resposta_repository import salvar

def processar_chat(pergunta):
    manual = buscar_manual()

    resposta = gerar_resposta(pergunta, manual)

    resposta_normalizada  = resposta.strip().lower()

    if "não sei" in resposta_normalizada:
        salvar(pergunta)

    return resposta