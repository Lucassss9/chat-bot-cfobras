from model.perguntas_sem_resposta_model import PerguntasSemResposta
from config.connection import session_local

def salvar(pergunta, usuario_id=None):
    session = session_local()
    session.add(PerguntasSemResposta(usuario_id=usuario_id, pergunta=pergunta))
