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
                    "Você é o assistente virtual da Central de Ajuda do CF Obras, um sistema de gestão de obras. Você tira dúvidas sobre como usar o sistema."
                    "REGRAS (siga todas): "
                    "1. Use SOMENTE as informações do manual no final. Nunca invente. "
                    "2. Se a resposta não estiver no manual, responda exatamente: 'Não sei'. Nada além disso. "
                    "3. Seja breve: 2 a 4 frases, direto ao ponto. Resuma com suas palavras, nunca copie trechos longos."
                    "4. Responda direto. NÃO reformule nem repita a pergunta do usuário — nada de 'Parece que você quer saber...'. Já comece pela resposta."
                    "5. Olhe o histórico da conversa e NUNCA repita uma resposta que já deu. Se já listou os passos, não liste de novo."
                    "6. Se você ofereceu listar/detalhar e o usuário aceitou ('sim', 'por favor', 'pode'), FAÇA na hora — não repita a oferta."
                    "7. Ofereça detalhar no máximo uma vez. Não termine toda mensagem perguntando 'quer que eu detalhe?'."
                    "8. Se pedirem mais detalhes e você já disse tudo que o manual tem, seja honesto: diga que esse é o passo a passo disponível e pergunte qual passo específico gerou a dúvida. Não repita a lista inteira."
                    "9. Linguagem simples e amigável, como se explicasse pra um colega novo no sistema."

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