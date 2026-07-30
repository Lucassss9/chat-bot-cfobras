from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from config.auth import exigir_papel
from config.connection import get_db
from repository.filial_repository import (
    listar_todas,
    listar_por_estado,
    criar,
    atualizar,
    apagar,
    existe,
)

router = APIRouter()


class FilialEntrada(BaseModel):
    nome: str
    estado: str


def _para_dict(f):
    return {"id": f.id, "nome": f.nome, "estado": f.estado}


@router.get("/filial")
def listar(estado: str = None,
           db: Session = Depends(get_db),
           papel: str = Depends(exigir_papel("solicitante", "admin"))):
    filiais = listar_por_estado(estado, db) if estado else listar_todas(db)
    return [_para_dict(f) for f in filiais]


@router.post("/filial")
def adicionar(dados: FilialEntrada,
              db: Session = Depends(get_db),
              papel: str = Depends(exigir_papel("admin"))):
    nome = (dados.nome or "").strip()
    estado = (dados.estado or "").strip().upper()
    if not nome:
        raise HTTPException(status_code=400, detail="Informe o nome da filial.")
    if not estado:
        raise HTTPException(status_code=400, detail="Informe o estado.")
    if existe(nome, estado, db):
        raise HTTPException(status_code=400, detail="Essa filial já existe nesse estado.")
    f = criar(nome, estado, db)
    return _para_dict(f)


@router.patch("/filial/{filial_id}")
def editar(filial_id: int,
           dados: FilialEntrada,
           db: Session = Depends(get_db),
           papel: str = Depends(exigir_papel("admin"))):
    nome = (dados.nome or "").strip()
    estado = (dados.estado or "").strip().upper()
    if not nome:
        raise HTTPException(status_code=400, detail="Informe o nome da filial.")
    if not estado:
        raise HTTPException(status_code=400, detail="Informe o estado.")
    f = atualizar(filial_id, nome, estado, db)
    if f is None:
        raise HTTPException(status_code=404, detail="Filial não encontrada.")
    return _para_dict(f)


@router.delete("/filial/{filial_id}")
def remover(filial_id: int,
            db: Session = Depends(get_db),
            papel: str = Depends(exigir_papel("admin"))):
    ok = apagar(filial_id, db)
    if ok is None:
        raise HTTPException(status_code=404, detail="Filial não encontrada.")
    return {"mensagem": "Filial apagada."}