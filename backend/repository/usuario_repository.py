from model.usuario_model import Usuario
from datetime import datetime, timezone
import bcrypt


def salvar_usuario(nome, email, senha, cargo, papel, db):
    try:
        senha = bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        novo_usuario = Usuario(nome=nome, email=email, senha=senha,
                               cargo=cargo, papel=papel, ativo=True)
        db.add(novo_usuario)
        db.commit()
    except:
        db.rollback()
        raise


def buscar_usuario_por_email(email, db):
    return db.query(Usuario).filter(Usuario.email == email).first()


def buscar_usuario_por_id(usuario_id, db):
    try:
        return db.query(Usuario).filter(Usuario.id == usuario_id).first()
    except:
        db.rollback()
        raise


def listar_usuarios(db):
    return db.query(Usuario).order_by(Usuario.nome).all()


def atualizar_papel(usuario_id, papel, db):
    try:
        usuario = buscar_usuario_por_id(usuario_id, db)
        if usuario is None:
            return None
        usuario.papel = papel
        db.commit()
        db.refresh(usuario)
        return usuario
    except:
        db.rollback()
        raise


def listar_emails_admins(db, excluir=None):
    excluir = (excluir or "").strip().lower()
    admins = db.query(Usuario).filter(Usuario.papel == "admin",
                                      Usuario.ativo.is_(True)).all()
    return [u.email for u in admins
            if u.email and u.email.strip().lower() != excluir]


def atualizar_senha(usuario_id, senha_nova, db, temporaria=False):
    try:
        usuario = buscar_usuario_por_id(usuario_id, db)
        if usuario is None:
            return None
        usuario.senha = bcrypt.hashpw(senha_nova.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        usuario.senha_alterada_em = datetime.now(timezone.utc)
        usuario.senha_temporaria = temporaria
        db.commit()
        db.refresh(usuario)
        return usuario
    except:
        db.rollback()
        raise


def atualizar_ativo(usuario_id, ativo, db):
    try:
        usuario = buscar_usuario_por_id(usuario_id, db)
        if usuario is None:
            return None
        usuario.ativo = ativo
        db.commit()
        db.refresh(usuario)
        return usuario
    except:
        db.rollback()
        raise