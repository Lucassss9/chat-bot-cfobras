from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from config.auth import exigir_papel
from config.connection import get_db
from typing import List
from repository.config_repository import (
    obter_senha_padrao, definir, obter_emails_resumo, definir_emails_resumo,
)

router = APIRouter()


class EmailsResumo(BaseModel):
    emails: List[EmailStr]


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

    @router.get("/config/emails-resumo")
    def ler_emails_resumo(db: Session = Depends(get_db),
                          papel: str = Depends(exigir_papel("admin"))):
        return {"emails": obter_emails_resumo(db)}

    @router.put("/config/emails-resumo")
    def mudar_emails_resumo(dados: EmailsResumo,
                            db: Session = Depends(get_db),
                            papel: str = Depends(exigir_papel("admin"))):
        if len(dados.emails) > 20:
            raise HTTPException(status_code=400, detail="No máximo 20 destinatários.")
        salvos = definir_emails_resumo([str(e) for e in dados.emails], db)
        return {"emails": salvos, "mensagem": "Lista atualizada."}

    app.include_router(router)