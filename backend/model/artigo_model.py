import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from config.connection import Base


class Artigo(Base):
    __tablename__ = "artigo"

    id = Column(Integer, primary_key=True, autoincrement=True)
    grupo = Column(String, nullable=False)
    pergunta = Column(Text, nullable=False)
    caminho = Column(Text, nullable=True)
    variacoes = Column(Text, nullable=True)
    resposta = Column(Text, nullable=False)
    ativo = Column(Boolean, nullable=False, default=True)
    destaque = Column(Boolean, nullable=False, default=False)
    ordem = Column(Integer, nullable=False, default=0)
    atualizado_em = Column(DateTime, nullable=False, default=datetime.datetime.now)