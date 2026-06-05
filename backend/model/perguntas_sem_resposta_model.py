from sqlalchemy import Column, Integer, Text, ForeignKey
from config.connection import get_db, Base

class PerguntasSemResposta(Base):
    __tablename__ = 'perguntas_sem_resposta'

    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey('usuario.id'))
    pergunta = Column(Text)