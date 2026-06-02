from repository.usuario_repository import salvar_usuario, buscar_usuario_por_email

def cadastrar_usuario(nome, email, senha):
    nome = nome.strip()
    email = email.strip().lower()
    senha = senha.strip()

    erro = _validar_vazio(nome, email, senha)

    if erro:
        return erro

    if not _validar_email(email):
        return "Email inválido"

    if not _validar_senha(senha):
        return "Senha inválida"

    usuario = buscar_usuario_por_email(email)

    if usuario is None:
        salvar_usuario(nome, email, senha)
        return "Usuário cadastrado com sucesso"
    else:
        return "Usuário já existe"

def login(email, senha):
    email = email.strip().lower()
    senha = senha.strip()

    if not email:
        return "Email obrigatório"

    if not senha:
        return "Senha obrigatória"

    usuario = buscar_usuario_por_email(email)

    if usuario is None:
        return "Faça o cadastro"

    if usuario.senha == senha:
        return  "Senha correta"
    else:
        return "Senha incorreta"

def _validar_email(email):
    return "@" in email and ".com" in email

def _validar_senha(senha):
    return len(senha) >= 8

def _validar_vazio(nome, email, senha):
    if not nome:
        return "Nome obrigatório"

    if not email:
        return "Email obrigatório"

    if not senha:
        return "Senha obrigatória"
