from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Response
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from config.auth import usuario_atual, papel_atual, exigir_papel
from config.connection import get_db
from repository.config_repository import obter_senha_padrao, obter_emails_resumo
from repository.usuario_repository import listar_emails_admins
from repository.colaborador_repository import (
    anexar_observacao,
    salvar,
    listar_por_status,
    listar_por_dia,
    apagar_para_lixeira,
    listar_lixeira,
    restaurar_da_lixeira,
    apagar_definitivo,
    listar_do_solicitante,
    listar_todos,
    buscar_por_id,
    buscar_email_do_solicitante,
    atualizar_status,
    atualizar_decisao,
    existe_email,
    existe_cpf,
    editar_e_reenviar,
)
from service.email_service import (
    avisar_recusa,
    avisar_cadastro_concluido,
    avisar_erro_no_robo,
    avisar_colaborador_aprovado,
    avisar_colaborador_vinculado,
)

router = APIRouter()

ESTADOS = ["SP", "RJ"]
STATUS_DO_ROBO = ["processando", "cadastrado", "vinculado", "erro"]
STATUS_VALIDOS = ["pendente", "aprovado", "processando", "cadastrado", "vinculado", "erro", "recusado"]

PERFIS = [
    "Equipe de Apoio - CIVIL",
    "Equipe de Apoio - INSTALL",
    "Equipe de Apoio - Engenheiro",
    "Almoxarifado",
    "Operacional",
    "Gerencial",
    "Portaria",
]

class ColaboradorCadastro(BaseModel):
    nome: str
    email: EmailStr
    funcao: Optional[str] = None
    estado: str
    obras: List[str]
    observacao: Optional[str] = None
    terceirizado: bool = False
    cpf: Optional[str] = None
    ja_tem_acesso: bool = False
    desvincular_anterior: Optional[bool] = None
    setor: Optional[str] = None

class StatusUpdate(BaseModel):
    status: str
    erro: Optional[str] = None
    observacao: Optional[str] = None


class PrioridadeUpdate(BaseModel):
    prioridade: str

class Recusa(BaseModel):
    motivo: str


class Exclusao(BaseModel):
    motivo: str


class Aprovacao(BaseModel):
    perfil: str

def _para_dict(colaborador):
    return {
        "id": colaborador.id,
        "nome": colaborador.nome,
        "email": colaborador.email,
        "funcao": colaborador.funcao,
        "estado": colaborador.estado,
        "obra": colaborador.obra,
        "obras": colaborador.obra.split(" ; ") if colaborador.obra else [],
        "observacao": colaborador.observacao,
        "ja_tem_acesso": colaborador.ja_tem_acesso,
        "desvincular_anterior": colaborador.desvincular_anterior,
        "perfil": colaborador.perfil,
        "setor": colaborador.setor,
        "prioridade": getattr(colaborador, "prioridade", "normal") or "normal",
        "cobrado_em": colaborador.cobrado_em.isoformat() if colaborador.cobrado_em else None,
        "criado_em": colaborador.criado_em.isoformat() if colaborador.criado_em else None,
        "terceirizado": colaborador.terceirizado,
        "cpf": colaborador.cpf,
        "status": colaborador.status,
        "motivo": colaborador.motivo,
        "erro": colaborador.erro,
        "solicitante": getattr(colaborador, "solicitante_nome", None),
        "email_repetido": getattr(colaborador, "email_repetido", False),
        "cpf_repetido": getattr(colaborador, "cpf_repetido", False),
    }


@router.post("/colaborador/cadastrar")
def cadastrar(dados: ColaboradorCadastro,
              db: Session = Depends(get_db),
              usuario_id: str = Depends(usuario_atual),
              papel: str = Depends(exigir_papel("solicitante", "admin"))):

    if dados.estado not in ESTADOS:
        raise HTTPException(status_code=400, detail="Estado deve ser SP ou RJ")

    if not dados.obras:
        raise HTTPException(status_code=400, detail="Escolha ao menos uma obra.")

    if dados.ja_tem_acesso and dados.desvincular_anterior is None:
        raise HTTPException(status_code=400,
                            detail="Diga se e para desvincular da filial anterior ou manter o vinculo.")

    if not dados.ja_tem_acesso:
        if not dados.funcao:
            raise HTTPException(status_code=400, detail="Informe a função.")
        if not dados.terceirizado and not dados.cpf:
            raise HTTPException(status_code=400,
                                detail="CPF é obrigatório para colaborador Cury")

    if not dados.ja_tem_acesso:
        if existe_email(dados.email, db):
            raise HTTPException(status_code=400,
                                detail="Já existe uma solicitação com esse e-mail.")
        if dados.cpf and existe_cpf(dados.cpf, db):
            raise HTTPException(status_code=400,
                                detail="Já existe uma solicitação com esse CPF.")

    obra_texto = " ; ".join(dados.obras)
    colaborador = salvar(dados, obra_texto, int(usuario_id), db)

    if dados.ja_tem_acesso:
        from repository.colaborador_repository import atualizar_status
        atualizar_status(colaborador.id, "cadastrado", None, db)
    return {"mensagem": "Solicitação enviada para aprovação.", "id": colaborador.id}


@router.get("/colaborador/checar")
def checar(email: str = "", cpf: str = "",
           db: Session = Depends(get_db),
           papel: str = Depends(exigir_papel("solicitante", "admin"))):
    return {
        "email_repetido": existe_email(email, db),
        "cpf_repetido": existe_cpf(cpf, db),
    }


@router.get("/colaborador/meus")
def meus(db: Session = Depends(get_db),
         usuario_id: str = Depends(usuario_atual),
         papel: str = Depends(papel_atual)):
    if papel == "admin":
        todos = listar_todos(db)
        for c in todos:
            if c.status == "pendente":
                c.email_repetido = existe_email(c.email, db, ignorar_id=c.id)
                c.cpf_repetido = (not c.terceirizado) and existe_cpf(c.cpf, db, ignorar_id=c.id)
        return [_para_dict(c) for c in todos]
    return [_para_dict(c) for c in listar_do_solicitante(int(usuario_id), db)]


@router.patch("/colaborador/{colaborador_id}/editar")
def editar(colaborador_id: int,
           dados: ColaboradorCadastro,
           db: Session = Depends(get_db),
           usuario_id: str = Depends(usuario_atual),
           papel: str = Depends(exigir_papel("solicitante", "admin"))):
    if dados.estado not in ESTADOS:
        raise HTTPException(status_code=400, detail="Estado deve ser SP ou RJ")
    if not dados.obras:
        raise HTTPException(status_code=400, detail="Escolha ao menos uma obra.")

    if dados.ja_tem_acesso and dados.desvincular_anterior is None:
        raise HTTPException(status_code=400,
                            detail="Diga se e para desvincular da filial anterior ou manter o vinculo.")

    if not dados.ja_tem_acesso:
        if not dados.funcao:
            raise HTTPException(status_code=400, detail="Informe a função.")
        if not dados.terceirizado and not dados.cpf:
            raise HTTPException(status_code=400, detail="CPF é obrigatório para colaborador Cury")

    obra_texto = " ; ".join(dados.obras)
    resultado = editar_e_reenviar(colaborador_id, dados, obra_texto, int(usuario_id), db, eh_admin=(papel == "admin"))

    if resultado == "nao_encontrado":
        raise HTTPException(status_code=404, detail="Solicitação não encontrada")
    if resultado == "nao_e_seu":
        raise HTTPException(status_code=403, detail="Você só pode editar as suas solicitações.")
    if resultado == "nao_recusado":
        raise HTTPException(status_code=400, detail="Só dá para editar uma solicitação recusada.")

    return {"mensagem": "Solicitação corrigida e reenviada para aprovação.", "id": resultado.id}


@router.patch("/colaborador/{colaborador_id}/aprovar")
def aprovar(colaborador_id: int,
            dados: Aprovacao,
            tarefas: BackgroundTasks,
            db: Session = Depends(get_db),
            papel: str = Depends(exigir_papel("admin"))):
    if dados.perfil not in PERFIS:
        raise HTTPException(status_code=400,
                            detail=f"Perfil inválido. Escolha um de: {', '.join(PERFIS)}")

    colaborador = buscar_por_id(colaborador_id, db)
    if colaborador is None:
        raise HTTPException(status_code=404, detail="Solicitação não encontrada")

    if colaborador.status != "pendente":
        raise HTTPException(status_code=400,
                            detail=f"Só dá para aprovar quem está pendente (está '{colaborador.status}').")

    colaborador.perfil = dados.perfil
    db.commit()
    colaborador = atualizar_decisao(colaborador_id, "aprovado", None, db)

    email_solicitante = buscar_email_do_solicitante(colaborador.solicitante_id, db)
    tarefas.add_task(avisar_colaborador_aprovado, email_solicitante, colaborador.nome,
                     copias=listar_emails_admins(db, excluir=email_solicitante))

    return _para_dict(colaborador)

@router.patch("/colaborador/{colaborador_id}/recusar")
def recusar(colaborador_id: int,
            dados: Recusa,
            tarefas: BackgroundTasks,
            db: Session = Depends(get_db),
            papel: str = Depends(exigir_papel("admin"))):
    if not dados.motivo.strip():
        raise HTTPException(status_code=400, detail="Explique o motivo da recusa.")

    colaborador = buscar_por_id(colaborador_id, db)
    if colaborador is None:
        raise HTTPException(status_code=404, detail="Solicitação não encontrada")

    if colaborador.status != "pendente":
        raise HTTPException(status_code=400,
                            detail=f"Só dá para recusar quem está pendente (está '{colaborador.status}').")

    colaborador = atualizar_decisao(colaborador_id, "recusado", dados.motivo.strip(), db)

    email_solicitante = buscar_email_do_solicitante(colaborador.solicitante_id, db)
    tarefas.add_task(avisar_recusa, email_solicitante, colaborador.nome, colaborador.motivo)

    return _para_dict(colaborador)

@router.get("/colaborador/pendentes")
def pendentes(db: Session = Depends(get_db),
              papel: str = Depends(exigir_papel("admin"))):
    senha = obter_senha_padrao(db)
    fila = []
    for c in listar_por_status("aprovado", db):
        d = _para_dict(c)
        d["senha_padrao"] = senha
        fila.append(d)
    return fila


@router.get("/colaborador/para-vincular")
def para_vincular(db: Session = Depends(get_db),
                  papel: str = Depends(exigir_papel("admin"))):
    senha = obter_senha_padrao(db)
    fila = []
    for c in listar_por_status("cadastrado", db):
        d = _para_dict(c)
        d["senha_padrao"] = senha
        fila.append(d)
    return fila


@router.patch("/colaborador/{colaborador_id}/status")
def mudar_status(colaborador_id: int,
                 dados: StatusUpdate,
                 tarefas: BackgroundTasks,
                 db: Session = Depends(get_db),
                 papel: str = Depends(exigir_papel("admin"))):
    if dados.status not in STATUS_VALIDOS:
        raise HTTPException(status_code=400,
                            detail=f"Status deve ser um de: {', '.join(STATUS_VALIDOS)}")

    colaborador = atualizar_status(colaborador_id, dados.status, dados.erro, db,
                                   observacao=dados.observacao)
    if colaborador is None:
        raise HTTPException(status_code=404, detail="Colaborador não encontrado")

    if dados.status in ("cadastrado", "vinculado") and not colaborador.ja_tem_acesso:
        anexar_observacao(colaborador, f"Senha inicial: {obter_senha_padrao(db)}")
        db.commit()
        db.refresh(colaborador)

    if dados.status == "vinculado":
        email_solicitante = buscar_email_do_solicitante(colaborador.solicitante_id, db)

        if not colaborador.ja_tem_acesso:
            tarefas.add_task(avisar_cadastro_concluido, colaborador.email,
                             colaborador.nome, obter_senha_padrao(db),
                             copias_ocultas=obter_emails_resumo(db))

        tarefas.add_task(avisar_colaborador_vinculado, email_solicitante, colaborador.nome,
                         colaborador.obra, bool(colaborador.ja_tem_acesso))

    if dados.status == "erro":
        email_solicitante = buscar_email_do_solicitante(colaborador.solicitante_id, db)
        tarefas.add_task(avisar_erro_no_robo, email_solicitante, colaborador.nome, dados.erro)

    return _para_dict(colaborador)


@router.patch("/colaborador/{colaborador_id}/prioridade")
def mudar_prioridade(colaborador_id: int,
                     dados: PrioridadeUpdate,
                     db: Session = Depends(get_db),
                     papel: str = Depends(exigir_papel("solicitante", "admin"))):
    valor = (dados.prioridade or "normal").strip().lower()
    if valor not in ("normal", "urgente"):
        raise HTTPException(status_code=400, detail="Prioridade deve ser 'normal' ou 'urgente'")
    colaborador = buscar_por_id(colaborador_id, db)
    if colaborador is None:
        raise HTTPException(status_code=404, detail="Colaborador não encontrado")
    colaborador.prioridade = valor
    db.commit()
    db.refresh(colaborador)
    return _para_dict(colaborador)


@router.get("/colaborador/relatorio")
def relatorio(data: str = "",
              db: Session = Depends(get_db),
              papel: str = Depends(exigir_papel("admin"))):
    from datetime import datetime, timedelta

    try:
        if data:
            inicio = datetime.strptime(data, "%Y-%m-%d")
        else:
            agora = datetime.now()
            inicio = datetime(agora.year, agora.month, agora.day)
    except ValueError:
        raise HTTPException(status_code=400, detail="Data invalida. Use AAAA-MM-DD.")

    fim = inicio + timedelta(days=1)
    registros = listar_por_dia(inicio, fim, db)

    linhas = ["DATA/HORA;NOME;EMAIL;CPF;FUNCAO;PERFIL;OBRAS;STATUS;MOTIVO;ERRO"]
    for c in registros:
        campos = [
            c.criado_em.strftime("%d/%m/%Y %H:%M") if c.criado_em else "",
            c.nome or "",
            c.email or "",
            c.cpf or "",
            c.funcao or "",
            c.perfil or "",
            (c.obra or "").replace(";", ","),
            c.status or "",
            (c.motivo or "").replace(";", ",").replace("\n", " "),
            (c.erro or "").replace(";", ",").replace("\n", " "),
        ]
        linhas.append(";".join(campos))

    conteudo = "\ufeff" + "\n".join(linhas)
    nome_arquivo = f"relatorio_{inicio.strftime('%Y-%m-%d')}.csv"
    return Response(
        content=conteudo,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{nome_arquivo}"'},
    )


@router.patch("/colaborador/{colaborador_id}/reenviar")
def reenviar(colaborador_id: int,
             db: Session = Depends(get_db),
             papel: str = Depends(exigir_papel("admin"))):
    colaborador = buscar_por_id(colaborador_id, db)
    if colaborador is None:
        raise HTTPException(status_code=404, detail="Solicitação não encontrada")
    if colaborador.status != "erro":
        raise HTTPException(status_code=400,
                            detail=f"Só dá para reenviar quem está com erro (está '{colaborador.status}').")
    if not colaborador.perfil:
        raise HTTPException(status_code=400,
                            detail="Sem perfil definido. Edite e escolha o perfil antes de reenviar.")

    colaborador.status = "aprovado"
    colaborador.erro = None
    db.commit()
    return _para_dict(colaborador)


@router.patch("/colaborador/{colaborador_id}/apagar")
def apagar(colaborador_id: int,
           dados: Exclusao,
           db: Session = Depends(get_db),
           usuario_id: str = Depends(usuario_atual),
           papel: str = Depends(exigir_papel("solicitante", "admin"))):
    if not dados.motivo or not dados.motivo.strip():
        raise HTTPException(status_code=400, detail="Informe o motivo da exclusao.")

    alvo = buscar_por_id(colaborador_id, db)
    if alvo is None:
        raise HTTPException(status_code=404, detail="Solicitacao nao encontrada")

    if papel != "admin":
        if alvo.solicitante_id != int(usuario_id):
            raise HTTPException(status_code=403, detail="Você só pode apagar as suas solicitações.")
        if alvo.status not in ("pendente", "recusado"):
            raise HTTPException(status_code=400,
                                detail="Só dá para apagar antes da aprovação. Peça ao admin.")

    c = apagar_para_lixeira(colaborador_id, dados.motivo.strip(), db)
    return _para_dict(c)


@router.get("/colaborador/lixeira")
def lixeira(db: Session = Depends(get_db),
            usuario_id: str = Depends(usuario_atual),
            papel: str = Depends(exigir_papel("solicitante", "admin"))):
    filtro_solicitante = None if papel == "admin" else int(usuario_id)
    itens = listar_lixeira(db, filtro_solicitante)
    saida = []
    for c in itens:
        d = _para_dict(c)
        d["solicitante"] = getattr(c, "solicitante_nome", None)
        d["motivo_exclusao"] = c.motivo_exclusao
        saida.append(d)
    return saida


@router.patch("/colaborador/{colaborador_id}/restaurar")
def restaurar(colaborador_id: int,
              db: Session = Depends(get_db),
              papel: str = Depends(exigir_papel("admin"))):
    c = restaurar_da_lixeira(colaborador_id, db)
    if c is None:
        raise HTTPException(status_code=404, detail="Solicitacao nao encontrada")
    return _para_dict(c)


@router.delete("/colaborador/{colaborador_id}/definitivo")
def definitivo(colaborador_id: int,
               db: Session = Depends(get_db),
               papel: str = Depends(exigir_papel("admin"))):
    ok = apagar_definitivo(colaborador_id, db)
    if ok is None:
        raise HTTPException(status_code=404, detail="Solicitacao nao encontrada")
    return {"mensagem": "Apagado definitivamente."}


@router.patch("/colaborador/{colaborador_id}/cobrar")
def cobrar_colaborador(colaborador_id: int,
                       db: Session = Depends(get_db),
                       papel: str = Depends(exigir_papel("solicitante", "admin"))):
    colaborador = buscar_por_id(colaborador_id, db)
    if colaborador is None:
        raise HTTPException(status_code=404, detail="Solicitação não encontrada")

    if colaborador.status not in ("pendente", "aprovado", "processando", "cadastrado", "erro"):
        raise HTTPException(status_code=400,
                            detail=f"Nao da para cobrar algo que ja esta '{colaborador.status}'.")

    agora = datetime.now()
    if colaborador.cobrado_em and (agora - colaborador.cobrado_em) < timedelta(hours=24):
        faltam = timedelta(hours=24) - (agora - colaborador.cobrado_em)
        horas = max(int(faltam.total_seconds() // 3600), 1)
        raise HTTPException(status_code=429,
                            detail=f"Ja cobrado hoje. Pode cobrar de novo em {horas}h.")

    colaborador.cobrado_em = agora
    db.commit()
    db.refresh(colaborador)
    return _para_dict(colaborador)