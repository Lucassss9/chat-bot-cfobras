from fastapi import FastAPI
from routes.chat_routes import registrar_rotas

app = FastAPI()

registrar_rotas(app)