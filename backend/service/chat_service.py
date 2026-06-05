from repository.manual_repository import buscar_manual
from repository.pergunta_sem_resposta_repository import salvar
from service.ai_service import gerar_resposta

def processar_chat(pergunta, usuario_id, db):
    manual = buscar_manual(db)

    resposta = gerar_resposta(pergunta, manual)

    resposta_normalizada  = resposta.strip().lower()

    if "não sei" in resposta_normalizada:
        salvar(pergunta, usuario_id, db)

    return resposta