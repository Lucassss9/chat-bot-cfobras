from model.artigo_model import Artigo
from datetime import datetime


def listar_ativos(db):
    try:
        return (db.query(Artigo)
                .filter(Artigo.ativo.is_(True))
                .order_by(Artigo.grupo, Artigo.id)
                .all())
    except Exception as erro:
        db.rollback()
        print("Erro ao listar artigos:", erro)
        return []


def listar_destaques(db):
    try:
        return (db.query(Artigo)
                .filter(Artigo.ativo.is_(True), Artigo.destaque.is_(True))
                .order_by(Artigo.ordem, Artigo.id)
                .all())
    except Exception as erro:
        db.rollback()
        print("Erro ao listar destaques:", erro)
        return []


def listar_todos(db):
    try:
        return db.query(Artigo).order_by(Artigo.grupo, Artigo.id).all()
    except Exception as erro:
        db.rollback()
        print("Erro ao listar artigos:", erro)
        return []


def buscar_por_id(artigo_id, db):
    return db.query(Artigo).filter(Artigo.id == artigo_id).first()


def criar(grupo, pergunta, caminho, resposta, db,
          variacoes=None, destaque=False, ordem=0):
    try:
        artigo = Artigo(grupo=grupo, pergunta=pergunta,
                        caminho=caminho, resposta=resposta,
                        variacoes=variacoes,
                        destaque=destaque, ordem=ordem)
        db.add(artigo)
        db.commit()
        db.refresh(artigo)
        return artigo
    except Exception:
        db.rollback()
        raise


def atualizar(artigo_id, dados, db):
    try:
        artigo = buscar_por_id(artigo_id, db)
        if artigo is None:
            return None

        for campo in ("grupo", "pergunta", "caminho", "resposta",
                      "variacoes", "ativo", "destaque", "ordem"):
            valor = getattr(dados, campo, None)
            if valor is not None:
                setattr(artigo, campo, valor)

        artigo.atualizado_em = datetime.now()
        db.commit()
        db.refresh(artigo)
        return artigo
    except Exception:
        db.rollback()
        raise


def apagar(artigo_id, db):
    try:
        artigo = buscar_por_id(artigo_id, db)
        if artigo is None:
            return False
        db.delete(artigo)
        db.commit()
        return True
    except Exception:
        db.rollback()
        raise


def montar_contexto(db):
    artigos = listar_ativos(db)
    if not artigos:
        return ""

    partes = []
    for a in artigos:
        bloco = f"### {a.pergunta}"

        if a.variacoes:
            outras = [v.strip() for v in a.variacoes.splitlines() if v.strip()]
            if outras:
                bloco += "\nTambem perguntam assim: " + " | ".join(outras)

        if a.caminho:
            bloco += f"\nOnde fica: {a.caminho}"

        bloco += f"\n{a.resposta}"
        partes.append(bloco)

    return "\n\n".join(partes)