from repository.artigo_repository import montar_contexto
from repository.pergunta_sem_resposta_repository import salvar
from repository.mensagens_repository import salvar as salvar_mensagem, buscar_ultimas
from service.ai_service import gerar_resposta

SEM_RESPOSTA = ("nao sei", "não sei", "nao sei.", "não sei.")


def _admitiu_nao_saber(resposta):
    return (resposta or "").strip().lower().strip(".!") in ("nao sei", "não sei")


def processar_chat(pergunta, usuario_id, db):
    contexto = montar_contexto(db)

    if not contexto:
        return "O manual ainda não tem conteúdo. Avise o administrador."

    historico = buscar_ultimas(usuario_id, 10, db)
    resposta = gerar_resposta(pergunta, contexto, historico)

    salvar_mensagem("user", pergunta, usuario_id, db)
    salvar_mensagem("assistant", resposta, usuario_id, db)

    if _admitiu_nao_saber(resposta):
        salvar(pergunta, usuario_id, db)

    return resposta