from model.perguntas_sem_resposta_model import PerguntasSemResposta
from config.connection import session_local

def salvar(pergunta, usuario_id=None):
    session = session_local()
    
    try:
        nova_pergunta = PerguntasSemResposta(usuario_id=usuario_id, pergunta=pergunta)
        session.add(nova_pergunta)
        session.commit()
    except Exception as e:
        session.rollback()
        print(e)
    finally:
        session.close()