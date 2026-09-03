from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.chat_routes import registrar_rotas
from routes.usuario_routes import router as usuario_router
from routes.colaborador_routes import router as colaborador_router
from routes.obra_routes import router as obra_router
from routes.config_routes import registrar_rotas_config
from routes.filial_routes import router as filial_router
from routes.artigo_routes import router as artigo_router
from routes.resumo_routes import router as resumo_router
from routes.teste_email_routes import router as teste_email_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health():
    return {"status": "ok"}


registrar_rotas(app)
app.include_router(usuario_router)
app.include_router(colaborador_router)
app.include_router(obra_router)
registrar_rotas_config(app)
app.include_router(filial_router)
app.include_router(artigo_router)
app.include_router(resumo_router)
app.include_router(teste_email_router)

@app.on_event("startup")
def popular_filiais():
    from config.connection import session_local
    from repository.filial_repository import listar_todas, criar
    try:
        from scripts.seed_filiais import SEED_FILIAIS
    except Exception:
        return
    db = session_local()
    try:
        if len(listar_todas(db)) == 0:
            for nome, estado in SEED_FILIAIS:
                criar(nome, estado, db)
    except Exception:
        pass
    finally:
        db.close()