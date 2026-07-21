from sqlalchemy import Column, Integer, String, Boolean
from config.connection import Base

PAPEIS = ["comum", "solicitante", "admin"]

class Usuario(Base):
    __tablename__ = 'usuario'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    senha = Column(String, nullable=False)

    cargo = Column(String, nullable=True)
    papel = Column(String, nullable=False, default="comum")
    ativo = Column(Boolean, nullable=False, default=True)