import base64
from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Response
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from config.auth import usuario_atual, papel_atual, exigir_papel
from config.connection import get_db
from repository.obra_repository import (
    salvar, buscar_por_id, listar_todas, listar_do_solicitante, atualizar_decisao,
    editar_e_reenviar,
    criar_colaboradores_da_obra,
)
from repository.colaborador_repository import buscar_email_do_solicitante
from service.email_service import avisar_recusa

router = APIRouter()


class PessoaEntrada(BaseModel):
    nome: str
    email: EmailStr
    funcao: Optional[str] = None
    cpf: Optional[str] = None
    terceirizado: bool = False
    ja_tem_acesso: bool = False
    setor: Optional[str] = None
    observacao: Optional[str] = None


class ObraExtraEntrada(BaseModel):
    obra_nome: str
    obra_codigo: Optional[str] = None
    obra_email: Optional[str] = None
    obra_endereco: Optional[str] = None
    obra_cidade: Optional[str] = None
    obra_estado: Optional[str] = None
    obra_engenheiro: Optional[str] = None
    obra_descricao: Optional[str] = None


class ObraEntrada(BaseModel):
    estado: str = "SP"
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
    obra_cep: Optional[str] = None
    tel_adm: Optional[str] = None
    tel_engenheiro: Optional[str] = None

    ficha_nome: Optional[str] = None
    ficha_base64: Optional[str] = None

    pessoas: List[PessoaEntrada] = []
    obras_extras: List[ObraExtraEntrada] = []


class Recusa(BaseModel):
    motivo: str


def _para_dict(s):
    return {
        "id": s.id,
        "estado": s.estado,
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
        "obra_cep": s.obra_cep,
        "tel_adm": s.tel_adm,
        "tel_engenheiro": s.tel_engenheiro,
        "ficha_nome": s.ficha_nome,
        "tem_ficha": s.ficha_arquivo is not None,
        "status": s.status,
        "motivo": s.motivo,
        "solicitante": getattr(s, "solicitante_nome", None),
        "pessoas": [{
            "nome": p.nome,
            "email": p.email,
            "funcao": p.funcao,
            "cpf": p.cpf,
            "terceirizado": p.terceirizado,
            "ja_tem_acesso": p.ja_tem_acesso,
            "setor": p.setor,
            "observacao": p.observacao,
        } for p in s.pessoas],
        "obras_extras": [{
            "obra_nome": e.obra_nome,
            "obra_codigo": e.obra_codigo,
            "obra_email": e.obra_email,
            "obra_endereco": e.obra_endereco,
            "obra_cidade": e.obra_cidade,
            "obra_estado": e.obra_estado,
            "obra_engenheiro": e.obra_engenheiro,
            "obra_descricao": e.obra_descricao,
        } for e in getattr(s, "obras_extras", [])],
    }


@router.post("/obra/solicitar")
def solicitar(dados: ObraEntrada,
              db: Session = Depends(get_db),
              usuario_id: str = Depends(usuario_atual),
              papel: str = Depends(exigir_papel("solicitante", "admin"))):

    if not dados.pessoas:
        raise HTTPException(status_code=400, detail="Informe ao menos uma pessoa para a obra.")

    if dados.estado not in ["SP", "RJ"]:
        raise HTTPException(status_code=400, detail="Estado deve ser SP ou RJ")

    if dados.tipo_filial == "nova" and not dados.filial_cnpj:
        raise HTTPException(status_code=400, detail="Filial nova precisa do CNPJ.")

    for pessoa in dados.pessoas:
        if not pessoa.ja_tem_acesso and not pessoa.funcao:
            raise HTTPException(
                status_code=400,
                detail=f"{pessoa.nome} não tem acesso ainda — informe a função.")
        if not pessoa.ja_tem_acesso and not pessoa.terceirizado and not pessoa.cpf:
            raise HTTPException(
                status_code=400,
                detail=f"{pessoa.nome} precisa de CPF (ou marque como terceirizado).")

    try:
        solicitacao = salvar(dados, int(usuario_id), db)
        criar_colaboradores_da_obra(solicitacao, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"mensagem": "Solicitação de obra enviada. As pessoas foram para Solicitações de cadastro.",
            "id": solicitacao.id}


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


@router.patch("/obra/{solicitacao_id}/editar")
def editar_obra(solicitacao_id: int,
                dados: ObraEntrada,
                db: Session = Depends(get_db),
                usuario_id: str = Depends(usuario_atual),
                papel: str = Depends(exigir_papel("solicitante", "admin"))):
    resultado = editar_e_reenviar(solicitacao_id, dados, int(usuario_id), db,
                                  eh_admin=(papel == "admin"))
    if resultado == "nao_encontrado":
        raise HTTPException(status_code=404, detail="Solicitação não encontrada")
    if resultado == "nao_e_seu":
        raise HTTPException(status_code=403, detail="Você só pode editar as suas solicitações.")
    if resultado == "nao_recusado":
        raise HTTPException(status_code=400, detail="Só dá para editar uma solicitação recusada.")
    return _para_dict(resultado)


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