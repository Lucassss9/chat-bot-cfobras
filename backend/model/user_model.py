from sqlalchemy import Column, Integer, Text
from config.connection import base

class Usuario(base):
    __tablename__ = 'usuario'

    id = Column(Integer, primary_key=true, autoincrement=True)
    nome = Column(Text, nullable=False)
    email = Column(Text, nullable=False)
    senha = Column(Text, nullable=False)