from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.chat_routes import registrar_rotas
from routes.usuario_routes import router as usuario_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

registrar_rotas(app)
app.include_router(usuario_router)

