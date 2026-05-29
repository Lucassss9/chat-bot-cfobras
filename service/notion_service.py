import os
from dotenv import load_dotenv
from notion_client import Client
from notion_client.helpers import iterate_paginated_api

def buscar_pagina():
    load_dotenv()

    notion_token = os.getenv("NOTION_TOKEN")
    page_id = os.getenv("NOTION_PAGE_ID")

    notion = Client(auth=notion_token)

    try:
        response = notion.blocks.children.list(block_id=page_id)
        paginas = response.get("results", [])

        print(f"Total de blocos encontrados: {len(paginas)}\n")

    except:
        print("Paginas não encontradas")

buscar_pagina()