import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from config.connection import Base


class Conversa(Base):
    __tablename__ = "conversa"

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_usuario = Column(Integer, ForeignKey("usuario.id"), nullable=False)
    titulo = Column(String, nullable=False, default="Nova conversa")
    criado_em = Column(DateTime, nullable=False, default=datetime.datetime.now)
    atualizado_em = Column(DateTime, nullable=False, default=datetime.datetime.now)