from fastapi import APIRouter, HTTPException, Depends
from exception.usuario_exception import UsuarioJaExisteError, CredenciaisInvalidasError, DadosInvalidoError
from pydantic import BaseModel, EmailStr
from service.usuario_service import (
    cadastrar_usuario, login, listar, mudar_papel, mudar_ativo,
    trocar_minha_senha, resetar_senha_de,
)
from config.connection import get_db
from config.auth import exigir_papel, usuario_atual
from sqlalchemy.orm import Session

router = APIRouter()


class UsuarioCadastro(BaseModel):
    nome: str
    email: EmailStr
    senha: str
    cargo: str


class UsuarioLogin(BaseModel):
    email: EmailStr
    senha: str


class PapelUpdate(BaseModel):
    papel: str


class AtivoUpdate(BaseModel):
    ativo: bool


class TrocaDeSenha(BaseModel):
    senha_atual: str
    senha_nova: str


@router.post("/usuario/cadastrar")
def cadastrar(usuario: UsuarioCadastro, db: Session = Depends(get_db)):
    try:
        return cadastrar_usuario(usuario.nome, usuario.email, usuario.senha, usuario.cargo, db)
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


@router.get("/usuario/listar")
def listar_todos(db: Session = Depends(get_db),
                 papel: str = Depends(exigir_papel("admin"))):
    return listar(db)


@router.patch("/usuario/{usuario_id}/papel")
def alterar_papel(usuario_id: int,
                  dados: PapelUpdate,
                  db: Session = Depends(get_db),
                  meu_id: str = Depends(usuario_atual),
                  papel: str = Depends(exigir_papel("admin"))):

    if int(meu_id) == usuario_id:
        raise HTTPException(status_code=400, detail="Você não pode alterar o seu próprio papel.")

    try:
        usuario = mudar_papel(usuario_id, dados.papel, db)
    except DadosInvalidoError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario


@router.patch("/usuario/{usuario_id}/ativo")
def alterar_ativo(usuario_id: int,
                  dados: AtivoUpdate,
                  db: Session = Depends(get_db),
                  meu_id: str = Depends(usuario_atual),
                  papel: str = Depends(exigir_papel("admin"))):

    if int(meu_id) == usuario_id:
        raise HTTPException(status_code=400, detail="Você não pode desativar a sua própria conta.")

    usuario = mudar_ativo(usuario_id, dados.ativo, db)
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario

@router.post("/usuario/trocar-senha")
def trocar_senha(dados: TrocaDeSenha,
                 db: Session = Depends(get_db),
                 meu_id: str = Depends(usuario_atual)):
    try:
        resultado = trocar_minha_senha(int(meu_id), dados.senha_atual, dados.senha_nova, db)
    except DadosInvalidoError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except CredenciaisInvalidasError as e:
        raise HTTPException(status_code=401, detail=str(e))

    if resultado is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return resultado


@router.post("/usuario/{usuario_id}/resetar-senha")
def resetar_senha(usuario_id: int,
                  db: Session = Depends(get_db),
                  meu_id: str = Depends(usuario_atual),
                  papel: str = Depends(exigir_papel("admin"))):
    if int(meu_id) == usuario_id:
        raise HTTPException(
            status_code=400,
            detail="Para trocar a sua própria senha use 'Trocar senha', informando a senha atual.")

    resultado = resetar_senha_de(usuario_id, db)
    if resultado is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return resultado