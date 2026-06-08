from sqlalchemy import Column, Integer, Text
from config.connection import Base

class Manual(Base):
    __tablename__ = "manuais"

    id = Column(Integer, primary_key=True, autoincrement=True)
    conteudo = Column(Text, nullable=False)