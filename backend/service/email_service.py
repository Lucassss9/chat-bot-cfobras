import os
import requests

BREVO_API_KEY = os.getenv("BREVO_API_KEY")
EMAIL_REMETENTE = os.getenv("EMAIL_REMETENTE")
NOME_REMETENTE = os.getenv("NOME_REMETENTE", "CF Obras")

URL_BREVO = "https://api.brevo.com/v3/smtp/email"
URL_CF_OBRAS = "https://manager.cfobras.com.br"


def _enviar(destinatario, assunto, corpo):
    if not destinatario:
        print("E-mail não enviado: destinatário vazio")
        return False

    if not BREVO_API_KEY or not EMAIL_REMETENTE:
        print(f"Brevo não configurado. E-mail que iria para {destinatario}: {assunto}")
        return False

    try:
        resposta = requests.post(
            URL_BREVO,
            headers={
                "api-key": BREVO_API_KEY,
                "Content-Type": "application/json",
                "accept": "application/json",
            },
            json={
                "sender": {"name": NOME_REMETENTE, "email": EMAIL_REMETENTE},
                "to": [{"email": destinatario}],
                "subject": assunto,
                "textContent": corpo,
            },
            timeout=20,
        )

        if resposta.status_code >= 400:
            print(f"Brevo recusou o e-mail para {destinatario}: "
                  f"{resposta.status_code} {resposta.text}")
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


def avisar_cadastro_concluido(destinatario, nome_colaborador, senha_inicial):
    """Vai para a PESSOA cadastrada, com as credenciais dela."""
    corpo = (
        f"Olá, {nome_colaborador}.\n\n"
        f"Seu acesso ao CF Obras foi criado.\n\n"
        f"Endereço: {URL_CF_OBRAS}\n"
        f"Login: {destinatario}\n"
        f"Senha inicial: {senha_inicial}\n\n"
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

def avisar_colaborador_aprovado(destinatario, nome_colaborador):
    corpo = (
        f"Olá,\n\n"
        f"A solicitação de cadastro de {nome_colaborador} foi aprovada e entrou na fila do robô.\n\n"
        f"Você recebe outro aviso quando o cadastro estiver concluído.\n"
    )
    return _enviar(destinatario, f"Solicitação aprovada - {nome_colaborador}", corpo)


def avisar_colaborador_vinculado(destinatario, nome_colaborador, obras, so_vinculo):
    """Vai para quem PEDIU, avisando que o robô terminou."""
    acao = "vinculado" if so_vinculo else "cadastrado e vinculado"
    corpo = (
        f"Olá,\n\n"
        f"{nome_colaborador} foi {acao} no CF Obras.\n\n"
        f"Obras: {obras or '-'}\n\n"
        + ("A pessoa continua com a senha que já usava.\n"
           if so_vinculo else
           "A pessoa recebeu por e-mail o endereço, o login e a senha inicial.\n")
    )
    return _enviar(destinatario, f"Cadastro concluído - {nome_colaborador}", corpo)


def avisar_obra_aprovada(destinatario, nome_obra):
    corpo = (
        f"Olá,\n\n"
        f"A solicitação da obra {nome_obra} foi aprovada.\n\n"
        f"As pessoas informadas entraram na fila de cadastro do robô.\n"
    )
    return _enviar(destinatario, f"Obra aprovada - {nome_obra}", corpo)


def avisar_obra_concluida(destinatario, nome_obra):
    corpo = (
        f"Olá,\n\n"
        f"A obra {nome_obra} foi concluída no CF Obras.\n\n"
        f"Obra, estrutura e acessos das pessoas já estão no sistema.\n"
    )
    return _enviar(destinatario, f"Obra concluída - {nome_obra}", corpo)


def avisar_obra_recusada(destinatario, nome_obra, motivo):
    corpo = (
        f"Olá,\n\n"
        f"A solicitação da obra {nome_obra} foi recusada.\n\n"
        f"Motivo: {motivo}\n\n"
        f"Corrija os dados e reenvie a solicitação pela Central de Ajuda.\n"
    )
    return _enviar(destinatario, f"Obra recusada - {nome_obra}", corpo)