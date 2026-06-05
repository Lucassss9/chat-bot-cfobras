from model.manual_model import Manual

def buscar_manual(db):
    try:
        return db.query(Manual).first()
    except Exception as e:
        db.rollback()
        print(e)