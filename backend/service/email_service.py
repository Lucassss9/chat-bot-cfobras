import os
import requests

RESEND_API_KEY = os.getenv("RESEND_API_KEY")

EMAIL_FROM = os.getenv("EMAIL_FROM", "CF Obras <onboarding@resend.dev>")

URL_RESEND = "https://api.resend.com/emails"
SENHA_INICIAL = "123Mudar@"
URL_CF_OBRAS = "https://manager.cfobras.com.br"


def _enviar(destinatario, assunto, corpo):
    if not destinatario:
        print("E-mail não enviado: destinatário vazio")
        return False

    if not RESEND_API_KEY:
        print(f"RESEND_API_KEY não configurada. E-mail que iria para {destinatario}: {assunto}")
        return False

    try:
        resposta = requests.post(
            URL_RESEND,
            headers={
                "Authorization": f"Bearer {RESEND_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "from": EMAIL_FROM,
                "to": [destinatario],
                "subject": assunto,
                "text": corpo,
            },
            timeout=20,
        )

        if resposta.status_code >= 400:
            print(f"Resend recusou o e-mail para {destinatario}: {resposta.status_code} {resposta.text}")
            return False

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