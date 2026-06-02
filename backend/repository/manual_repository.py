from model.manual_model import Manual
from config.connection import session_local

def buscar_manual():
    session = session_local()
    manual = session.query(Manual).first()
    session.close()
    return manual.conteudo