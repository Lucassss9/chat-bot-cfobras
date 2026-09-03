from config.connection import session_local, engine, Base
from model.artigo_model import Artigo
from datetime import datetime


ARTIGOS = [
    {
        "grupo": "Primeiro acesso",
        "pergunta": "Como faço login no CF Obras?",
        "caminho": "https://manager.cfobras.com.br/login",
        "resposta": (
            "Entre em https://manager.cfobras.com.br/login com o seu e-mail e a senha.\n"
            "Se for o seu primeiro acesso, a senha é a senha padrão informada pelo suporte — "
            "troque assim que entrar.\n"
            "Ainda não tem cadastro? Use a aba Cadastro para pedir o seu acesso e aguarde a "
            "liberação, ou fale com o suporte."
        ),
    },
    {
        "grupo": "Primeiro acesso",
        "pergunta": "Esqueci minha senha, o que faço?",
        "variacoes": "esqueci a senha\nperdi a senha\nnao consigo entrar\nsenha errada\nresetar senha\nnao lembro a senha",
        "caminho": None,
        "resposta": (
            "Você não consegue redefinir sozinho. Entre em contato com o suporte pedindo o "
            "reset da senha."
        ),
    },
    {
        "grupo": "Primeiro acesso",
        "pergunta": "Como troco a obra em que estou trabalhando?",
        "variacoes": "trocar de obra\nmudar obra\ntroca de filial\nestou na obra errada",
        "caminho": "Seletor de filial, no topo da tela",
        "resposta": (
            "Se você tem mais de uma filial liberada, clique no seletor de filial no topo, "
            "à direita, e escolha a que quiser.\n"
            "Se a filial que você precisa não estiver na lista, abra uma solicitação de "
            "cadastro para essa obra."
        ),
    },
    {
        "grupo": "Primeiro acesso",
        "pergunta": "Minha obra não aparece no seletor, por quê?",
        "variacoes": "minha obra nao aparece\nnao acho minha obra\nfalta obra na lista",
        "caminho": None,
        "resposta": (
            "Você não está vinculado a essa obra. Entre em contato com o suporte para pedir "
            "o vínculo."
        ),
    },
    {
        "grupo": "Primeiro acesso",
        "pergunta": "Para que serve o botão Nova Requisição no topo?",
        "caminho": "Topo da tela, ao lado do seletor de filial",
        "resposta": (
            "É um atalho para criar uma requisição sem passar pelo menu. Leva direto para o "
            "cadastro de requisição."
        ),
    },
    {
        "grupo": "Primeiro acesso",
        "pergunta": "O sistema funciona no celular?",
        "caminho": None,
        "resposta": (
            "Funciona, com as mesmas funcionalidades da versão de computador."
        ),
    },
    {
        "grupo": "Primeiro acesso",
        "pergunta": "O que o Dashboard mostra?",
        "caminho": "Dashboard",
        "resposta": (
            "Indicadores e alertas operacionais de estoque e requisições. Ele traz:\n"
            "- Total de Obras, Total de Requisições e Total de Estoque em R$;\n"
            "- Notas Recebidas x Notas Lançadas, comparando o que veio na planilha com o que "
            "foi lançado em pedido, com a diferença e o percentual de cobertura;\n"
            "- Estoque Baixo, listando obra, código e insumo, quantidade em estoque, unidade "
            "e estoque mínimo;\n"
            "- Requisições Pendentes, com código, obra, torre e pavimento, data, observação e "
            "quem pediu. Dali mesmo dá para Aprovar ou Concluir a requisição."
        ),
    },
    {
        "grupo": "Materiais",
        "pergunta": "Como faço uma requisição de material?",
        "variacoes": "requisicao\ncomo pedir material\npedir material\nfazer requisicao\ncomo requisitar\nnova requisicao\nsolicitar material",
        "destaque": True,
        "ordem": 2,
        "caminho": "Materiais > Requisição de Materiais",
        "resposta": (
            "1. Vá em Materiais > Requisição de Materiais e clique em Cadastro.\n"
            "2. Preencha Obra, Torre e Pavimento.\n"
            "3. Escreva uma observação dizendo para que é o material.\n"
            "4. Adicione os itens e salve.\n\n"
            "Depois de salvar, a requisição fica aguardando aprovação da equipe de apoio: "
            "engenheiros (de estagiário a residente), mestre, contramestre e encarregado. "
            "O residente é quem consegue aprovar e concluir."
        ),
    },
    {
        "grupo": "Materiais",
        "pergunta": "Como acompanho o andamento da minha requisição?",
        "caminho": "Materiais > Requisição de Materiais",
        "resposta": (
            "A lista de Requisição de Materiais mostra o status de cada uma. As pendentes "
            "também aparecem no Dashboard, com os botões de Aprovar e Concluir."
        ),
    },
    {
        "grupo": "Materiais",
        "pergunta": "Dá para cancelar uma requisição já enviada?",
        "caminho": "Materiais > Requisição de Materiais",
        "resposta": (
            "Dá. Basta excluir a requisição na tela de Requisição de Materiais. Ela vai para "
            "a Lixeira de Requisições e pode ser recuperada."
        ),
    },
    {
        "grupo": "Materiais",
        "pergunta": "Minha requisição sumiu, onde encontro?",
        "variacoes": "sumiu a requisicao\nrequisicao desapareceu\nnao acho minha requisicao\nexclui sem querer\nlixeira",
        "caminho": "Materiais > Lixeira de Requisições",
        "resposta": (
            "Se ela foi excluída, está na Lixeira de Requisições.\n"
            "Atenção: só residente, gerente de obra e gerente geral de obra conseguem ver "
            "essa tela."
        ),
    },
    {
        "grupo": "Materiais",
        "pergunta": "Dá para recuperar uma requisição apagada?",
        "caminho": "Materiais > Lixeira de Requisições",
        "resposta": (
            "Dá. A requisição excluída fica na Lixeira de Requisições e pode ser restaurada "
            "de lá."
        ),
    },
    {
        "grupo": "Materiais",
        "pergunta": "O insumo que preciso não aparece na requisição, o que faço?",
        "variacoes": "insumo nao aparece\nnao acho o material na requisicao\nfalta material na lista\nnao tem o insumo",
        "caminho": "Materiais > Requisição de Materiais",
        "resposta": (
            "Primeiro verifique se existe estoque desse insumo na obra — só aparece na "
            "requisição o que tem estoque.\n"
            "Se não tem estoque mas a nota com esse insumo já foi lançada, fale com o "
            "suporte para verificar."
        ),
    },
    {
        "grupo": "Materiais",
        "pergunta": "Como uso um kit dentro de uma requisição?",
        "caminho": "Materiais > Requisição de Materiais",
        "resposta": (
            "Em Requisição de Materiais, clique em Cadastro, preencha os dados como em "
            "qualquer requisição e clique em Adicionar Kit em vez de adicionar item a item."
        ),
    },
    {
        "grupo": "Materiais",
        "pergunta": "Como dou entrada em material que chegou?",
        "variacoes": "lancar nota\nlancamento de nota\ncomo lanco a nota fiscal\ndar entrada\nchegou material como faco\nentrada de material\nlancar nf\nrecebimento",
        "destaque": True,
        "ordem": 3,
        "caminho": "Materiais > Recebimento de materiais",
        "resposta": (
            "Existem dois tipos de lançamento: automatizado e manual.\n\n"
            "AUTOMATIZADO (quando existe pedido)\n"
            "1. Informe o número do PEDIDO e clique em Buscar. Só funciona com pedido.\n"
            "2. A nota tem que bater com o pedido. Se tiver qualquer item diferente, você "
            "vai precisar fazer o lançamento manual.\n"
            "3. Informe a quantidade que chegou de cada item e selecione os itens.\n"
            "4. Clique em Vincular Nota Fiscal. Você pode enviar o XML da nota (opção Upload) "
            "ou digitar a chave de acesso e o número da nota (opção Manual).\n"
            "5. Informe a data de recebimento e finalize.\n\n"
            "MANUAL\n"
            "1. Precisa do XML da nota. Se não tiver, dá para baixar em sites de consulta de "
            "DANFE. Tem que ser o XML, não o PDF.\n"
            "2. Anexe o XML e avance.\n"
            "3. Selecione a obra e informe o número do pedido ou do contrato. Avance.\n"
            "4. Vão aparecer os itens da nota. Aqui você precisa informar o código de cada "
            "insumo.\n"
            "5. Confira o conversor de cada item (veja o artigo sobre o conversor no "
            "recebimento).\n"
            "6. Avance e conclua.\n\n"
            "Nos dois tipos, depois de concluir ainda é preciso APROVAR a nota.\n\n"
            "ATENÇÃO: confira sempre se a descrição do insumo do sistema bate com a "
            "descrição da nota, e se o conversor foi preenchido corretamente. Erro nessas "
            "duas coisas entra no estoque errado e prejudica a obra."
        ),
    },
    {
        "grupo": "Materiais",
        "pergunta": "Onde encontro o código do insumo para lançar a nota?",
        "variacoes": "codigo do insumo\nonde acho o codigo\nnao acho o codigo do insumo\nqual o codigo do material\ninsumo inativo\nnao aparece o insumo pra lancar",
        "destaque": True,
        "ordem": 5,
        "caminho": "Materiais > Recebimento de materiais",
        "resposta": (
            "O código do insumo pode ser encontrado em:\n"
            "- análise do pedido, emissão do pedido ou emissão do contrato, pelo Sienge;\n"
            "- banco de insumos em https://job.eng.br/insumos-publico.html, filtrando pela "
            "tabela da obra.\n\n"
            "Se não souber qual é a tabela da obra, pergunte ao suporte.\n"
            "Se o insumo não aparecer ou estiver inativo, fale com o suporte para verificar."
        ),
    },
    {
        "grupo": "Materiais",
        "pergunta": "Como funciona o conversor no lançamento da nota?",
        "variacoes": "conversor\no que coloco no conversor\ncomo faz a conversao\nnota veio em rolo e o sistema em metro\nveio em tonelada e preciso em kg\ncomo converter a unidade da nota\nsaco de cimento pra kg\nnao sei o que por no conversor",
        "destaque": True,
        "ordem": 1,
        "caminho": "Materiais > Recebimento de materiais",
        "resposta": (
            "O conversor traduz a unidade da nota fiscal para a unidade que o sistema usa. "
            "Ele fica no lançamento, em Materiais > Recebimento de materiais, e aparece para "
            "cada insumo da nota.\n\n"
            "O NÚMERO QUE VAI NO CAMPO\n"
            "É a resposta desta pergunta: 1 unidade da nota equivale a quantos da unidade do "
            "sistema? Se as duas unidades forem iguais, o conversor é 1.\n\n"
            "ALGUMAS CONVERSÕES SÃO SEMPRE IGUAIS\n"
            "Porque são definição: 1 tonelada são 1000 kg, 1 milheiro são 1000 unidades, "
            "1 dúzia são 12, 1 m³ são 1000 litros, 1 kg são 1000 g, 1 litro são 1000 ml. "
            "Nesses casos o número não muda nunca.\n\n"
            "AS OUTRAS DEPENDEM DO PRODUTO E PRECISAM SER CONFERIDAS\n"
            "Saco, barra, rolo, caixa, galão, lata, fardo, pacote, peça: o número está na "
            "embalagem ou na descrição do item dentro da nota. Não existe valor padrão — saco "
            "de cimento costuma ter 50 kg, mas o de argamassa costuma ter 20, e barra de aço "
            "vem de 6 ou de 12 metros dependendo da bitola. Confira sempre, item por item.\n\n"
            "CONFIRA ANTES DE CONCLUIR\n"
            "Multiplique a quantidade da nota pelo conversor. Esse é o número que vai entrar "
            "no estoque. Se chegaram 10 rolos e o conversor é 50, entram 500 metros. Se o "
            "resultado não fizer sentido para o que você recebeu, o conversor está errado.\n\n"
            "Errar o conversor faz entrar quantidade errada no estoque — ele fica inflado ou "
            "zerado sem motivo, e a obra sente depois.\n\n"
            "A aba Ajuda tem uma calculadora que faz essa conta."
        ),
    },
    {
        "grupo": "Materiais",
        "pergunta": "Errei a quantidade no recebimento, como corrijo?",
        "variacoes": "errei a quantidade\nlancei errado\nquantidade errada na nota\ncomo corrigir lancamento\nlancei a nota errada",
        "caminho": None,
        "resposta": (
            "Só o suporte consegue corrigir um recebimento já lançado. Entre em contato "
            "informando o número da nota e o que ficou errado."
        ),
    },
    {
        "grupo": "Materiais",
        "pergunta": "O que aparece na tela de Pedidos?",
        "caminho": "Materiais > Pedidos",
        "resposta": (
            "A tela puxa todos os pedidos do Sienge. Por ela você consegue programar a "
            "entrega de materiais para a obra — basta ter o e-mail do fornecedor."
        ),
    },
    {
        "grupo": "Materiais",
        "pergunta": "Como vejo o estoque da obra?",
        "variacoes": "estoque\nver estoque\nquanto tem no estoque\nsaldo de estoque\nestoque da obra",
        "caminho": "Materiais > Cadastro de Estoque, ou Relatórios > Estoques",
        "resposta": (
            "Por Materiais > Cadastro de Estoque você vê o estoque da obra na tela.\n\n"
            "Por Relatórios > Estoques você tira o relatório: selecione a obra, escolha "
            "Quantitativo, use um período longo e gere."
        ),
    },
    {
        "grupo": "Materiais",
        "pergunta": "Qual a diferença entre Acompanhamento de Estoque e Cadastro de Estoque?",
        "variacoes": "diferenca entre acompanhamento e cadastro de estoque\nqual usar pra ver estoque\nacompanhamento ou cadastro",
        "caminho": "Materiais",
        "resposta": (
            "Cadastro de Estoque mostra o estoque da obra inteira.\n"
            "Acompanhamento de Estoque serve para acompanhar um material específico ao longo "
            "do tempo."
        ),
    },
    {
        "grupo": "Materiais",
        "pergunta": "O estoque está errado, como ajusto?",
        "variacoes": "estoque errado\nestoque nao bate\najustar estoque\nsobrou material no sistema\nfalta material no sistema",
        "caminho": "Materiais > Requisição de Materiais",
        "resposta": (
            "Você pode fazer uma requisição de ajuste para acertar a quantidade. Se não tiver "
            "certeza do que fazer, peça orientação ao suporte antes — ajuste errado piora o "
            "problema."
        ),
    },
    {
        "grupo": "Materiais",
        "pergunta": "O que é Material Disponível?",
        "caminho": "Materiais > Material Disponível",
        "resposta": (
            "É a vitrine de material parado. A obra publica ali o que tem sobrando, e outras "
            "obras que precisarem podem pedir. Serve para aproveitar material parado em vez "
            "de comprar de novo."
        ),
    },
    {
        "grupo": "Materiais",
        "pergunta": "Para que serve a Quantidade Máxima?",
        "caminho": "Materiais > Quantidade Máxima",
        "resposta": (
            "O residente ou a engenharia define quanto de um material pode ser usado em "
            "determinado pavimento ou torre.\n"
            "Se a requisição passar dessa quantidade, só o residente pode aprovar a saída "
            "do material."
        ),
    },
    {
        "grupo": "Materiais",
        "pergunta": "Como defino o estoque mínimo de um item?",
        "variacoes": "estoque minimo\nminimo do insumo\nalerta de estoque\ncolocar minimo",
        "caminho": "Materiais > Estoque Mínimo",
        "resposta": (
            "Procure o insumo na tela de Estoque Mínimo e informe a quantidade mínima que a "
            "obra precisa ter.\n\n"
            "Quando o item ficar abaixo desse valor, um e-mail é enviado no fim do dia para "
            "as pessoas cadastradas nos alertas. Para incluir alguém nessa lista de alertas, "
            "peça ao suporte."
        ),
    },
    {
        "grupo": "Materiais",
        "pergunta": "O que acontece quando o item fica abaixo do estoque mínimo?",
        "caminho": "Materiais > Estoque Mínimo",
        "resposta": (
            "Todo fim de dia é enviado um e-mail para as pessoas cadastradas nos alertas, "
            "avisando dos itens abaixo do mínimo. Os itens também aparecem no bloco Estoque "
            "Baixo do Dashboard.\n"
            "Para colocar um e-mail na lista de alertas, peça ao suporte."
        ),
    },
    {
        "grupo": "Materiais",
        "pergunta": "Como uso o conversor de unidades?",
        "variacoes": "conversor de unidade\nmudar unidade da requisicao\ndeixar cimento em saco pra requisitar\ntrocar unidade do insumo",
        "destaque": True,
        "ordem": 6,
        "caminho": "Materiais > Conversor de Unidades",
        "resposta": (
            "Este conversor serve para facilitar a REQUISIÇÃO, e é diferente do conversor do "
            "lançamento de nota.\n\n"
            "O almoxarife cadastra aqui, por exemplo, que o cimento é requisitado em saco em "
            "vez de kg. Quem for requisitar vai ver saco na tela, mas o estoque continua "
            "sendo controlado em kg.\n\n"
            "Ou seja: muda só a unidade que aparece na hora de pedir, não a unidade em que o "
            "material é controlado."
        ),
    },
    {
        "grupo": "Materiais",
        "pergunta": "Como crio um kit de insumos?",
        "variacoes": "kit\ncriar kit\nmontar kit\nkit de material\nkits v2",
        "destaque": True,
        "ordem": 8,
        "caminho": "Materiais > Kits V2",
        "resposta": (
            "1. Vá em Materiais > Kits V2 e clique em criar novo kit.\n"
            "2. Preencha os campos obrigatórios: Código do Kit, Obra e Descrição.\n"
            "3. Se quiser, informe a Apropriação (subetapa do orçamento), o Estoque Mínimo do "
            "kit e uma Observação.\n"
            "4. Se o kit for por tipologia de apartamento, ligue a chave Criar Kit por "
            "Tipologia de Apartamento.\n"
            "5. Em Insumos do Kit, busque os insumos da obra por código ou descrição e "
            "adicione à composição.\n"
            "6. Em Composição do Kit, informe a quantidade por kit de cada insumo. O sistema "
            "calcula o valor total e quantos Kits Possíveis dá para montar com o estoque "
            "atual.\n"
            "7. Clique em Salvar Kit V2.\n\n"
            "Se a lista de insumos vier vazia, é porque nenhuma obra foi selecionada.\n"
            "Em caso de dúvida, fale com o suporte."
        ),
    },
    {
        "grupo": "Materiais",
        "pergunta": "Qual a diferença entre Kits e Kits V2?",
        "caminho": "Materiais > Kits V2",
        "resposta": (
            "Use apenas o Kits V2. A tela antiga de Kits vai sair do sistema."
        ),
    },
    {
        "grupo": "Transferência",
        "pergunta": "Como transfiro material para outra obra?",
        "variacoes": "transferencia\ntransferir material\nemprestimo de material\nmandar material pra outra obra\ndoacao de material\ndevolver material pra obra",
        "destaque": True,
        "ordem": 7,
        "caminho": "Transferência > Transferência de Materiais",
        "resposta": (
            "1. Vá em Transferência > Transferência de Materiais e clique em Cadastro.\n"
            "2. Escolha o Tipo: Empréstimo, Devolução ou Doação.\n"
            "3. Selecione a obra de ORIGEM.\n"
            "4. Em DESTINO, escolha primeiro a Filial e depois a Obra — a lista de obras só "
            "carrega depois que a filial é escolhida.\n"
            "5. Informe a Data do Empréstimo e a Data Necessária de Devolução.\n"
            "6. Escreva uma observação.\n"
            "7. Clique em Adicionar Item e informe os materiais e as quantidades.\n"
            "8. Clique em Salvar.\n\n"
            "A transferência passa pelos status Pendente, Liberada, Concluída ou Cancelada. "
            "Na lista dá para filtrar por status e buscar por código, insumo ou observação."
        ),
    },
    {
        "grupo": "Transferência",
        "pergunta": "Como acompanho uma transferência que fiz?",
        "caminho": "Transferência > Transferência de Materiais",
        "resposta": (
            "A lista mostra código, tipo, rota (origem → destino), data, observação, quem "
            "cadastrou e o status.\n"
            "Use o filtro de status para ver só as pendentes, liberadas, concluídas ou "
            "canceladas. No menu de cada linha você pode Visualizar, Editar, Copiar ou "
            "Excluir."
        ),
    },
    {
        "grupo": "Equipamentos",
        "pergunta": "Como faço uma requisição de equipamento?",
        "variacoes": "requisicao de equipamento\npedir equipamento\nfuncionario pegou equipamento\ncomo registro equipamento pra funcionario\nequipamento pra terceirizado",
        "caminho": "Equipamentos > Requisição de Equipamentos",
        "resposta": (
            "1. Vá em Equipamentos > Requisição de Equipamentos e clique em Cadastro.\n"
            "2. Preencha Obra, Torre e Pavimento.\n"
            "3. Na observação, escreva o nome do funcionário que pegou o equipamento.\n"
            "4. Adicione o equipamento e salve.\n"
            "5. Na hora de concluir, o sistema pede o CPF do funcionário. Se ele já tiver "
            "cadastro, é só informar o CPF que os dados aparecem.\n"
            "6. Se não tiver cadastro, aparece uma mensagem pedindo para cadastrar. A empresa "
            "dele precisa estar cadastrada em Geral > Empresas Parceiras — é um cadastro "
            "simples.\n"
            "7. Com o CPF informado, indique o equipamento que ele pegou e conclua."
        ),
    },
    {
        "grupo": "Equipamentos",
        "pergunta": "Preciso de aprovação para requisitar equipamento?",
        "caminho": "Equipamentos > Requisição de Equipamentos",
        "resposta": (
            "A requisição de equipamentos é feita pelo almoxarife."
        ),
    },
    {
        "grupo": "Equipamentos",
        "pergunta": "Como vejo quais equipamentos estão na minha obra?",
        "caminho": "Equipamentos > Cadastro de Equipamentos",
        "resposta": (
            "Em Equipamentos > Cadastro de Equipamentos você vê os equipamentos da obra.\n"
            "Para ver especificamente os que estão em uso, use Equipamentos > Equipamentos "
            "em Uso."
        ),
    },
    {
        "grupo": "Equipamentos",
        "pergunta": "O que significa equipamento ocioso?",
        "caminho": "Equipamentos > Equipamentos Ociosos",
        "resposta": (
            "É o equipamento que está há mais de uma semana sem uso. A tela de Equipamentos "
            "Ociosos lista esses casos para você decidir se devolve ou repassa."
        ),
    },
    {
        "grupo": "Equipamentos",
        "pergunta": "Como devolvo um equipamento?",
        "caminho": "Equipamentos > Retorno de Equipamentos",
        "resposta": (
            "Use Equipamentos > Retorno de Equipamentos para registrar a devolução."
        ),
    },
    {
        "grupo": "Equipamentos",
        "pergunta": "Como registro a manutenção de um equipamento?",
        "caminho": "Equipamentos > Registro de Manutenção",
        "resposta": (
            "1. Vá em Equipamentos > Registro de Manutenção e clique em Novo Registro.\n"
            "2. Informe o equipamento, a obra, o empreiteiro, o responsável, a data e o "
            "custo.\n\n"
            "A tela mostra no topo o Total em Manutenção no período, os Registros Críticos, "
            "as Obras Atendidas e o Maior Custo.\n"
            "Você pode filtrar os registros, alternar entre a visão de Tabela e de Cards, e "
            "exportar em XLSX ou CSV."
        ),
    },
    {
        "grupo": "Equipamentos",
        "pergunta": "Como cadastro o fornecedor do equipamento?",
        "caminho": "Equipamentos > Cadastro de Fornecedor",
        "resposta": (
            "Use Equipamentos > Cadastro de Fornecedor."
        ),
    },
    {
        "grupo": "Relatórios",
        "pergunta": "Como acesso o relatório? Quais relatórios existem?",
        "variacoes": "relatorio\nrelatorios\ncomo tiro relatorio\nquero um relatorio\nonde ficam os relatorios",
        "destaque": True,
        "ordem": 4,
        "caminho": "Relatórios",
        "resposta": (
            "Não existe um relatório só — existem doze, no menu Relatórios:\n\n"
            "- Estoques: o que a obra tem em estoque\n"
            "- Entradas de Materiais: tudo que entrou no período\n"
            "- Requisições: histórico de requisições\n"
            "- Índices: consumo de um insumo por mês e por pavimento\n"
            "- QrCode: gera o QR Code de um insumo\n"
            "- Equipamentos Requisições: requisições de equipamento\n"
            "- Inventário Equipamentos: inventário dos equipamentos\n"
            "- Comunicação Visual: plaquinhas de identificação de insumo\n"
            "- Nota Fiscal: consulta de notas\n"
            "- Materiais Recebidos: o que foi recebido no período\n"
            "- Resumo Aderência: o que já foi recebido e lançado no Sienge mas ainda não foi "
            "lançado aqui\n"
            "- Logs de Login: quem entrou no sistema\n\n"
            "Diga qual desses você precisa que eu explico o passo a passo."
        ),
    },
    {
        "grupo": "Relatórios",
        "pergunta": "Como tiro o relatório de estoque?",
        "caminho": "Relatórios > Estoques",
        "resposta": (
            "Em Relatórios > Estoques, selecione a obra, escolha Quantitativo, informe um "
            "período longo o suficiente e gere o relatório."
        ),
    },
    {
        "grupo": "Relatórios",
        "pergunta": "O que é o relatório de Índices e como uso?",
        "caminho": "Relatórios > Índices",
        "resposta": (
            "Mostra o consumo de um insumo na obra: o gráfico de Consumo Mensal e a tabela "
            "de Consumo por Pavimento.\n\n"
            "1. Selecione a obra. O campo de insumo só libera depois disso.\n"
            "2. Digite o código ou o nome do insumo e clique em Buscar.\n"
            "3. Informe a data inicial e a data final.\n"
            "4. Clique em Gerar. Dá para exportar em Excel.\n\n"
            "Se o botão Gerar estiver desabilitado, é porque ainda falta preencher algum "
            "campo."
        ),
    },
    {
        "grupo": "Relatórios",
        "pergunta": "Para que serve o relatório de QrCode?",
        "caminho": "Relatórios > QrCode",
        "resposta": (
            "Gera o QR Code de um insumo, para identificação no almoxarifado."
        ),
    },
    {
        "grupo": "Relatórios",
        "pergunta": "O que é Comunicação Visual?",
        "caminho": "Relatórios > Comunicação Visual",
        "resposta": (
            "Cria as plaquinhas de identificação usadas para marcar os insumos no "
            "almoxarifado."
        ),
    },
    {
        "grupo": "Relatórios",
        "pergunta": "O que é o Resumo de Aderência?",
        "caminho": "Relatórios > Resumo Aderência",
        "resposta": (
            "Mostra o que já foi recebido e lançado no Sienge mas ainda não foi lançado no "
            "CF Obras. Serve para achar o que está faltando lançar."
        ),
    },
    {
        "grupo": "Relatórios",
        "pergunta": "Como vejo o histórico de requisições?",
        "caminho": "Relatórios > Requisições",
        "resposta": (
            "Use Relatórios > Requisições."
        ),
    },
    {
        "grupo": "Relatórios",
        "pergunta": "Como vejo tudo que entrou de material no período?",
        "caminho": "Relatórios > Entradas de Materiais",
        "resposta": (
            "Use Relatórios > Entradas de Materiais. Para conferir especificamente o que foi "
            "recebido, use Relatórios > Materiais Recebidos."
        ),
    },
    {
        "grupo": "Relatórios",
        "pergunta": "Como faço o inventário de equipamentos?",
        "caminho": "Relatórios > Inventário Equipamentos",
        "resposta": (
            "Use Relatórios > Inventário Equipamentos."
        ),
    },
    {
        "grupo": "Relatórios",
        "pergunta": "Como consulto notas fiscais?",
        "caminho": "Relatórios > Nota Fiscal",
        "resposta": (
            "Use Relatórios > Nota Fiscal."
        ),
    },
    {
        "grupo": "Estatísticas",
        "pergunta": "Como vejo as estatísticas por obra e filial?",
        "caminho": "Estatísticas > Obras/Filiais",
        "resposta": (
            "Em Estatísticas > Obras/Filiais você escolhe a obra e o período. Deixando a obra "
            "em branco, o resultado é de todas as obras da filial. O período tem limite de "
            "90 dias.\n\n"
            "A tela mostra:\n"
            "- Total de requisições cadastradas, separando Concluídas e Pendentes por mês;\n"
            "- Eficiência de Estoque, em percentual;\n"
            "- Movimentos de Estoque, com Total Estoque, Total Entrada e Total Saída em R$.\n\n"
            "No celular, alguns gráficos pedem que você vire a tela para a horizontal."
        ),
    },
    {
        "grupo": "Estatísticas",
        "pergunta": "Como vejo quem está usando o sistema na obra?",
        "caminho": "Estatísticas > Acompanhamento de Uso",
        "resposta": (
            "Use Estatísticas > Acompanhamento de Uso."
        ),
    },
    {
        "grupo": "Geral",
        "pergunta": "Como cadastro uma empresa parceira?",
        "caminho": "Geral > Empresas Parceiras",
        "resposta": (
            "Use Geral > Empresas Parceiras. É um cadastro simples, e ele é necessário antes "
            "de cadastrar um funcionário terceirizado na requisição de equipamentos."
        ),
    },
    {
        "grupo": "Geral",
        "pergunta": "O que é o Analítico Completo?",
        "caminho": "Geral > Analítico Completo",
        "resposta": (
            "É o painel consolidado da base de apropriação, por obra, recurso e WBS. "
            "Cada linha compara sete visões do mesmo item:\n\n"
            "- ORÇADO: quantidade e valor planejados no orçamento original da obra\n"
            "- LEVANTADO: quantidades e valores apurados em campo\n"
            "- CONTRATADO: quantidades e valores totais contratados\n"
            "- CONSUMIDO: o que foi aplicado na obra e lançado no CF Obras\n"
            "- ESTOQUE: o que está em estoque no CF Obras\n"
            "- SALDOS: saldo disponível nos pedidos de compra e contratos do Sienge\n"
            "- A ADITIVAR: quanto ainda falta contratar, considerando o consumo, os saldos e "
            "o que falta executar\n\n"
            "No topo aparecem Total Orçado, Total Contratado, Total Estoque/Pendente, Saldo "
            "Disponível, A Aditivar e o Desvio em percentual.\n"
            "Pelo botão de filtros dá para filtrar por obra, unidade de gasto, categoria, "
            "grupo de recursos, ou mostrar só o que tem orçamento, apropriação, pendência ou "
            "desvio."
        ),
    },
    {
        "grupo": "Fora do alcance",
        "pergunta": "Como troco minha senha?",
        "caminho": None,
        "resposta": (
            "A tela de usuários é do suporte. Peça ao suporte a alteração da sua senha."
        ),
    },
    {
        "grupo": "Fora do alcance",
        "pergunta": "Como cadastro um usuário novo?",
        "caminho": None,
        "resposta": (
            "O cadastro de usuário é feito pelo suporte. Envie nome, e-mail, função e a obra "
            "em que a pessoa vai trabalhar."
        ),
    },
    {
        "grupo": "Fora do alcance",
        "pergunta": "Como vinculo alguém a uma obra?",
        "caminho": None,
        "resposta": (
            "O vínculo de usuário com obra é feito pelo suporte."
        ),
    },
    {
        "grupo": "Fora do alcance",
        "pergunta": "Como cadastro uma obra nova?",
        "caminho": None,
        "resposta": (
            "O cadastro de obra é feito pelo suporte."
        ),
    },
    {
        "grupo": "Fora do alcance",
        "pergunta": "Como cadastro um insumo novo?",
        "caminho": None,
        "resposta": (
            "O cadastro de insumo é feito pelo suporte. Informe o código e a descrição do "
            "insumo e a obra."
        ),
    },
    {
        "grupo": "Fora do alcance",
        "pergunta": "Como peço acesso a outra obra?",
        "caminho": None,
        "resposta": (
            "Peça ao suporte, informando qual obra você precisa acessar."
        ),
    },
    {
        "grupo": "Fora do alcance",
        "pergunta": "Não estou vendo um menu que meu colega vê, por quê?",
        "variacoes": "nao aparece o menu\nfalta menu\nnao tenho acesso\nnao consigo ver a tela\nmeu colega ve e eu nao",
        "caminho": None,
        "resposta": (
            "Os menus mudam conforme o seu perfil e as suas permissões. Se você precisa de "
            "uma tela que não aparece, fale com o suporte dizendo qual é."
        ),
    },
    {
        "grupo": "Fora do alcance",
        "pergunta": "Quem eu procuro quando algo não funciona?",
        "caminho": None,
        "resposta": (
            "Fale com o suporte do CF Obras, descrevendo a tela, o que você tentou fazer e a "
            "mensagem que apareceu."
        ),
    },
]


def executar():
    Base.metadata.create_all(bind=engine, tables=[Artigo.__table__])

    db = session_local()
    criados = 0
    atualizados = 0

    try:
        for dados in ARTIGOS:
            existente = (db.query(Artigo)
                         .filter(Artigo.pergunta == dados["pergunta"])
                         .first())

            if existente is None:
                db.add(Artigo(**dados))
                criados += 1
            else:
                existente.grupo = dados["grupo"]
                existente.caminho = dados["caminho"]
                existente.variacoes = dados.get("variacoes")
                existente.resposta = dados["resposta"]
                existente.destaque = dados.get("destaque", False)
                existente.ordem = dados.get("ordem", 0)
                existente.atualizado_em = datetime.now()
                atualizados += 1

        db.commit()
        total = db.query(Artigo).count()
        print(f"{criados} criado(s), {atualizados} atualizado(s). Total no banco: {total}")

    except Exception as erro:
        db.rollback()
        print("Falhou, nada foi gravado:", erro)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    executar()