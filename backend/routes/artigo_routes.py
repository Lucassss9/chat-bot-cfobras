from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from config.auth import exigir_papel, usuario_atual
from config.connection import get_db
from repository.artigo_repository import (
    listar_todos, listar_destaques, buscar_por_id, criar, atualizar, apagar,
)

router = APIRouter()


class ArtigoEntrada(BaseModel):
    grupo: str
    pergunta: str
    resposta: str
    caminho: Optional[str] = None
    variacoes: Optional[str] = None
    destaque: bool = False
    ordem: int = 0


class ArtigoEdicao(BaseModel):
    grupo: Optional[str] = None
    pergunta: Optional[str] = None
    resposta: Optional[str] = None
    caminho: Optional[str] = None
    variacoes: Optional[str] = None
    ativo: Optional[bool] = None
    destaque: Optional[bool] = None
    ordem: Optional[int] = None


def _para_dict(a):
    return {
        "id": a.id,
        "grupo": a.grupo,
        "pergunta": a.pergunta,
        "caminho": a.caminho,
        "resposta": a.resposta,
        "variacoes": a.variacoes,
        "ativo": a.ativo,
        "destaque": a.destaque,
        "ordem": a.ordem,
        "atualizado_em": a.atualizado_em.isoformat() if a.atualizado_em else None,
    }


@router.get("/artigo/destaques")
def destaques(db: Session = Depends(get_db),
              usuario_id: str = Depends(usuario_atual)):

    return [{"id": a.id, "grupo": a.grupo, "pergunta": a.pergunta,
             "caminho": a.caminho}
            for a in listar_destaques(db)]


@router.get("/artigo")
def listar(db: Session = Depends(get_db),
           papel: str = Depends(exigir_papel("admin"))):
    return [_para_dict(a) for a in listar_todos(db)]


@router.post("/artigo")
def novo(dados: ArtigoEntrada,
         db: Session = Depends(get_db),
         papel: str = Depends(exigir_papel("admin"))):
    if not dados.pergunta.strip() or not dados.resposta.strip():
        raise HTTPException(status_code=400, detail="Pergunta e resposta são obrigatórias.")

    artigo = criar(dados.grupo.strip(), dados.pergunta.strip(),
                   (dados.caminho or "").strip() or None,
                   dados.resposta.strip(), db,
                   variacoes=(dados.variacoes or "").strip() or None,
                   destaque=dados.destaque, ordem=dados.ordem)
    return _para_dict(artigo)


@router.put("/artigo/{artigo_id}")
def editar(artigo_id: int,
           dados: ArtigoEdicao,
           db: Session = Depends(get_db),
           papel: str = Depends(exigir_papel("admin"))):
    artigo = atualizar(artigo_id, dados, db)
    if artigo is None:
        raise HTTPException(status_code=404, detail="Artigo não encontrado")
    return _para_dict(artigo)


@router.delete("/artigo/{artigo_id}")
def remover(artigo_id: int,
            db: Session = Depends(get_db),
            papel: str = Depends(exigir_papel("admin"))):
    if buscar_por_id(artigo_id, db) is None:
        raise HTTPException(status_code=404, detail="Artigo não encontrado")

    apagar(artigo_id, db)
    return {"mensagem": "Artigo apagado."}