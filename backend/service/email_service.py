import os
import requests

BREVO_API_KEY = os.getenv("BREVO_API_KEY")
EMAIL_REMETENTE = os.getenv("EMAIL_REMETENTE")
NOME_REMETENTE = os.getenv("NOME_REMETENTE", "CF Obras")

URL_BREVO = "https://api.brevo.com/v3/smtp/email"
URL_CF_OBRAS = "https://manager.cfobras.com.br"
URL_CENTRAL = os.getenv("URL_CENTRAL", "https://central-cfobras.vercel.app")

NAVY = "#0d3b66"
CINZA_TEXTO = "#374151"
CINZA_CLARO = "#6b7280"
BORDA = "#e5e7eb"
FUNDO = "#f5f6f8"

ASSINATURA_NOME = "Central de Ajuda"
ASSINATURA_EMPRESA = "Controle Fácil de Obras"


def _bloco_html(paragrafos):
    return "".join(
        f'<p style="margin:0 0 14px;font-size:15px;line-height:1.6;color:{CINZA_TEXTO}">{p}</p>'
        for p in paragrafos if p
    )


def _caixa_html(linhas):
    if not linhas:
        return ""

    itens = "".join(
        f'<tr>'
        f'<td style="padding:4px 0;font-size:13px;color:{CINZA_CLARO};white-space:nowrap">{rotulo}</td>'
        f'<td style="padding:4px 0 4px 14px;font-size:14px;color:{NAVY};font-weight:600;'
        f'font-family:Consolas,Monaco,monospace">{valor}</td>'
        f'</tr>'
        for rotulo, valor in linhas
    )

    return (
        f'<table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" '
        f'style="background:{FUNDO};border:1px solid {BORDA};border-radius:8px;margin:0 0 18px">'
        f'<tr><td style="padding:16px 20px">'
        f'<table role="presentation" cellpadding="0" cellspacing="0" border="0">{itens}</table>'
        f'</td></tr></table>'
    )


AVISO_TESTE = (
    '<tr><td style="background:#fef3c7;border-bottom:1px solid #fcd34d;'
    'padding:12px 28px;font-size:13px;color:#92400e;font-weight:600">'
    'MENSAGEM DE TESTE — enviada pelo painel de administracao. '
    'Nenhuma solicitacao real foi criada. Ignore este e-mail.'
    '</td></tr>'
)


def _montar_html(titulo, paragrafos, caixa=None, rodape_extra=None, html_extra=None, teste=False):
    return (
        f'<!DOCTYPE html><html lang="pt-BR"><head><meta charset="utf-8">'
        f'<meta name="viewport" content="width=device-width,initial-scale=1"></head>'
        f'<body style="margin:0;padding:0;background:{FUNDO};'
        f'font-family:Segoe UI,Helvetica,Arial,sans-serif">'
        f'<table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" '
        f'style="background:{FUNDO};padding:24px 12px">'
        f'<tr><td align="center">'
        f'<table role="presentation" cellpadding="0" cellspacing="0" border="0" width="600" '
        f'style="max-width:600px;width:100%;background:#ffffff;border:1px solid {BORDA};'
        f'border-radius:10px;overflow:hidden">'
        f'<tr><td style="background:{NAVY};padding:18px 28px">'
        f'<span style="font-size:16px;font-weight:700;color:#ffffff">CF Obras</span>'
        f'<span style="font-size:14px;color:#a9c2db"> &middot; Central de Ajuda</span>'
        f'</td></tr>'
        f'{AVISO_TESTE if teste else ""}'
        f'<tr><td style="padding:28px">'
        f'<h1 style="margin:0 0 18px;font-size:19px;line-height:1.3;color:{NAVY};'
        f'font-weight:700">{titulo}</h1>'
        f'{_bloco_html(paragrafos)}'
        f'{_caixa_html(caixa)}'
        f'{html_extra or ""}'
        f'</td></tr>'
        f'<tr><td style="padding:0 28px"><div style="border-top:1px solid {BORDA}"></div></td></tr>'
        f'<tr><td style="padding:18px 28px 24px">'
        f'<p style="margin:0 0 4px;font-size:14px;font-weight:600;color:{NAVY}">{ASSINATURA_NOME}</p>'
        f'<p style="margin:0 0 12px;font-size:13px;color:{CINZA_CLARO}">{ASSINATURA_EMPRESA}</p>'
        f'<p style="margin:0;font-size:12px;line-height:1.6;color:{CINZA_CLARO}">'
        f'Este e-mail foi enviado automaticamente. Nao responda esta mensagem.<br>'
        f'Para acompanhar suas solicitacoes, acesse a '
        f'<a href="{URL_CENTRAL}" style="color:{NAVY}">Central de Ajuda</a>.'
        f'{"<br>" + rodape_extra if rodape_extra else ""}'
        f'</p></td></tr>'
        f'</table></td></tr></table></body></html>'
    )


def _montar_texto(titulo, paragrafos, caixa=None, rodape_extra=None, teste=False):
    import re

    limpos = [re.sub(r"<[^>]+>", "", p) for p in paragrafos if p]
    partes = []
    if teste:
        partes += ["*** MENSAGEM DE TESTE - ignore este e-mail ***", ""]
    partes += [titulo, "", "\n\n".join(limpos)]

    if caixa:
        partes.append("")
        partes.extend(f"{rotulo}: {valor}" for rotulo, valor in caixa)

    partes.extend([
        "",
        "-" * 40,
        ASSINATURA_NOME,
        ASSINATURA_EMPRESA,
        "",
        "Este e-mail foi enviado automaticamente. Nao responda esta mensagem.",
        f"Para acompanhar suas solicitacoes, acesse: {URL_CENTRAL}",
    ])

    if rodape_extra:
        partes.append(rodape_extra)

    return "\n".join(partes)


def _enviar(destinatario, assunto, titulo, paragrafos, caixa=None, rodape_extra=None,
            html_extra=None, teste=False):
    if not destinatario:
        print("E-mail nao enviado: destinatario vazio")
        return False

    if not BREVO_API_KEY or not EMAIL_REMETENTE:
        print(f"Brevo nao configurado. E-mail que iria para {destinatario}: {assunto}")
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
                "to": [{"email": e.strip()} for e in destinatario.split(",") if e.strip()],
                "subject": (f"[TESTE] {assunto}" if teste else assunto),
                "htmlContent": _montar_html(titulo, paragrafos, caixa, rodape_extra,
                                            html_extra, teste),
                "textContent": _montar_texto(titulo, paragrafos, caixa, rodape_extra, teste),
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


def avisar_recusa(destinatario, nome_colaborador, motivo, teste=False):
    return _enviar(
        destinatario,
        f"Solicitacao recusada - {nome_colaborador}",
        "Solicitacao recusada",
        [
            f"A solicitacao de cadastro de <b>{nome_colaborador}</b> no CF Obras foi recusada.",
            f"<b>Motivo:</b> {motivo}",
            "Corrija os dados e envie a solicitacao novamente pela Central de Ajuda.",
        ],
        teste=teste,
    )


def avisar_cadastro_concluido(destinatario, nome_colaborador, senha_inicial, teste=False):
    return _enviar(
        destinatario,
        "Seu acesso ao CF Obras foi criado",
        "Seu acesso foi criado",
        [
            f"Ola, {nome_colaborador}.",
            "Seu acesso ao CF Obras ja esta liberado. Use os dados abaixo para entrar.",
        ],
        caixa=[
            ("Endereco", URL_CF_OBRAS),
            ("Login", destinatario),
            ("Senha inicial", senha_inicial),
        ],
        rodape_extra="Troque a senha no primeiro acesso.",
        teste=teste,
    )


def avisar_erro_no_robo(destinatario, nome_colaborador, erro, teste=False):
    return _enviar(
        destinatario,
        f"Falha no cadastro - {nome_colaborador}",
        "Falha no cadastro",
        [
            f"O cadastro de <b>{nome_colaborador}</b> no CF Obras falhou.",
            f"<b>Erro:</b> {erro}",
            "Confira os dados na Central de Ajuda e reenvie a solicitacao.",
        ],
        teste=teste,
    )


def avisar_colaborador_aprovado(destinatario, nome_colaborador, teste=False):
    return _enviar(
        destinatario,
        f"Solicitacao aprovada - {nome_colaborador}",
        "Solicitacao aprovada",
        [
            f"A solicitacao de cadastro de <b>{nome_colaborador}</b> foi aprovada "
            f"e entrou na fila do robo.",
            "Voce recebe outro aviso assim que o cadastro estiver concluido.",
        ],
        teste=teste,
    )


def avisar_colaborador_vinculado(destinatario, nome_colaborador, obras, so_vinculo, teste=False):
    acao = "vinculado" if so_vinculo else "cadastrado e vinculado"
    fecho = ("A pessoa continua com a senha que ja usava."
             if so_vinculo else
             "A pessoa recebeu por e-mail o endereco, o login e a senha inicial.")

    return _enviar(
        destinatario,
        f"Cadastro concluido - {nome_colaborador}",
        "Cadastro concluido",
        [f"<b>{nome_colaborador}</b> foi {acao} no CF Obras.", fecho],
        caixa=[("Obras", obras or "-")],
        teste=teste,
    )


def avisar_obra_aprovada(destinatario, nome_obra, teste=False):
    return _enviar(
        destinatario,
        f"Obra aprovada - {nome_obra}",
        "Obra aprovada",
        [
            f"A solicitacao da obra <b>{nome_obra}</b> foi aprovada.",
            "As pessoas informadas entraram na fila de cadastro do robo.",
        ],
        teste=teste,
    )


def avisar_obra_concluida(destinatario, nome_obra, teste=False):
    return _enviar(
        destinatario,
        f"Obra concluida - {nome_obra}",
        "Obra concluida",
        [
            f"A obra <b>{nome_obra}</b> foi concluida no CF Obras.",
            "Obra, estrutura e acessos das pessoas ja estao no sistema.",
        ],
        teste=teste,
    )


def avisar_obra_recusada(destinatario, nome_obra, motivo, teste=False):
    return _enviar(
        destinatario,
        f"Obra recusada - {nome_obra}",
        "Obra recusada",
        [
            f"A solicitacao da obra <b>{nome_obra}</b> foi recusada.",
            f"<b>Motivo:</b> {motivo}",
            "Corrija os dados e reenvie a solicitacao pela Central de Ajuda.",
        ],
        teste=teste,
    )


EMAIL_RESUMO = os.getenv("EMAIL_RESUMO", "lucas.gabriel@cury.net")


def _linha_pendencia(item):
    urgente = item["prioridade"] == "urgente"
    cor = "#b42318" if urgente else CINZA_TEXTO
    peso = "700" if urgente else "500"

    dias = item["dias"]
    espera = "hoje" if dias == 0 else ("1 dia" if dias == 1 else f"{dias} dias")

    marca = ""
    if urgente:
        marca = ('<br><span style="font-size:11px;font-weight:700;'
                 'color:#b42318">URGENTE</span>')

    celula = f'padding:9px 10px;border-bottom:1px solid {BORDA}'

    return (
        f'<tr>'
        f'<td style="{celula};font-size:14px;color:{cor};font-weight:{peso}">'
        f'{item["titulo"]}{marca}</td>'
        f'<td style="{celula};font-size:13px;color:{CINZA_CLARO};white-space:nowrap">'
        f'{item["solicitante"] or "-"}</td>'
        f'<td style="{celula};font-size:13px;color:{CINZA_CLARO};white-space:nowrap">'
        f'{espera}</td>'
        f'</tr>'
    )


def _tabela_pendencias(titulo, itens):
    if not itens:
        return (f'<p style="margin:0 0 18px;font-size:14px;color:{CINZA_CLARO}">'
                f'{titulo}: nada pendente.</p>')

    cabecalho = (
        f'<tr>'
        f'<th align="left" style="padding:6px 10px;font-size:11px;letter-spacing:.04em;'
        f'text-transform:uppercase;color:{CINZA_CLARO};border-bottom:2px solid {BORDA}">Item</th>'
        f'<th align="left" style="padding:6px 10px;font-size:11px;letter-spacing:.04em;'
        f'text-transform:uppercase;color:{CINZA_CLARO};border-bottom:2px solid {BORDA}">Pediu</th>'
        f'<th align="left" style="padding:6px 10px;font-size:11px;letter-spacing:.04em;'
        f'text-transform:uppercase;color:{CINZA_CLARO};border-bottom:2px solid {BORDA}">Espera</th>'
        f'</tr>'
    )

    return (
        f'<p style="margin:0 0 8px;font-size:14px;font-weight:700;color:{NAVY}">'
        f'{titulo} ({len(itens)})</p>'
        f'<table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" '
        f'style="border-collapse:collapse;margin:0 0 22px">'
        f'{cabecalho}{"".join(_linha_pendencia(i) for i in itens)}'
        f'</table>'
    )


def avisar_pendentes(destinatario, colaboradores, obras, teste=False):
    total = len(colaboradores) + len(obras)

    if total == 0:
        corpo = ["Nao ha solicitacoes em aberto no momento."]
    else:
        urgentes = sum(1 for i in colaboradores + obras if i["prioridade"] == "urgente")
        abertura = f"Ha <b>{total}</b> solicitacao(oes) em aberto na Central de Ajuda."
        if urgentes:
            abertura += f" Dessas, <b>{urgentes}</b> marcada(s) como urgente pelo solicitante."
        corpo = [abertura]

    tabelas = (_tabela_pendencias("Cadastros de colaborador", colaboradores)
               + _tabela_pendencias("Solicitacoes de obra", obras)) if total else ""

    assunto = (f"{total} solicitacao(oes) em aberto" if total
               else "Nenhuma solicitacao em aberto")

    return _enviar(destinatario, assunto, "Solicitacoes em aberto", corpo,
                   html_extra=tabelas, teste=teste)