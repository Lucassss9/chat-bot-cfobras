import os
from dotenv import load_dotenv
from groq import Groq

def gerar_resposta(pergunta, texto_manual):
    load_dotenv()

    groq_key = os.getenv("GROQ_API_KEY")
    groq = Groq(api_key=groq_key)

    try:
        chat = groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            message=[
                {
                    "role": "system",
                    "content": f"Você é um assistente de IA que responde perguntas com base em um texto fornecido em {texto_manual}. Use apenas as informações do texto para responder às perguntas. Se a resposta não estiver no texto, diga que não sabe."
                },
                {
                    "role": "user",
                    "content": pergunta
                }
            ]
        )
    except:
        return "Desculpe, ocorreu um erro ao gerar a resposta. Por favor, tente novamente mais tarde."
    
    return chat.choices[0].message.content