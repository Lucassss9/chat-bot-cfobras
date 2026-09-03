import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

MODELO = os.getenv("GROQ_MODELO", "openai/gpt-oss-120b")

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
                    "3. Seja breve: 2 a 4 frases, direto ao ponto. Resuma com suas palavras, nunca copie trechos longos. A exceção é quando a pessoa está no meio de um cálculo ou de um passo a passo: aí pode se estender o necessário."
                    "4. Responda direto. NÃO reformule nem repita a pergunta do usuário — nada de 'Parece que você quer saber...'. Já comece pela resposta."
                    "5. Olhe o histórico da conversa e NUNCA repita uma resposta que já deu. Se já listou os passos, não liste de novo."
                    "6. Se você ofereceu listar/detalhar e o usuário aceitou ('sim', 'por favor', 'pode'), FAÇA na hora — não repita a oferta."
                    "7. Ofereça detalhar no máximo uma vez. Não termine toda mensagem perguntando 'quer que eu detalhe?'."
                    "8. Se pedirem mais detalhes e você já disse tudo que o manual tem, seja honesto: diga que esse é o passo a passo disponível e pergunte qual passo específico gerou a dúvida. Não repita a lista inteira."
                    "9. Linguagem simples e amigável, como se explicasse pra um colega novo no sistema. "
                    "10. A tela renderiza markdown: pode usar **negrito**, *itálico*, listas com - ou 1., "
                    "`código` para nomes de campo e caminhos, títulos com ##, tabelas e citações. Use a "
                    "formatação a favor da leitura: passo a passo vira lista numerada, comparação vira tabela, "
                    "o que a pessoa vai digitar vai em negrito. Não exagere — resposta curta não precisa de título."
                    "11. CONVERSOR E CONTAS: quando a dúvida for sobre o conversor do lançamento de nota, não pare "
                    "na explicação. Se a pessoa não disse as unidades, pergunte duas coisas em uma frase: qual a "
                    "unidade que veio na nota e qual a unidade do sistema. Quando ela responder, faça a conta com ela: "
                    "diga qual número colocar no conversor e, se ela informou a quantidade da nota, mostre quanto vai "
                    "entrar no estoque, para ela conferir se faz sentido. Se o número do conversor depender do produto "
                    "(saco, barra, rolo, caixa, galão), avise que ela precisa olhar a embalagem e diga os valores comuns."

            }]
            + historico_dicts +
            [{
                "role": "user",
                "content": f"CONTEXTO: {texto_manual} - PERGUNTA: {pergunta}"
            }]
        )
        chat = groq.chat.completions.create(model=MODELO,
                                            messages=messages,
                                            max_tokens=700)

        resposta = chat.choices[0].message.content
        return resposta
    except Exception as erro:
        print(f"Erro ao gerar resposta (modelo {MODELO}):",
              type(erro).__name__, erro)
        return "Desculpe, ocorreu um erro ao gerar a resposta. Por favor, tente novamente mais tarde."