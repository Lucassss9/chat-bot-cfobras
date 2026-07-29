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