from fastapi import APIRouter
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
    return cadastrar_usuario(
        usuario.nome,
        usuario.email,
        usuario.senha
    )

@router.post("/usuario/login")
def fazer_login(usuario: UsuarioLogin):
    return login(
        usuario.email,
        usuario.senha
    )