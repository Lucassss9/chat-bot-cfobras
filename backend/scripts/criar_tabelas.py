from config.connection import engine, base
from model.manual_model import Manual
from model.perguntas_sem_resposta_model import PerguntasSemResposta
from model.usuario_model import Usuario

print("Conectando ao servidor da Neon na AWS...")
base.metadata.create_all(bind=engine)
print("Sucesso! Tabelas criadas!")