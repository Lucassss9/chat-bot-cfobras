from fastapi import APIRouter
from pydantic import BaseModel
from service.usuario_service import cadastrar_usuario

router = APIRouter()

class Usuario(BaseModel):
    nome: str
    email: str
    senha: str

@router.post("/usuario/cadastrar")
def cadastrar(usuario: Usuario):
    return cadastrar_usuario(
        usuario.nome,
        usuario.email,
        usuario.senha
    )
