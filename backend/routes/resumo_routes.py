import os
from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from config.connection import get_db
from config.auth import exigir_papel
from model.colaborador_model import Colaborador
from model.obra_model import SolicitacaoObra
from model.usuario_model import Usuario
from repository.config_repository import obter_emails_resumo
from service.email_service import avisar_pendentes, EMAIL_RESUMO

router = APIRouter()

CHAVE_RESUMO = os.getenv("CHAVE_RESUMO")


def _destinatarios(db):
    emails = obter_emails_resumo(db)
    return ",".join(emails) if emails else EMAIL_RESUMO


def _dias_esperando(criado_em):
    if not criado_em:
        return 0
    return max((datetime.now() - criado_em).days, 0)


def _ordenar(itens):
    return sorted(itens, key=lambda i: (i["prioridade"] != "urgente", -i["dias"]))


def _levantar_pendencias(db):
    nomes = {u.id: u.nome for u in db.query(Usuario).all()}

    colaboradores = _ordenar([
        {
            "titulo": c.nome,
            "solicitante": nomes.get(c.solicitante_id),
            "prioridade": (c.prioridade or "normal"),
            "dias": _dias_esperando(c.criado_em),
        }
        for c in db.query(Colaborador).filter(Colaborador.status == "pendente").all()
    ])

    obras = _ordenar([
        {
            "titulo": o.obra_nome,
            "solicitante": nomes.get(o.solicitante_id),
            "prioridade": (getattr(o, "prioridade", "normal") or "normal"),
            "dias": _dias_esperando(o.criado_em),
        }
        for o in db.query(SolicitacaoObra)
        .filter(SolicitacaoObra.status == "pendente")
        .filter(SolicitacaoObra.apagada.is_(False))
        .all()
    ])

    return colaboradores, obras


@router.get("/resumo/pendentes")
def ver_pendentes(db: Session = Depends(get_db),
                  papel: str = Depends(exigir_papel("admin"))):
    colaboradores, obras = _levantar_pendencias(db)
    return {
        "destinatario": _destinatarios(db),
        "colaboradores": colaboradores,
        "obras": obras,
        "total": len(colaboradores) + len(obras),
    }


@router.post("/resumo/pendentes/enviar")
def enviar_pendentes(tarefas: BackgroundTasks,
                     db: Session = Depends(get_db),
                     papel: str = Depends(exigir_papel("admin"))):
    """Envio manual, pelo botao do painel."""
    colaboradores, obras = _levantar_pendencias(db)
    destinos = _destinatarios(db)
    tarefas.add_task(avisar_pendentes, destinos, colaboradores, obras)
    return {"enviado_para": destinos, "total": len(colaboradores) + len(obras)}


@router.post("/resumo/pendentes/agendado")
def enviar_pendentes_agendado(tarefas: BackgroundTasks,
                              db: Session = Depends(get_db),
                              x_chave_resumo: str = Header(default="")):

    if not CHAVE_RESUMO:
        raise HTTPException(status_code=503, detail="Envio agendado nao configurado.")

    if x_chave_resumo != CHAVE_RESUMO:
        raise HTTPException(status_code=401, detail="Chave invalida.")

    colaboradores, obras = _levantar_pendencias(db)

    if not colaboradores and not obras:
        return {"enviado": False, "motivo": "nada pendente"}

    tarefas.add_task(avisar_pendentes, _destinatarios(db), colaboradores, obras)
    return {"enviado": True, "total": len(colaboradores) + len(obras)}