from model.filial_model import Filial


def listar_todas(db):
    return (db.query(Filial)
            .order_by(Filial.estado, Filial.nome)
            .all())


def listar_por_estado(estado, db):
    return (db.query(Filial)
            .filter(Filial.estado == estado)
            .order_by(Filial.nome)
            .all())


def buscar_por_id(filial_id, db):
    return db.query(Filial).filter(Filial.id == filial_id).first()


def existe(nome, estado, db):
    return (db.query(Filial)
            .filter(Filial.nome == nome)
            .filter(Filial.estado == estado)
            .first()) is not None


def criar(nome, estado, db):
    filial = Filial(nome=nome, estado=estado)
    db.add(filial)
    db.commit()
    db.refresh(filial)
    return filial


def atualizar(filial_id, nome, estado, db):
    filial = buscar_por_id(filial_id, db)
    if filial is None:
        return None
    filial.nome = nome
    filial.estado = estado
    db.commit()
    db.refresh(filial)
    return filial


def apagar(filial_id, db):
    filial = buscar_por_id(filial_id, db)
    if filial is None:
        return None
    db.delete(filial)
    db.commit()
    return True