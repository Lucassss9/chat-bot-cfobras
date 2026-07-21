from model.colaborador_model import Colaborador
from model.usuario_model import Usuario


def salvar(dados, solicitante_id, db):
    try:
        colaborador = Colaborador(
            nome=dados.nome,
            email=dados.email,
            funcao=dados.funcao,
            estado=dados.estado,
            obra=dados.obra,
            terceirizado=dados.terceirizado,
            cpf=None if dados.terceirizado else dados.cpf,
            data_admissao=None if dados.terceirizado else dados.data_admissao,
            exibir_epi=False if dados.terceirizado else dados.exibir_epi,
            solicitante_id=solicitante_id,
        )
        db.add(colaborador)
        db.commit()
        db.refresh(colaborador)
        return colaborador
    except Exception:
        db.rollback()
        raise


def listar_por_status(status, db):
    return db.query(Colaborador).filter(Colaborador.status == status).all()


def listar_todos(db):
    """Só para admin: tudo, de todo mundo, com o nome de quem solicitou."""
    resultados = (db.query(Colaborador, Usuario.nome)
                  .outerjoin(Usuario, Colaborador.solicitante_id == Usuario.id)
                  .order_by(Colaborador.criado_em.desc())
                  .all())

    lista = []
    for colaborador, nome_do_solicitante in resultados:
        colaborador.solicitante_nome = nome_do_solicitante
        lista.append(colaborador)
    return lista


def listar_do_solicitante(solicitante_id, db):
    return (db.query(Colaborador)
            .filter(Colaborador.solicitante_id == solicitante_id)
            .order_by(Colaborador.criado_em.desc())
            .all())


def buscar_por_id(colaborador_id, db):
    return db.query(Colaborador).filter(Colaborador.id == colaborador_id).first()


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