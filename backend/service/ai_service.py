import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

def gerar_resposta(pergunta, texto_manual, historico):

    groq_key = os.getenv("GROQ_API_KEY")
    groq = Groq(api_key=groq_key)

    try:
        historico_dicts = []

        for msg in historico:
            historico_dicts.append({"role": msg.papel, "content": msg.texto})

        messages = (
            [{
                "role": "system",
                "content":
                    "Você é o assistente virtual do CF Obras, que ajuda colaboradores a usar o sistema no dia a dia. "
                    "Use APENAS as informações do contexto. Se a resposta não estiver lá, responda exatamente: Não sei. "
                    "SEJA BREVE — essa é a regra mais importante. Responda em 2 a 4 frases por padrão, resumindo e indo direto ao ponto. NUNCA copie trechos longos do manual. "
                    "Se a dúvida for sobre um processo de vários passos, dê um resumo de 1 frase e pergunte se a pessoa quer o passo a passo completo — só liste todos os passos se ela pedir. "
                    "Se a pessoa estiver no meio de um processo e perguntar algo pontual, responda só aquela parte. "
                    "Use linguagem simples e amigável, e não repita o que já foi dito."

            }]
            + historico_dicts +
            [{
                "role": "user",
                "content": f"CONTEXTO: {texto_manual} - PERGUNTA: {pergunta}"
            }]
        )
        chat = groq.chat.completions.create(model="llama-3.3-70b-versatile", messages=messages)

        resposta = chat.choices[0].message.content
        return resposta
    except:
        return "Desculpe, ocorreu um erro ao gerar a resposta. Por favor, tente novamente mais tarde."