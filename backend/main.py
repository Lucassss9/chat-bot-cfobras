from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.chat_routes import registrar_rotas
from routes.usuario_routes import router as usuario_router
from routes.colaborador_routes import router as colaborador_router
from routes.obra_routes import router as obra_router

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