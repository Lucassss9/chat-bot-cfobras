import os
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

SECRET = os.getenv("JWT_KEY")
ALGORITMO = os.getenv("ALGORITHM")

pegar_token = OAuth2PasswordBearer(tokenUrl="token")


def _decodificar(token):
    try:
        return jwt.decode(token, SECRET, algorithms=[ALGORITMO])
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token invalido")


def usuario_atual(token: str = Depends(pegar_token)):
    return _decodificar(token)["sub"]


def papel_atual(token: str = Depends(pegar_token)):
    return _decodificar(token).get("papel", "comum")


def exigir_papel(*papeis_permitidos):
    """Uso: Depends(exigir_papel("admin")) — barra quem não tem o papel."""

    def verificar(papel: str = Depends(papel_atual)):
        if papel not in papeis_permitidos:
            raise HTTPException(status_code=403, detail="Você não tem permissão para isso.")
        return papel

    return verificar