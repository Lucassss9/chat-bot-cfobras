from repository.usuario_repository import (
    salvar_usuario, buscar_usuario_por_email, buscar_usuario_por_id, listar_usuarios,
    atualizar_papel, atualizar_ativo, atualizar_senha,
)
from exception.usuario_exception import UsuarioJaExisteError, DadosInvalidoError, CredenciaisInvalidasError
from model.usuario_model import PAPEIS
from datetime import datetime, timedelta, timezone
import jwt
import os
import bcrypt
import secrets

SECRET = os.getenv("JWT_KEY")
ALGORITMO = os.getenv("ALGORITHM")

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
        agora = datetime.now(timezone.utc)
        dados = {
            "sub": str(usuario.id),
            "papel": usuario.papel,
            "iat": agora,
            "exp": agora + timedelta(hours=8),
        }
        token = jwt.encode(dados, SECRET, algorithm=ALGORITMO)
        return {
            "token": token,
            "id": usuario.id,
            "nome": usuario.nome,
            "cargo": usuario.cargo,
            "papel": usuario.papel,
            "senha_temporaria": bool(usuario.senha_temporaria),
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


def trocar_minha_senha(usuario_id, senha_atual, senha_nova, db):
    senha_atual = (senha_atual or "").strip()
    senha_nova = (senha_nova or "").strip()

    if not senha_atual:
        raise DadosInvalidoError("Informe a sua senha atual.")

    if not _validar_senha(senha_nova):
        raise DadosInvalidoError("A senha nova deve ter 8 caracteres ou mais.")

    if senha_atual == senha_nova:
        raise DadosInvalidoError("A senha nova precisa ser diferente da atual.")

    usuario = buscar_usuario_por_id(usuario_id, db)
    if usuario is None:
        return None

    if not bcrypt.checkpw(senha_atual.encode("utf-8"), usuario.senha.encode("utf-8")):
        raise CredenciaisInvalidasError("Senha atual incorreta.")

    atualizar_senha(usuario_id, senha_nova, db, temporaria=False)
    return {"mensagem": "Senha alterada. Entre de novo com a senha nova."}


def resetar_senha_de(usuario_id, db):
    """Admin zera a senha de alguem. A temporaria aparece uma unica vez."""
    usuario = buscar_usuario_por_id(usuario_id, db)
    if usuario is None:
        return None

    temporaria = _gerar_senha_temporaria()
    atualizar_senha(usuario_id, temporaria, db, temporaria=True)

    return {
        "nome": usuario.nome,
        "email": usuario.email,
        "senha_temporaria": temporaria,
    }


_ALFABETO = "ABCDEFGHJKMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789"


def _gerar_senha_temporaria():
    blocos = ["".join(secrets.choice(_ALFABETO) for _ in range(4)) for _ in range(3)]
    return "-".join(blocos)


def _para_dict(usuario):
    return {
        "id": usuario.id,
        "nome": usuario.nome,
        "email": usuario.email,
        "cargo": usuario.cargo,
        "papel": usuario.papel,
        "ativo": usuario.ativo,
        "senha_temporaria": bool(usuario.senha_temporaria),
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