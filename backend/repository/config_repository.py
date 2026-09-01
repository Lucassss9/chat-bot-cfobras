from model.config_model import Config

SENHA_PADRAO_DEFAULT = "123Mudar@"


def obter(chave, db, padrao=None):
    item = db.query(Config).filter(Config.chave == chave).first()
    return item.valor if item and item.valor is not None else padrao


def definir(chave, valor, db):
    item = db.query(Config).filter(Config.chave == chave).first()
    if item is None:
        item = Config(chave=chave, valor=valor)
        db.add(item)
    else:
        item.valor = valor
    db.commit()
    return item


def obter_senha_padrao(db):
    return obter("senha_padrao", db, SENHA_PADRAO_DEFAULT)


def obter_emails_resumo(db):
    bruto = obter("emails_resumo", db, "") or ""
    return [e.strip() for e in bruto.split(",") if e.strip()]


def definir_emails_resumo(lista, db):
    limpos = []
    for email in lista:
        email = (email or "").strip().lower()
        if email and email not in limpos:
            limpos.append(email)
    definir("emails_resumo", ",".join(limpos), db)
    return limpos