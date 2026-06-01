from database.connection import engine, base
from database.manual_model import Manual

print("Conectando ao servidor da Neon na AWS...")
base.metadata.create_all(bind=engine)
print("Sucesso! A tabela 'manuais' foi criada na nuvem!")