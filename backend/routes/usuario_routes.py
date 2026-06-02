from fastapi import APIRouter
from pydantic import BaseModel
from service.usuario_service import cadastrar_usuario, login

router = APIRouter()

class Usuario_Cadastro(BaseModel):
    nome: str
    email: str
    senha: str

class Usuario_Login(BaseModel):
    email: str
    senha: str

@router.post("/usuario/cadastrar")
def cadastrar(usuario: Usuario_Cadastro):
    return cadastrar_usuario(
        usuario.nome,
        usuario.email,
        usuario.senha
    )

@router.post("/usuario/login")
def fazer_login(usuario: Usuario_Login):
    return login(
        usuario.email,
        usuario.senha
    )