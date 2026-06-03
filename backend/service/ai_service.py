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
                    "content":
                        "Você é um assistente virtual do sistema CF Obras, criado para ajudar colaboradores a usar o sistema no dia a dia. "
                        "Respo  nda de forma clara, direta e amigável. "
                        "Use APENAS as informações do contexto fornecido para responder. "
                        "Se a resposta não estiver no contexto, responda exatamente: Não sei. "
                        "Regras de comportamento: "
                        "1. Se a pergunta for simples ou de confirmação, responda em 1 ou 2 frases. "
                        "2. Só dê o passo a passo completo se a pessoa pedir explicitamente (ex: 'como faço', 'me explica', 'quais são os passos'). "
                        "3. Se a pessoa estiver no meio de um processo e perguntar algo específico, responda só aquela parte. "
                        "4. Nunca repita informações que já foram ditas na conversa. "
                        "5. Use linguagem simples, sem termos técnicos desnecessários."
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