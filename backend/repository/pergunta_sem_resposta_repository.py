from model.perguntas_sem_resposta_model import PerguntasSemResposta

def salvar(pergunta, usuario_id, db):

    try:
        nova_pergunta = PerguntasSemResposta(usuario_id=usuario_id, pergunta=pergunta)
        db.add(nova_pergunta)
        db.commit()
    except Exception as e:
        db.rollback()
        print(e)