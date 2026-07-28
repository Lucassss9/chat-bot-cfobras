from model.colaborador_model import Colaborador
from model.usuario_model import Usuario
from service.texto_util import normalizar_nome, normalizar_email


def salvar(dados, obra_texto, solicitante_id, db):
    try:
        colaborador = Colaborador(
            nome=normalizar_nome(dados.nome),
            email=normalizar_email(dados.email),
            funcao=None if dados.ja_tem_acesso else dados.funcao,
            estado=dados.estado,
            obra=obra_texto,
            observacao=(dados.observacao or None),
            terceirizado=False if dados.ja_tem_acesso else dados.terceirizado,
            cpf=None if (dados.ja_tem_acesso or dados.terceirizado) else dados.cpf,
            ja_tem_acesso=dados.ja_tem_acesso,
            solicitante_id=solicitante_id,
        )
        db.add(colaborador)
        db.commit()
        db.refresh(colaborador)
        return colaborador
    except Exception:
        db.rollback()
        raise


def existe_email(email, db, ignorar_id=None):
    email = (email or "").strip().lower()
    if not email:
        return False
    consulta = (db.query(Colaborador)
                .filter(Colaborador.email == email)
                .filter(Colaborador.status != "recusado"))
    if ignorar_id is not None:
        consulta = consulta.filter(Colaborador.id != ignorar_id)
    return consulta.first() is not None


def existe_cpf(cpf, db, ignorar_id=None):
    cpf = (cpf or "").strip()
    if not cpf:
        return False
    consulta = (db.query(Colaborador)
                .filter(Colaborador.cpf == cpf)
                .filter(Colaborador.status != "recusado"))
    if ignorar_id is not None:
        consulta = consulta.filter(Colaborador.id != ignorar_id)
    return consulta.first() is not None


def editar_e_reenviar(colaborador_id, dados, obra_texto, solicitante_id, db):
    try:
        colaborador = buscar_por_id(colaborador_id, db)
        if colaborador is None:
            return "nao_encontrado"
        if colaborador.solicitante_id != solicitante_id:
            return "nao_e_seu"
        if colaborador.status != "recusado":
            return "nao_recusado"

        colaborador.nome = normalizar_nome(dados.nome)
        colaborador.email = normalizar_email(dados.email)
        colaborador.funcao = None if dados.ja_tem_acesso else dados.funcao
        colaborador.estado = dados.estado
        colaborador.obra = obra_texto
        colaborador.observacao = dados.observacao or None
        colaborador.terceirizado = False if dados.ja_tem_acesso else dados.terceirizado
        colaborador.cpf = None if (dados.ja_tem_acesso or dados.terceirizado) else dados.cpf
        colaborador.ja_tem_acesso = dados.ja_tem_acesso
        colaborador.status = "pendente"
        colaborador.motivo = None
        colaborador.erro = None
        db.commit()
        db.refresh(colaborador)
        return colaborador
    except Exception:
        db.rollback()
        raise


def listar_por_status(status, db):
    return db.query(Colaborador).filter(Colaborador.status == status).all()


def listar_todos(db):
    resultados = (db.query(Colaborador, Usuario.nome, Usuario.email)
                  .outerjoin(Usuario, Colaborador.solicitante_id == Usuario.id)
                  .order_by(Colaborador.criado_em.desc())
                  .all())

    lista = []
    for colaborador, nome_do_solicitante, email_do_solicitante in resultados:
        colaborador.solicitante_nome = nome_do_solicitante
        colaborador.solicitante_email = email_do_solicitante
        lista.append(colaborador)
    return lista


def listar_do_solicitante(solicitante_id, db):
    return (db.query(Colaborador)
            .filter(Colaborador.solicitante_id == solicitante_id)
            .order_by(Colaborador.criado_em.desc())
            .all())


def buscar_por_id(colaborador_id, db):
    return db.query(Colaborador).filter(Colaborador.id == colaborador_id).first()


def buscar_email_do_solicitante(solicitante_id, db):
    usuario = db.query(Usuario).filter(Usuario.id == solicitante_id).first()
    return usuario.email if usuario else None


def atualizar_status(colaborador_id, status, erro, db):
    try:
        colaborador = buscar_por_id(colaborador_id, db)
        if colaborador is None:
            return None
        colaborador.status = status
        colaborador.erro = erro
        db.commit()
        db.refresh(colaborador)
        return colaborador
    except Exception:
        db.rollback()
        raise


def atualizar_decisao(colaborador_id, status, motivo, db):
    try:
        colaborador = buscar_por_id(colaborador_id, db)
        if colaborador is None:
            return None
        colaborador.status = status
        colaborador.motivo = motivo
        db.commit()
        db.refresh(colaborador)
        return colaborador
    except Exception:
        db.rollback()
        raise