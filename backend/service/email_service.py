import os
import smtplib
from email.message import EmailMessage

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")         
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
NOME_REMETENTE = os.getenv("NOME_REMETENTE", "CF Obras")

SENHA_INICIAL = "123Mudar@"
URL_CF_OBRAS = "https://manager.cfobras.com.br"


def _enviar(destinatario, assunto, corpo):
    if not destinatario:
        print("E-mail não enviado: destinatário vazio")
        return False

    if not SMTP_USER or not SMTP_PASSWORD:
        print(f"SMTP não configurado. E-mail que iria para {destinatario}: {assunto}")
        return False

    try:
        mensagem = EmailMessage()
        mensagem["Subject"] = assunto
        mensagem["From"] = f"{NOME_REMETENTE} <{SMTP_USER}>"
        mensagem["To"] = destinatario
        mensagem.set_content(corpo)

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=20) as servidor:
            servidor.starttls()
            servidor.login(SMTP_USER, SMTP_PASSWORD)
            servidor.send_message(mensagem)

        print(f"E-mail enviado para {destinatario}: {assunto}")
        return True

    except Exception as erro:
        print(f"Erro ao enviar e-mail para {destinatario}: {erro}")
        return False


def avisar_recusa(destinatario, nome_colaborador, motivo):
    corpo = (
        f"Olá,\n\n"
        f"A solicitação de cadastro de {nome_colaborador} no CF Obras foi recusada.\n\n"
        f"Motivo: {motivo}\n\n"
        f"Corrija os dados e envie a solicitação novamente pela Central de Ajuda.\n"
    )
    return _enviar(destinatario, f"Solicitação recusada - {nome_colaborador}", corpo)


def avisar_cadastro_concluido(destinatario, nome_colaborador):
    corpo = (
        f"Olá, {nome_colaborador}.\n\n"
        f"Seu acesso ao CF Obras foi criado.\n\n"
        f"Endereço: {URL_CF_OBRAS}\n"
        f"Login: {destinatario}\n"
        f"Senha inicial: {SENHA_INICIAL}\n\n"
        f"Troque a senha no primeiro acesso.\n"
    )
    return _enviar(destinatario, "Seu acesso ao CF Obras foi criado", corpo)


def avisar_erro_no_robo(destinatario, nome_colaborador, erro):
    corpo = (
        f"Olá,\n\n"
        f"O cadastro de {nome_colaborador} no CF Obras falhou.\n\n"
        f"Erro: {erro}\n\n"
        f"Verifique os dados na Central de Ajuda.\n"
    )
    return _enviar(destinatario, f"Falha no cadastro - {nome_colaborador}", corpo)