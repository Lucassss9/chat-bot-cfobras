from model.usuario_model import Usuario
import bcrypt

def salvar_usuario(nome, email, senha, db):
    print(f"Salvando: {nome}, {email}")
    try:
        senha = bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        novo_usuario = Usuario(nome=nome, email=email, senha=senha)
        db.add(novo_usuario)
        db.commit()
    except:
        db.rollback()
        raise

def buscar_usuario_por_email(email, db):
     return db.query(Usuario).filter(Usuario.email == email).first()

def buscar_usuario_por_id(usuario_id, db):
    try:
        usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
        return usuario
    except:
        db.rollback()
        raise