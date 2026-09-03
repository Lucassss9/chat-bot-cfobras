from sqlalchemy import desc
from model.mensagens_model import Mensagens

def salvar(papel, texto, id_usuario, db, id_conversa=None):
    try:
        mensagens = Mensagens(papel=papel, texto=texto, id_usuario=id_usuario,
                              id_conversa=id_conversa)
        db.add(mensagens)
        db.commit()
    except:
        db.rollback()
        raise

def buscar_ultimas(usuario_id, n, db, id_conversa=None):
    consulta = db.query(Mensagens).filter(Mensagens.id_usuario == usuario_id)

    if id_conversa is not None:
        consulta = consulta.filter(Mensagens.id_conversa == id_conversa)

    mensagens = consulta.order_by(desc(Mensagens.data_hora)).limit(n).all()

    mensagens.reverse()

    return mensagens