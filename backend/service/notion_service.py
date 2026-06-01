import os
from dotenv import load_dotenv
from notion_client import Client

load_dotenv()
notion_token = os.getenv("NOTION_TOKEN")
page_id = os.getenv("NOTION_PAGE_ID")

notion = Client(auth=notion_token, timeout=30000)

def buscar_pagina(id_alvo=None):
    try:
        lista_de_subpaginas = []
        tipos_de_texto = ["paragraph", "heading_1", "heading_2", "heading_3", "bulleted_list_item", "numbered_list_item", "callout", "quote"]
        texto_da_pagina = ""

        id_atual = page_id if id_alvo is None else id_alvo
        
        response = notion.blocks.children.list(block_id=id_atual)
        paginas = response.get("results", [])

        for bloco in paginas:
            id_do_bloco = bloco.get("id")
            tipo_do_bloco = bloco.get("type")

            if tipo_do_bloco == "child_page":
                titulo_da_pagina = bloco.get("child_page", {}).get("title")
                lista_de_subpaginas.append({"id": id_do_bloco, "titulo": titulo_da_pagina})

                try:
                    texto_da_pagina += buscar_pagina(id_alvo=id_do_bloco)
                except Exception as erro_sub:
                    print(f"Erro ao ler a subpágina {titulo_da_pagina}: {erro_sub}")

            if tipo_do_bloco in tipos_de_texto:
                linha_completa = ""
                texto = bloco.get(tipo_do_bloco, {}).get("rich_text", [])

                if texto == []:
                    continue
                
                for pedacos in texto:
                    linha_completa += pedacos.get("plain_text")

                texto_da_pagina += linha_completa + "\n"
        
        return texto_da_pagina
    except Exception as erro:
        print(f"O erro real que aconteceu na página foi: {erro}")
        return ""