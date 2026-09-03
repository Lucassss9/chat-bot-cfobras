from repository.artigo_repository import montar_contexto
from repository.pergunta_sem_resposta_repository import salvar
from repository.mensagens_repository import salvar as salvar_mensagem, buscar_ultimas
from service.ai_service import gerar_resposta


def _admitiu_nao_saber(resposta):
    return (resposta or "").strip().lower().strip(".!") in ("nao sei", "não sei")


def _e_pergunta_de_verdade(pergunta):
    texto = (pergunta or "").strip().lower().strip(".!?")

    if len(texto) < 3:
        return False

    sem_unidade = texto.replace(",", ".").rstrip("abcdefghijklmnopqrstuvwxyz²³ ")
    try:
        float(sem_unidade)
        return False
    except ValueError:
        pass

    if texto in ("sim", "nao", "não", "ok", "certo", "isso", "pode", "claro",
                 "obrigado", "obrigada", "valeu", "entendi"):
        return False

    return True


def processar_chat(pergunta, usuario_id, db):
    contexto = montar_contexto(db)

    if not contexto:
        return "O manual ainda não tem conteúdo. Avise o administrador."

    historico = buscar_ultimas(usuario_id, 10, db)
    resposta = gerar_resposta(pergunta, contexto, historico)

    salvar_mensagem("user", pergunta, usuario_id, db)
    salvar_mensagem("assistant", resposta, usuario_id, db)

    if _admitiu_nao_saber(resposta) and _e_pergunta_de_verdade(pergunta):
        salvar(pergunta, usuario_id, db)

    return resposta