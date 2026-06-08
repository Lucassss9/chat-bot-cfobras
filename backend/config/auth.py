import os
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

SECRET = os.getenv("JWT_KEY")
ALGORITMO = os.getenv("ALGORITHM")

pegar_token = OAuth2PasswordBearer(tokenUrl="token")

def usuario_atual(token: str = Depends(pegar_token)):
    try:
        dados = jwt.decode(token, SECRET, algorithms=[ALGORITMO])
        return dados["sub"]
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token invalido")