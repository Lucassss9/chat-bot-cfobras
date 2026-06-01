from service.ai_service import gerar_resposta
from service.notion_service import buscar_pagina

print("Passo 1: O main.py começou a rodar!")

print("Passo 2: Chamando o Notion (aguarde)...")
manual_da_obra = buscar_pagina()
print(f"Notion respondeu! Tamanho do texto: {len(manual_da_obra)} caracteres.")

duvida_user = "Como eu faço para cadastrar um novo funcionário para o EPI?"

print("⏳ Passo 3: Chamando o Groq com a pergunta...")
resposta = gerar_resposta(pergunta=duvida_user, texto_manual=manual_da_obra)

print("🏆 Passo 4: Resposta final do Bot:")
print(resposta)