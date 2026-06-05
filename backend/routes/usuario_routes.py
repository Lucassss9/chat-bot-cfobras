from fastapi import APIRouter, HTTPException, Depends
from exception.usuario_exception import UsuarioJaExisteError, CredenciaisInvalidasError, DadosInvalidoError
from pydantic import BaseModel, EmailStr
from service.usuario_service import cadastrar_usuario, login
from config.connection import get_db
from sqlalchemy.orm import Session

router = APIRouter()

class UsuarioCadastro(BaseModel):
    nome: str
    email: EmailStr
    senha: str

class UsuarioLogin(BaseModel):
    email: EmailStr
    senha: str

@router.post("/usuario/cadastrar")
def cadastrar(usuario: UsuarioCadastro, db: Session = Depends(get_db)):
    try:
        return cadastrar_usuario(usuario.nome, usuario.email, usuario.senha, db)
    except UsuarioJaExisteError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except DadosInvalidoError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/usuario/login")
def fazer_login(usuario: UsuarioLogin, db: Session = Depends(get_db)):
    try:
        return login(usuario.email, usuario.senha, db)
    except DadosInvalidoError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except CredenciaisInvalidasError as e:
        raise HTTPException(status_code=401, detail=str(e))