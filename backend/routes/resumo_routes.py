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


def _total(grupos):
    return sum(len(lista) for par in grupos.values() for lista in par)


def _dias_esperando(criado_em):
    if not criado_em:
        return 0
    return max((datetime.now() - criado_em).days, 0)


def _ordenar(itens):
    return sorted(itens, key=lambda i: (i.get("cobrado_dias") is None,
                                        i["prioridade"] != "urgente",
                                        -i["dias"]))


ESPERANDO_VOCE = ["pendente"]
ESPERANDO_ROBO = ["aprovado", "processando", "cadastrado", "erro"]


def _item(titulo, solicitante_id, prioridade, criado_em, cobrado_em, status, nomes):
    return {
        "titulo": titulo,
        "solicitante": nomes.get(solicitante_id),
        "prioridade": (prioridade or "normal"),
        "status": status,
        "dias": _dias_esperando(criado_em),
        "cobrado_dias": _dias_esperando(cobrado_em) if cobrado_em else None,
    }


def _levantar(db, status_alvo):
    nomes = {u.id: u.nome for u in db.query(Usuario).all()}

    colaboradores = _ordenar([
        _item(c.nome, c.solicitante_id, c.prioridade, c.criado_em,
              getattr(c, "cobrado_em", None), c.status, nomes)
        for c in db.query(Colaborador).filter(Colaborador.status.in_(status_alvo)).all()
    ])

    obras = _ordenar([
        _item(o.obra_nome, o.solicitante_id, getattr(o, "prioridade", "normal"),
              o.criado_em, getattr(o, "cobrado_em", None), o.status, nomes)
        for o in db.query(SolicitacaoObra)
        .filter(SolicitacaoObra.status.in_(status_alvo))
        .filter(SolicitacaoObra.apagada.is_(False))
        .all()
    ])

    return colaboradores, obras


def _levantar_pendencias(db):
    return {
        "esperando_voce": _levantar(db, ESPERANDO_VOCE),
        "esperando_robo": _levantar(db, ESPERANDO_ROBO),
    }


@router.get("/resumo/pendentes")
def ver_pendentes(db: Session = Depends(get_db),
                  papel: str = Depends(exigir_papel("admin"))):
    grupos = _levantar_pendencias(db)
    return {
        "destinatario": _destinatarios(db),
        "esperando_voce": {"colaboradores": grupos["esperando_voce"][0],
                           "obras": grupos["esperando_voce"][1]},
        "esperando_robo": {"colaboradores": grupos["esperando_robo"][0],
                           "obras": grupos["esperando_robo"][1]},
        "total": _total(grupos),
    }


@router.post("/resumo/pendentes/enviar")
def enviar_pendentes(tarefas: BackgroundTasks,
                     db: Session = Depends(get_db),
                     papel: str = Depends(exigir_papel("admin"))):
    """Envio manual, pelo botao do painel."""
    grupos = _levantar_pendencias(db)
    destinos = _destinatarios(db)
    tarefas.add_task(avisar_pendentes, destinos, grupos)
    return {"enviado_para": destinos, "total": _total(grupos)}


@router.post("/resumo/pendentes/agendado")
def enviar_pendentes_agendado(tarefas: BackgroundTasks,
                              db: Session = Depends(get_db),
                              x_chave_resumo: str = Header(default="")):

    if not CHAVE_RESUMO:
        raise HTTPException(status_code=503, detail="Envio agendado nao configurado.")

    if x_chave_resumo != CHAVE_RESUMO:
        raise HTTPException(status_code=401, detail="Chave invalida.")

    grupos = _levantar_pendencias(db)

    if _total(grupos) == 0:
        return {"enviado": False, "motivo": "nada pendente"}

    tarefas.add_task(avisar_pendentes, _destinatarios(db), grupos)
    return {"enviado": True, "total": _total(grupos)}