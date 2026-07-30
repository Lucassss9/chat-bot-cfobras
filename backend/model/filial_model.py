from sqlalchemy import Column, Integer, String
from config.connection import Base


class Filial(Base):
    __tablename__ = "filial"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String, nullable=False)
    estado = Column(String, nullable=False)