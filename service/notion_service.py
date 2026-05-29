import os
from dotenv import load_dotenv
from notion_client import Client
from notion_client.helpers import iterate_paginated_api

def buscar_pagina():
    
    load_dotenv()

    lista_de_subpaginas = []

    notion_token = os.getenv("NOTION_TOKEN")
    page_id = os.getenv("NOTION_PAGE_ID")

    notion = Client(auth=notion_token)

    try:
        response = notion.blocks.children.list(block_id=page_id)
        paginas = response.get("results", [])

        for bloco in paginas:
            id_do_bloco = bloco.get("id")
            tipo_do_bloco = bloco.get("type")

            if tipo_do_bloco == "child_page":
                id_da_pagina = id_do_bloco
                lista_de_subpaginas.append(id_da_pagina)

        for id_subpagina in lista_de_subpaginas:
            response_subpagina = notion.blocks.children.list(block_id=id_subpagina)
            subpaginas = response_subpagina.get("results", [])
            print("==================================")
            print(f"{len(subpaginas)} subpáginas encontradas para a página com ID: {id_subpagina}")

            for subpagina in subpaginas:
                id_da_subpagina = subpagina.get("id")
                tipo_da_subpagina = subpagina.get("type")
                print(f"ID da subpágina: {id_da_subpagina}")
                print(f"Tipo da subpágina: {tipo_da_subpagina}")
            
            for bloco_conteudo in subpaginas:
                tipo_conteudo = bloco_conteudo.get("type")

                if tipo_conteudo == "paragraph":
                    texto_conteudo = bloco_conteudo.get("paragraph", {}).get("rich_text", [])


        print(lista_de_subpaginas)
    except Exception as erro:
        print(f"O erro real que aconteceu foi: {erro}")

buscar_pagina()