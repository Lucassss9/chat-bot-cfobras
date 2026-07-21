import base64
from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Response
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from config.auth import usuario_atual, papel_atual, exigir_papel
from config.connection import get_db
from repository.obra_repository import (
    salvar, buscar_por_id, listar_todas, listar_do_solicitante, atualizar_decisao,
)
from repository.colaborador_repository import buscar_email_do_solicitante
from service.email_service import avisar_recusa

router = APIRouter()


class PessoaEntrada(BaseModel):
    nome: str
    email: EmailStr
    funcao: Optional[str] = None
    tipo: Optional[str] = None
    ja_tem_acesso: bool = False


class ObraEntrada(BaseModel):
    tipo_filial: str = "existente"
    filial_nome: str
    filial_cnpj: Optional[str] = None
    filial_endereco: Optional[str] = None
    filial_cidade: Optional[str] = None
    filial_estado: Optional[str] = None

    obra_nome: str
    obra_codigo: Optional[str] = None
    obra_email: Optional[str] = None
    obra_endereco: Optional[str] = None
    obra_cidade: Optional[str] = None
    obra_estado: Optional[str] = None
    obra_engenheiro: Optional[str] = None
    obra_descricao: Optional[str] = None

    ficha_nome: Optional[str] = None
    ficha_base64: Optional[str] = None

    pessoas: List[PessoaEntrada] = []


class Recusa(BaseModel):
    motivo: str


def _para_dict(s):
    return {
        "id": s.id,
        "tipo_filial": s.tipo_filial,
        "filial_nome": s.filial_nome,
        "filial_cnpj": s.filial_cnpj,
        "filial_endereco": s.filial_endereco,
        "filial_cidade": s.filial_cidade,
        "filial_estado": s.filial_estado,
        "obra_nome": s.obra_nome,
        "obra_codigo": s.obra_codigo,
        "obra_email": s.obra_email,
        "obra_endereco": s.obra_endereco,
        "obra_cidade": s.obra_cidade,
        "obra_estado": s.obra_estado,
        "obra_engenheiro": s.obra_engenheiro,
        "obra_descricao": s.obra_descricao,
        "ficha_nome": s.ficha_nome,
        "tem_ficha": s.ficha_arquivo is not None,
        "status": s.status,
        "motivo": s.motivo,
        "solicitante": getattr(s, "solicitante_nome", None),
        "pessoas": [{
            "nome": p.nome,
            "email": p.email,
            "funcao": p.funcao,
            "tipo": p.tipo,
            "ja_tem_acesso": p.ja_tem_acesso,
        } for p in s.pessoas],
    }


@router.post("/obra/solicitar")
def solicitar(dados: ObraEntrada,
              db: Session = Depends(get_db),
              usuario_id: str = Depends(usuario_atual),
              papel: str = Depends(exigir_papel("solicitante", "admin"))):

    if not dados.pessoas:
        raise HTTPException(status_code=400, detail="Informe ao menos uma pessoa para a obra.")

    if dados.tipo_filial == "nova" and not dados.filial_cnpj:
        raise HTTPException(status_code=400, detail="Filial nova precisa do CNPJ.")

    try:
        solicitacao = salvar(dados, int(usuario_id), db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"mensagem": "Solicitação de obra enviada para aprovação.", "id": solicitacao.id}


@router.get("/obra/minhas")
def minhas(db: Session = Depends(get_db),
           usuario_id: str = Depends(usuario_atual),
           papel: str = Depends(papel_atual)):
    if papel == "admin":
        return [_para_dict(s) for s in listar_todas(db)]
    return [_para_dict(s) for s in listar_do_solicitante(int(usuario_id), db)]


@router.get("/obra/{solicitacao_id}/ficha")
def baixar_ficha(solicitacao_id: int,
                 db: Session = Depends(get_db),
                 papel: str = Depends(exigir_papel("admin"))):
    solicitacao = buscar_por_id(solicitacao_id, db)
    if solicitacao is None or solicitacao.ficha_arquivo is None:
        raise HTTPException(status_code=404, detail="Ficha não encontrada")

    nome = solicitacao.ficha_nome or "ficha.pdf"
    return Response(
        content=solicitacao.ficha_arquivo,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{nome}"'},
    )


@router.patch("/obra/{solicitacao_id}/aprovar")
def aprovar(solicitacao_id: int,
            db: Session = Depends(get_db),
            papel: str = Depends(exigir_papel("admin"))):
    solicitacao = buscar_por_id(solicitacao_id, db)
    if solicitacao is None:
        raise HTTPException(status_code=404, detail="Solicitação não encontrada")
    if solicitacao.status != "pendente":
        raise HTTPException(status_code=400, detail=f"Já está '{solicitacao.status}'.")

    return _para_dict(atualizar_decisao(solicitacao_id, "aprovado", None, db))


@router.patch("/obra/{solicitacao_id}/concluir")
def concluir(solicitacao_id: int,
             db: Session = Depends(get_db),
             papel: str = Depends(exigir_papel("admin"))):
    """Você marca aqui depois de cadastrar a obra no CF Obras."""
    solicitacao = buscar_por_id(solicitacao_id, db)
    if solicitacao is None:
        raise HTTPException(status_code=404, detail="Solicitação não encontrada")

    return _para_dict(atualizar_decisao(solicitacao_id, "concluido", None, db))


@router.patch("/obra/{solicitacao_id}/recusar")
def recusar(solicitacao_id: int,
            dados: Recusa,
            tarefas: BackgroundTasks,
            db: Session = Depends(get_db),
            papel: str = Depends(exigir_papel("admin"))):
    if not dados.motivo.strip():
        raise HTTPException(status_code=400, detail="Explique o motivo da recusa.")

    solicitacao = buscar_por_id(solicitacao_id, db)
    if solicitacao is None:
        raise HTTPException(status_code=404, detail="Solicitação não encontrada")
    if solicitacao.status != "pendente":
        raise HTTPException(status_code=400, detail=f"Já está '{solicitacao.status}'.")

    solicitacao = atualizar_decisao(solicitacao_id, "recusado", dados.motivo.strip(), db)

    email_solicitante = buscar_email_do_solicitante(solicitacao.solicitante_id, db)
    tarefas.add_task(avisar_recusa, email_solicitante,
                     f"obra {solicitacao.obra_nome}", solicitacao.motivo)

    return _para_dict(solicitacao)