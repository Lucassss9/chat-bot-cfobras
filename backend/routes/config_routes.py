from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from config.auth import exigir_papel
from config.connection import get_db
from repository.config_repository import obter_senha_padrao, definir

router = APIRouter()


class SenhaPadrao(BaseModel):
    senha: str


def registrar_rotas_config(app):
    @router.get("/config/senha-padrao")
    def ler_senha(db: Session = Depends(get_db),
                  papel: str = Depends(exigir_papel("solicitante", "admin"))):
        return {"senha": obter_senha_padrao(db)}

    @router.patch("/config/senha-padrao")
    def mudar_senha(dados: SenhaPadrao,
                    db: Session = Depends(get_db),
                    papel: str = Depends(exigir_papel("admin"))):
        if not dados.senha or len(dados.senha) < 6:
            raise HTTPException(status_code=400, detail="A senha precisa de ao menos 6 caracteres.")
        definir("senha_padrao", dados.senha, db)
        return {"senha": dados.senha, "mensagem": "Senha padrão atualizada."}

    app.include_router(router)