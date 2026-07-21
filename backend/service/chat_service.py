from repository.manual_repository import buscar_manual
from repository.pergunta_sem_resposta_repository import salvar
from repository.mensagens_repository import salvar as salvar_mensagem, buscar_ultimas
from service.ai_service import gerar_resposta


def processar_chat(pergunta, usuario_id, db):
    manual = buscar_manual(db)

    if manual is None:
        return "O manual ainda não foi sincronizado. Avise o administrador."

    historico = buscar_ultimas(usuario_id, 10, db)
    resposta = gerar_resposta(pergunta, manual.conteudo, historico)

    salvar_mensagem("user", pergunta, usuario_id, db)
    salvar_mensagem("assistant", resposta, usuario_id, db)

    if "não sei" in resposta.strip().lower():
        salvar(pergunta, usuario_id, db)

    return resposta