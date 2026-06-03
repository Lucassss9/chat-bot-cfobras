from repository.usuario_repository import salvar_usuario, buscar_usuario_por_email

def cadastrar_usuario(nome, email, senha):
    nome = nome.strip()
    email = email.strip().lower()
    senha = senha.strip()

    erro = _validar_vazio(nome, email, senha)
    print(f"Erro validação: {erro}")

    if erro:
        return erro

    if not _validar_email(email):
        return {"sucesso": False, "mensagem": "E-mail inválido"}

    if not _validar_senha(senha):
        return {"sucesso": False, "mensagem": "Senha inválida"}

    usuario = buscar_usuario_por_email(email)

    if usuario is None:
        salvar_usuario(nome, email, senha)
        return {"sucesso": True, "mensagem": "Usuário cadastrado com sucesso"}
    else:
        return {"sucesso": False, "mensagem": "Usuário já existe"}

def login(email, senha):
    email = email.strip().lower()
    senha = senha.strip()

    if not email:
        return {"mensagem": "E-mail Obrigatorio"}

    if not senha:
        return {"mensagem": "Senha Obrigatoria"}

    usuario = buscar_usuario_por_email(email)

    if usuario is None:
        return {"mensagem": "Faça o Cadastro"}

    if usuario.senha == senha:
        return {"id": usuario.id, "nome": usuario.nome}
    else:
        return {"mensagem": "Senha incorreta"}

def _validar_email(email):
    return "@" in email and ".com" in email or ".net" in email

def _validar_senha(senha):
    return len(senha) >= 8

def _validar_vazio(nome, email, senha):
    if not nome:
        return {"sucesso": False, "mensagem": "Nome Obrigatorio"}

    if not email:
        return {"sucesso": False, "mensagem": "E-mail Obrigatorio"}

    if not senha:
        return {"sucesso": False, "mensagem": "Senha Obrigatoria"}
