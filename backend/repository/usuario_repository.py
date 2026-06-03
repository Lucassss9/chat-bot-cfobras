from model.usuario_model import Usuario
from config.connection import session_local

def salvar_usuario(nome, email, senha):
    print(f"Salvando: {nome}, {email}")
    session = session_local()

    try:
        novo_usuario = Usuario(
            nome=nome,
            email=email,
            senha=senha
        )

        session.add(novo_usuario)
        session.commit()
    except Exception as e:
        session.rollback()
        print(e)
    finally:
        session.close()

def buscar_usuario_por_email(email):
    session = session_local()

    try:
        usuario = session.query(Usuario).filter(Usuario.email == email).first()
        return usuario
    finally:
        session.close()

def buscar_usuario_por_id(usuario_id):
    session = session_local()

    try:
        usuario = session.query(Usuario).filter(Usuario.id == usuario_id).first()
        return usuario
    finally:
        session.close()