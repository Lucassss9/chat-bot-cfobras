from model.usuario_model import Usuario


def salvar_usuario(nome, email, senha, db):
    print(f"Salvando: {nome}, {email}")
    try:
        novo_usuario = Usuario(nome=nome, email=email, senha=senha )
        db.add(novo_usuario)
        db.commit()
    except Exception as e:
        db.rollback()
        return e

def buscar_usuario_por_email(email, db):
    try:
        usuario = db.query(Usuario).filter(Usuario.email == email).first()
        return usuario
    except Exception as e:
        db.rollback()
        return e

def buscar_usuario_por_id(usuario_id, db):
    try:
        usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
        return usuario
    except Exception as e:
        db.rollback()
        return e