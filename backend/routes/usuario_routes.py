from fastapi import APIRouter, HTTPException
from exception.usuario_exception import UsuarioJaExisteError, CredenciaisInvalidasError, DadosInvalidoError
from pydantic import BaseModel
from service.usuario_service import cadastrar_usuario, login

router = APIRouter()

class UsuarioCadastro(BaseModel):
    nome: str
    email: str
    senha: str

class UsuarioLogin(BaseModel):
    email: str
    senha: str

@router.post("/usuario/cadastrar")
def cadastrar(usuario: UsuarioCadastro):
    try:
        return cadastrar_usuario(
            usuario.nome,
            usuario.email,
            usuario.senha
        )
    except UsuarioJaExisteError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except DadosInvalidoError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/usuario/login")
def fazer_login(usuario: UsuarioLogin):
    try:
        return login(
            usuario.email,
            usuario.senha
        )
    except DadosInvalidoError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except CredenciaisInvalidasError as e:
        raise HTTPException(status_code=401, detail=str(e))