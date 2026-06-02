import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

def gerar_resposta(pergunta, texto_manual):

    groq_key = os.getenv("GROQ_API_KEY")
    groq = Groq(api_key=groq_key)

    try:
        chat = groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "Você é um assistente do sistema CF Obras. "
                               "Responda SOMENTE usando as informações fornecidas no contexto. "
                               "Se a resposta não estiver no contexto, responda exatamente: Não sei."
                },
                {
                    "role": "user",
                    "content": f"CONTEXTO: {texto_manual} - PERGUNTA: {pergunta}"
                }
            ]
        )

        resposta = chat.choices[0].message.content
        return resposta
    except:
        return "Desculpe, ocorreu um erro ao gerar a resposta. Por favor, tente novamente mais tarde."