from sqlalchemy import Column, Integer, String, Text
from .connection import base

class Manual(base):
    __tablename__ = "manuais"

    id = Column(Integer, primary_key=True, autoincrement=True)
    categoria = Column(String, nullable=False)
    titulo = Column(String, nullable=False)
    conteudo = Column(Text, nullable=False)