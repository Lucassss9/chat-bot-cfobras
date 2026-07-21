import os
from dotenv import load_dotenv
from notion_client import Client

load_dotenv()
notion_token = os.getenv("NOTION_TOKEN")
page_id = os.getenv("NOTION_PAGE_ID")

notion = Client(auth=notion_token, timeout_ms=30000)

TIPOS_DE_TEXTO = ["paragraph", "heading_1", "heading_2", "heading_3",
                  "bulleted_list_item", "numbered_list_item", "callout",
                  "quote", "toggle", "to_do"]


def _extrair_texto(rich_text):
    linha = ""
    for pedaco in rich_text:
        linha += pedaco.get("plain_text", "")
    return linha


def _extrair_linha_da_tabela(bloco):
    celulas = bloco.get("table_row", {}).get("cells", [])
    textos = []
    for celula in celulas:
        textos.append(_extrair_texto(celula))
    return " | ".join(textos)


def buscar_pagina(id_alvo=None, profundidade=0):
    if profundidade > 10:
        return ""

    try:
        texto_da_pagina = ""
        id_atual = page_id if id_alvo is None else id_alvo
        cursor = None

        while True:
            response = notion.blocks.children.list(block_id=id_atual, start_cursor=cursor)
            blocos = response.get("results", [])

            for bloco in blocos:
                id_do_bloco = bloco.get("id")
                tipo_do_bloco = bloco.get("type")

                if tipo_do_bloco == "table_row":
                    linha = _extrair_linha_da_tabela(bloco)
                    if linha.strip():
                        texto_da_pagina += linha + "\n"
                    continue

                if tipo_do_bloco in TIPOS_DE_TEXTO:
                    linha = _extrair_texto(bloco.get(tipo_do_bloco, {}).get("rich_text", []))
                    if linha.strip():
                        texto_da_pagina += linha + "\n"

                if bloco.get("has_children"):
                    try:
                        texto_da_pagina += buscar_pagina(id_alvo=id_do_bloco,
                                                         profundidade=profundidade + 1)
                    except Exception as erro_filho:
                        print(f"Erro ao ler os filhos do bloco {id_do_bloco}: {erro_filho}")

            if not response.get("has_more"):
                break
            cursor = response.get("next_cursor")

        return texto_da_pagina

    except Exception as erro:
        print(f"O erro real que aconteceu na página foi: {erro}")
        return ""