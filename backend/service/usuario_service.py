from repository.usuario_repository import salvar_usuario, buscar_usuario_por_email
from exception.usuario_exception import UsuarioJaExisteError, DadosInvalidoError, CredenciaisInvalidasError

def cadastrar_usuario(nome, email, senha):
    nome = nome.strip()
    email = email.strip().lower()
    senha = senha.strip()

    _validar_vazio(nome, email, senha)

    if not _validar_senha(senha):
        raise DadosInvalidoError("Senha deve conter 8 caracteres ou mais")

    usuario = buscar_usuario_por_email(email)

    if usuario is None:
        salvar_usuario(nome, email, senha)
        return {"mensagem": "Usuário cadastrado com sucesso"}
    else:
        raise UsuarioJaExisteError("Usuário já existe")

def login(email, senha):
    email = email.strip().lower()
    senha = senha.strip()

    if not email:
        raise DadosInvalidoError("E-mail obrigatório")

    if not senha:
        raise DadosInvalidoError("Senha obrigatória")

    usuario = buscar_usuario_por_email(email)

    if usuario is None:
        raise CredenciaisInvalidasError("Usuário não existe. Faça o seu cadastro.")

    if usuario.senha == senha:
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