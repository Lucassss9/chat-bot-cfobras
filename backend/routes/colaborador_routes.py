from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from config.auth import usuario_atual, exigir_papel
from config.connection import get_db
from repository.colaborador_repository import (
    salvar,
    listar_por_status,
    listar_do_solicitante,
    atualizar_status,
)

router = APIRouter()

ESTADOS = ["SP", "RJ"]
STATUS_VALIDOS = ["pendente", "processando", "concluido", "erro"]


class ColaboradorCadastro(BaseModel):
    nome: str
    email: EmailStr
    funcao: str
    estado: str
    obra: str
    terceirizado: bool = False
    cpf: Optional[str] = None
    data_admissao: Optional[date] = None
    exibir_epi: bool = False


class StatusUpdate(BaseModel):
    status: str
    erro: Optional[str] = None


def _para_dict(colaborador):
    return {
        "id": colaborador.id,
        "nome": colaborador.nome,
        "email": colaborador.email,
        "funcao": colaborador.funcao,
        "estado": colaborador.estado,
        "obra": colaborador.obra,
        "terceirizado": colaborador.terceirizado,
        "cpf": colaborador.cpf,
        # o robô digita no formato DD/MM/AAAA
        "data_admissao": colaborador.data_admissao.strftime("%d/%m/%Y") if colaborador.data_admissao else None,
        "exibir_epi": colaborador.exibir_epi,
        "status": colaborador.status,
        "erro": colaborador.erro,
    }


@router.post("/colaborador/cadastrar")
def cadastrar(dados: ColaboradorCadastro,
              db: Session = Depends(get_db),
              usuario_id: str = Depends(usuario_atual),
              papel: str = Depends(exigir_papel("solicitante", "admin"))):

    if dados.estado not in ESTADOS:
        raise HTTPException(status_code=400, detail="Estado deve ser SP ou RJ")

    if not dados.terceirizado and (not dados.cpf or dados.data_admissao is None):
        raise HTTPException(status_code=400,
                            detail="CPF e data de admissão são obrigatórios para colaborador Cury")

    colaborador = salvar(dados, int(usuario_id), db)
    return {"mensagem": "Solicitação registrada. O robô vai processar em breve.",
            "id": colaborador.id}


@router.get("/colaborador/pendentes")
def pendentes(db: Session = Depends(get_db),
              papel: str = Depends(exigir_papel("admin"))):
    """O robô Java consome esta rota para saber o que cadastrar."""
    return [_para_dict(c) for c in listar_por_status("pendente", db)]


@router.get("/colaborador/meus")
def meus(db: Session = Depends(get_db),
         usuario_id: str = Depends(usuario_atual)):
    return [_para_dict(c) for c in listar_do_solicitante(int(usuario_id), db)]


@router.patch("/colaborador/{colaborador_id}/status")
def mudar_status(colaborador_id: int,
                 dados: StatusUpdate,
                 db: Session = Depends(get_db),
                 papel: str = Depends(exigir_papel("admin"))):
    """O robô avisa aqui se deu certo ou não."""
    if dados.status not in STATUS_VALIDOS:
        raise HTTPException(status_code=400,
                            detail=f"Status deve ser um de: {', '.join(STATUS_VALIDOS)}")

    colaborador = atualizar_status(colaborador_id, dados.status, dados.erro, db)
    if colaborador is None:
        raise HTTPException(status_code=404, detail="Colaborador não encontrado")

    return _para_dict(colaborador)