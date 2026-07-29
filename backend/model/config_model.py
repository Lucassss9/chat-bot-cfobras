from sqlalchemy import Column, Integer, String
from config.connection import Base


class Config(Base):
    __tablename__ = "config"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chave = Column(String, unique=True, nullable=False)
    valor = Column(String, nullable=True)