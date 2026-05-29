import os
from dotenv import load_dotenv
from notion_client import Client
from notion_client.helpers import iterate_paginated_api

def buscar_pagina(id_alvo=None):
    
    load_dotenv()

    notion_token = os.getenv("NOTION_TOKEN")
    page_id = os.getenv("NOTION_PAGE_ID")

    notion = Client(auth=notion_token)

    try:
        lista_de_subpaginas = []
        tipos_de_texto = ["paragraph", "heading_1", "heading_2", "heading_3", "bulleted_list_item", "numbered_list_item", "callout"]
        texto_da_pagina = ""

        if id_alvo == None:
            response = notion.blocks.children.list(block_id=page_id)
        else:
            response = notion.blocks.children.list(block_id=id_alvo)
        
        paginas = response.get("results", [])

        for bloco in paginas:
            id_do_bloco = bloco.get("id")
            tipo_do_bloco = bloco.get("type")

            if tipo_do_bloco == "child_page":
                titulo_da_pagina = bloco.get("child_page", {}).get("title")
                lista_de_subpaginas.append({"id": id_do_bloco, "titulo": titulo_da_pagina})
                buscar_pagina(id_alvo=id_do_bloco)


            if tipo_do_bloco in tipos_de_texto:
                texto = bloco.get(tipo_do_bloco, {}).get("rich_text", [])
                
                if texto == []:
                    continue
            
                texto_da_pagina += texto[0].get("plain_text") + "\n"


        print(lista_de_subpaginas)
        print(f"--- CONTEÚDO DA PÁGINA ({id_alvo}): ---")
        print(texto_da_pagina)
    except Exception as erro:
        print(f"O erro real que aconteceu foi: {erro}")

buscar_pagina()