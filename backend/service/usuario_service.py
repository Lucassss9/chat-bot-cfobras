from repository.usuario_repository import salvar_usuario, buscar_usuario_por_email
from exception.usuario_exception import UsuarioJaExisteError, DadosInvalidoError, CredenciaisInvalidasError
import bcrypt

def cadastrar_usuario(nome, email, senha, db):
    nome = nome.strip()
    email = email.strip().lower()
    senha = senha.strip()

    _validar_vazio(nome, email, senha)

    if not _validar_senha(senha):
        raise DadosInvalidoError("Senha deve conter 8 caracteres ou mais")

    usuario = buscar_usuario_por_email(email, db)

    if usuario is None:
        salvar_usuario(nome, email, senha, db)
        return {"mensagem": "Usuário cadastrado com sucesso"}
    else:
        raise UsuarioJaExisteError("Usuário já existe")

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

    hash_banco = usuario.senha

    if bcrypt.checkpw(senha.encode("utf-8"), hash_banco.encode("utf-8")):
        return {"id": usuario.id, "nome": usuario.nome}
    else:
        raise CredenciaisInvalidasError("Senha incorreta")

def _validar_senha(senha):
    return len(senha) >= 8

def _validar_vazio(nome, email, senha):
    if not nome:
        raise DadosInvalidoError("Nome Obrigatorio")

    if not email:
        raise DadosInvalidoError("E-mail Obrigatorio")

    if not senha:
        raise DadosInvalidoError("Senha Obrigatoria")