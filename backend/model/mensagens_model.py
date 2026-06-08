import datetime
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from config.connection import Base

class Mensagens(Base):
    __tablename__ = "mensagens"

    id = Column(Integer, primary_key=True)
    id_usuario = Column(Integer, ForeignKey('usuario.id'))
    papel = Column(Text)
    texto = Column(Text)
    data_hora = Column(DateTime, default=datetime.datetime.now)