import datetime
from sqlalchemy import (Column, Integer, String, Boolean, DateTime, Text,
                        LargeBinary, ForeignKey)
from sqlalchemy.orm import relationship
from config.connection import Base


class SolicitacaoObra(Base):
    __tablename__ = "solicitacao_obra"

    id = Column(Integer, primary_key=True, autoincrement=True)

    tipo_filial = Column(String, nullable=False, default="existente")
    filial_nome = Column(String, nullable=False)
    filial_cnpj = Column(String, nullable=True)
    filial_endereco = Column(String, nullable=True)
    filial_cidade = Column(String, nullable=True)
    filial_estado = Column(String, nullable=True)

    # dados da obra
    obra_nome = Column(String, nullable=False)
    obra_codigo = Column(String, nullable=True)
    obra_email = Column(String, nullable=True)
    obra_endereco = Column(String, nullable=True)
    obra_cidade = Column(String, nullable=True)
    obra_estado = Column(String, nullable=True)
    obra_engenheiro = Column(String, nullable=True)
    obra_descricao = Column(Text, nullable=True)

    ficha_nome = Column(String, nullable=True)
    ficha_arquivo = Column(LargeBinary, nullable=True)

    # controle
    status = Column(String, default="pendente")
    motivo = Column(Text, nullable=True)
    solicitante_id = Column(Integer, ForeignKey("usuario.id"))
    criado_em = Column(DateTime, default=datetime.datetime.now)

    pessoas = relationship("PessoaDaObra", back_populates="solicitacao",
                           cascade="all, delete-orphan")


class PessoaDaObra(Base):
    __tablename__ = "pessoa_da_obra"

    id = Column(Integer, primary_key=True, autoincrement=True)
    solicitacao_id = Column(Integer, ForeignKey("solicitacao_obra.id"), nullable=False)

    nome = Column(String, nullable=False)
    email = Column(String, nullable=False)
    funcao = Column(String, nullable=True)
    tipo = Column(String, nullable=True)
    ja_tem_acesso = Column(Boolean, default=False)

    solicitacao = relationship("SolicitacaoObra", back_populates="pessoas")