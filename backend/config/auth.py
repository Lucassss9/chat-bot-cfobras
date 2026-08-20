import os
import jwt
from datetime import datetime, timezone
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from config.connection import get_db
from repository.usuario_repository import buscar_usuario_por_id

SECRET = os.getenv("JWT_KEY")
ALGORITMO = os.getenv("ALGORITHM")

pegar_token = OAuth2PasswordBearer(tokenUrl="token")


def _decodificar(token):
    try:
        return jwt.decode(token, SECRET, algorithms=[ALGORITMO])
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token invalido")


def usuario_atual(token: str = Depends(pegar_token), db: Session = Depends(get_db)):
    dados = _decodificar(token)
    _conferir_sessao(dados, db)
    return dados["sub"]


def _conferir_sessao(dados, db):
    usuario = buscar_usuario_por_id(dados.get("sub"), db)

    if usuario is None or not usuario.ativo:
        raise HTTPException(status_code=401, detail="Sessao encerrada. Faca login novamente.")

    if usuario.senha_alterada_em is None:
        return usuario

    emitido_em = dados.get("iat")
    if emitido_em is None:
        raise HTTPException(status_code=401, detail="Sua senha foi alterada. Faca login novamente.")

    alterada = usuario.senha_alterada_em
    if alterada.tzinfo is None:
        alterada = alterada.replace(tzinfo=timezone.utc)

    if datetime.fromtimestamp(emitido_em, tz=timezone.utc) < alterada:
        raise HTTPException(status_code=401, detail="Sua senha foi alterada. Faca login novamente.")

    return usuario


def papel_atual(token: str = Depends(pegar_token), db: Session = Depends(get_db)):
    dados = _decodificar(token)
    usuario = _conferir_sessao(dados, db)
    return usuario.papel


def exigir_papel(*papeis_permitidos):

    def verificar(papel: str = Depends(papel_atual)):
        if papel not in papeis_permitidos:
            raise HTTPException(status_code=403, detail="Você não tem permissão para isso.")
        return papel

    return verificar