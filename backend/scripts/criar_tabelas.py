from config.connection import engine, base

print("Conectando ao servidor da Neon na AWS...")
base.metadata.create_all(bind=engine)
print("Sucesso! A tabela 'manuais' foi criada na nuvem!")