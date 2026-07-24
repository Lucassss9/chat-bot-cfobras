import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from config.connection import Base


class Colaborador(Base):
    __tablename__ = "colaborador"

    id = Column(Integer, primary_key=True, autoincrement=True)

    nome = Column(String, nullable=False)
    email = Column(String, nullable=False)
    funcao = Column(String, nullable=False)
    estado = Column(String, nullable=False)
    obra = Column(String, nullable=False)       
    observacao = Column(Text, nullable=True)
    terceirizado = Column(Boolean, default=False)
    cpf = Column(String, nullable=True)

    status = Column(String, default="pendente")
    motivo = Column(Text, nullable=True)
    erro = Column(Text, nullable=True)
    solicitante_id = Column(Integer, ForeignKey("usuario.id"))
    criado_em = Column(DateTime, default=datetime.datetime.now)