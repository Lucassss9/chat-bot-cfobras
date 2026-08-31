from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from config.auth import exigir_papel
from config.connection import get_db
from repository.config_repository import obter_senha_padrao
from service import email_service as es

router = APIRouter()

NOME_FALSO = "Fulano de Teste"
OBRA_FALSA = "CCISA00 - OBRA DE TESTE"


def _amostra_pendentes():
    return (
        [
            {"titulo": "Fulano de Teste", "solicitante": "Beltrano de Teste",
             "prioridade": "urgente", "dias": 6},
            {"titulo": "Sicrano de Teste", "solicitante": "Beltrano de Teste",
             "prioridade": "normal", "dias": 2},
        ],
        [
            {"titulo": OBRA_FALSA, "solicitante": "Beltrano de Teste",
             "prioridade": "urgente", "dias": 11},
        ],
    )


def _montar_envios(db):
    senha = obter_senha_padrao(db)
    colaboradores, obras = _amostra_pendentes()

    return {
        "colaborador_aprovado": (
            "Colaborador aprovado",
            lambda para: es.avisar_colaborador_aprovado(para, NOME_FALSO, teste=True),
        ),
        "colaborador_cadastrado": (
            "Colaborador cadastrado e vinculado (aviso a quem pediu)",
            lambda para: es.avisar_colaborador_vinculado(
                para, NOME_FALSO, "CCISA00 - OBRA DE TESTE", False, teste=True),
        ),
        "colaborador_so_vinculado": (
            "Colaborador so vinculado (aviso a quem pediu)",
            lambda para: es.avisar_colaborador_vinculado(
                para, NOME_FALSO, "CCISA00 - OBRA DE TESTE", True, teste=True),
        ),
        "credenciais": (
            "Acesso criado (vai para a pessoa, com login e senha)",
            lambda para: es.avisar_cadastro_concluido(para, NOME_FALSO, senha, teste=True),
        ),
        "colaborador_recusado": (
            "Colaborador recusado",
            lambda para: es.avisar_recusa(
                para, NOME_FALSO, "Motivo de exemplo: CPF divergente do RH.", teste=True),
        ),
        "erro_robo": (
            "Falha do robo no cadastro",
            lambda para: es.avisar_erro_no_robo(
                para, NOME_FALSO, "Erro de exemplo: campo obrigatorio nao preenchido.",
                teste=True),
        ),
        "obra_aprovada": (
            "Obra aprovada",
            lambda para: es.avisar_obra_aprovada(para, OBRA_FALSA, teste=True),
        ),
        "obra_concluida": (
            "Obra concluida",
            lambda para: es.avisar_obra_concluida(para, OBRA_FALSA, teste=True),
        ),
        "obra_recusada": (
            "Obra recusada",
            lambda para: es.avisar_obra_recusada(
                para, OBRA_FALSA, "Motivo de exemplo: filial incorreta.", teste=True),
        ),
        "resumo_pendentes": (
            "Resumo de solicitacoes em aberto",
            lambda para: es.avisar_pendentes(para, colaboradores, obras, teste=True),
        ),
    }


class EnvioDeTeste(BaseModel):
    destinatario: EmailStr
    tipo: str


@router.get("/teste-email/tipos")
def listar_tipos(db: Session = Depends(get_db),
                 papel: str = Depends(exigir_papel("admin"))):
    envios = _montar_envios(db)
    return {"tipos": [{"id": chave, "nome": nome} for chave, (nome, _) in envios.items()]}


@router.post("/teste-email/enviar")
def enviar_teste(dados: EnvioDeTeste,
                 db: Session = Depends(get_db),
                 papel: str = Depends(exigir_papel("admin"))):
    envios = _montar_envios(db)

    if dados.tipo == "todos":
        resultados = {}
        for chave, (_, enviar) in envios.items():
            resultados[chave] = bool(enviar(str(dados.destinatario)))
        falhas = [c for c, ok in resultados.items() if not ok]
        return {
            "destinatario": dados.destinatario,
            "enviados": len(resultados) - len(falhas),
            "falharam": falhas,
            "resultados": resultados,
        }

    if dados.tipo not in envios:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo invalido. Use 'todos' ou um de: {', '.join(envios)}")

    nome, enviar = envios[dados.tipo]
    if not enviar(str(dados.destinatario)):
        raise HTTPException(
            status_code=502,
            detail="O envio falhou. Confira BREVO_API_KEY e EMAIL_REMETENTE "
                   "e veja o log do servidor.")

    return {"destinatario": dados.destinatario, "tipo": dados.tipo, "nome": nome,
            "enviado": True}