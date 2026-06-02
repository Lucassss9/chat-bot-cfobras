from fastapi import FastAPI
from routes.chat_routes import registrar_rotas
from routes.usuario_routes import router as usuario_router

app = FastAPI()

registrar_rotas(app)
app.include_router(usuario_router)