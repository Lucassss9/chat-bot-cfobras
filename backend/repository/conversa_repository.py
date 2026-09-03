from datetime import datetime

from sqlalchemy import desc

from model.conversa_model import Conversa
from model.mensagens_model import Mensagens

TITULO_PADRAO = "Nova conversa"


def listar(usuario_id, db):
    return (db.query(Conversa)
            .filter(Conversa.id_usuario == usuario_id)
            .order_by(desc(Conversa.atualizado_em))
            .all())


def buscar(conversa_id, usuario_id, db):
    """Sempre filtrando por usuario: sem isso alguem leria a conversa de outro
    trocando o id na URL."""
    return (db.query(Conversa)
            .filter(Conversa.id == conversa_id, Conversa.id_usuario == usuario_id)
            .first())


def criar(usuario_id, db, titulo=TITULO_PADRAO):
    try:
        conversa = Conversa(id_usuario=usuario_id, titulo=titulo)
        db.add(conversa)
        db.commit()
        db.refresh(conversa)
        return conversa
    except Exception:
        db.rollback()
        raise


def renomear(conversa_id, usuario_id, titulo, db):
    try:
        conversa = buscar(conversa_id, usuario_id, db)
        if conversa is None:
            return None
        conversa.titulo = titulo.strip() or TITULO_PADRAO
        db.commit()
        db.refresh(conversa)
        return conversa
    except Exception:
        db.rollback()
        raise


def marcar_uso(conversa, db):
    try:
        conversa.atualizado_em = datetime.now()
        db.commit()
    except Exception:
        db.rollback()


def titular_pela_primeira_pergunta(conversa, pergunta, db):
    """A conversa nasce como 'Nova conversa' e ganha nome na primeira pergunta.
    Pedir titulo antes de comecar seria atrito para quem so quer perguntar."""
    if conversa.titulo != TITULO_PADRAO:
        return

    texto = " ".join((pergunta or "").split())
    if not texto:
        return

    conversa.titulo = texto[:57] + "..." if len(texto) > 60 else texto
    try:
        db.commit()
    except Exception:
        db.rollback()


def mensagens_da_conversa(conversa_id, usuario_id, db):
    return (db.query(Mensagens)
            .filter(Mensagens.id_usuario == usuario_id,
                    Mensagens.id_conversa == conversa_id)
            .order_by(Mensagens.data_hora, Mensagens.id)
            .all())


def apagar(conversa_id, usuario_id, db):
    try:
        conversa = buscar(conversa_id, usuario_id, db)
        if conversa is None:
            return False

        (db.query(Mensagens)
         .filter(Mensagens.id_conversa == conversa_id)
         .delete(synchronize_session=False))

        db.delete(conversa)
        db.commit()
        return True
    except Exception:
        db.rollback()
        raise