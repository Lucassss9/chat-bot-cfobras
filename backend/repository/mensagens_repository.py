from sqlalchemy import desc
from model.mensagens_model import Mensagens

def salvar(papel, texto, id_usuario, db):
    try:
        mensagens = Mensagens(papel=papel, texto=texto, id_usuario=id_usuario)
        db.add(mensagens)
        db.commit()
    except:
        db.rollback()
        raise

def buscar_ultimas(usuario_id, n, db):
    mensagens = (db.query(Mensagens).filter(usuario_id == Mensagens.id_usuario)
                 .order_by(desc(Mensagens.data_hora)).limit(n).all())

    mensagens.reverse()

    return mensagens