from repository.usuario_repository import (
    salvar_usuario, buscar_usuario_por_email, listar_usuarios,
    atualizar_papel, atualizar_ativo,
)
from exception.usuario_exception import UsuarioJaExisteError, DadosInvalidoError, CredenciaisInvalidasError
from model.usuario_model import PAPEIS
from datetime import datetime, timedelta, timezone
import jwt
import os
import bcrypt

SECRET = os.getenv("JWT_KEY")
ALGORITMO = os.getenv("ALGORITHM")

# quem se cadastrar com este e-mail vira admin automaticamente (defina no .env / Render)
ADMIN_EMAIL = (os.getenv("ADMIN_EMAIL") or "").strip().lower()


def cadastrar_usuario(nome, email, senha, cargo, db):
    nome = nome.strip()
    email = email.strip().lower()
    senha = senha.strip()
    cargo = (cargo or "").strip()

    _validar_vazio(nome, email, senha)

    if not cargo:
        raise DadosInvalidoError("Cargo obrigatório")

    if not _validar_senha(senha):
        raise DadosInvalidoError("Senha deve conter 8 caracteres ou mais")

    if buscar_usuario_por_email(email, db) is not None:
        raise UsuarioJaExisteError("Usuário já existe")

    # todo mundo entra como "comum". Só um admin promove depois.
    papel = "admin" if (ADMIN_EMAIL and email == ADMIN_EMAIL) else "comum"

    salvar_usuario(nome, email, senha, cargo, papel, db)
    return {"mensagem": "Usuário cadastrado com sucesso"}


def login(email, senha, db):
    email = email.strip().lower()
    senha = senha.strip()

    if not email:
        raise DadosInvalidoError("E-mail obrigatório")

    if not senha:
        raise DadosInvalidoError("Senha obrigatória")

    usuario = buscar_usuario_por_email(email, db)

    if usuario is None:
        raise CredenciaisInvalidasError("Usuário não existe. Faça o seu cadastro.")

    if not usuario.ativo:
        raise CredenciaisInvalidasError("Este acesso está desativado. Fale com o administrador.")

    if bcrypt.checkpw(senha.encode("utf-8"), usuario.senha.encode("utf-8")):
        dados = {
            "sub": str(usuario.id),
            "papel": usuario.papel,
            "exp": datetime.now(timezone.utc) + timedelta(hours=8),
        }
        token = jwt.encode(dados, SECRET, algorithm=ALGORITMO)
        return {
            "token": token,
            "id": usuario.id,
            "nome": usuario.nome,
            "cargo": usuario.cargo,
            "papel": usuario.papel,
        }
    else:
        raise CredenciaisInvalidasError("Senha incorreta")


def listar(db):
    usuarios = listar_usuarios(db)
    return [_para_dict(u) for u in usuarios]


def mudar_papel(usuario_id, papel, db):
    if papel not in PAPEIS:
        raise DadosInvalidoError(f"Papel deve ser um de: {', '.join(PAPEIS)}")

    usuario = atualizar_papel(usuario_id, papel, db)
    if usuario is None:
        return None
    return _para_dict(usuario)


def mudar_ativo(usuario_id, ativo, db):
    usuario = atualizar_ativo(usuario_id, ativo, db)
    if usuario is None:
        return None
    return _para_dict(usuario)


def _para_dict(usuario):
    return {
        "id": usuario.id,
        "nome": usuario.nome,
        "email": usuario.email,
        "cargo": usuario.cargo,
        "papel": usuario.papel,
        "ativo": usuario.ativo,
    }


def _validar_senha(senha):
    return len(senha) >= 8


def _validar_vazio(nome, email, senha):
    if not nome:
        raise DadosInvalidoError("Nome Obrigatorio")

    if not email:
        raise DadosInvalidoError("E-mail Obrigatorio")

    if not senha:
        raise DadosInvalidoError("Senha Obrigatoria")