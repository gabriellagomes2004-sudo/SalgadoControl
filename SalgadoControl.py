
import csv
import os
from datetime import datetime

from Buscas import busca_sequencial, busca_binaria, ordenar_insercao


# Arquivos utilizados pelo sistema
PASTA_DADOS = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "dados"
)
ARQUIVO_PRODUTOS = os.path.join(PASTA_DADOS, "produtos.csv")
ARQUIVO_PRODUCOES = os.path.join(PASTA_DADOS, "producoes.csv")
ARQUIVO_VENDAS = os.path.join(PASTA_DADOS, "vendas.csv")
ARQUIVO_DESPESAS = os.path.join(PASTA_DADOS, "despesas.csv")
ARQUIVO_HISTORICO = os.path.join(PASTA_DADOS, "historico.csv")

CAMPOS_PRODUTOS = ["codigo", "nome", "preco_venda", "custo_unitario"]
CAMPOS_PRODUCOES = ["codigo", "produto", "quantidade", "data"]
CAMPOS_VENDAS = ["codigo", "produto", "quantidade", "cliente", "data"]
CAMPOS_DESPESAS = ["codigo", "descricao", "tipo", "valor", "data"]
CAMPOS_HISTORICO = ["data", "descricao"]

produtos = []
producoes = []
vendas = []
despesas = []
historico = []


# Leitura e gravação dos dados
def criar_pasta():
    os.makedirs(PASTA_DADOS, exist_ok=True)


def carregar_lista(arquivo, conversoes=None):
    registros = []
    conversoes = conversoes or {}

    try:
        with open(arquivo, newline="", encoding="utf-8") as arq:
            leitor = csv.DictReader(arq)

            for linha in leitor:
                for campo, funcao in conversoes.items():
                    linha[campo] = funcao(linha[campo])

                registros.append(linha)

    except FileNotFoundError:
        pass

    return registros


def salvar_lista(arquivo, campos, registros):
    criar_pasta()

    with open(arquivo, "w", newline="", encoding="utf-8") as arq:
        escritor = csv.DictWriter(arq, fieldnames=campos)
        escritor.writeheader()
        escritor.writerows(registros)


def carregar():
    global produtos, producoes, vendas, despesas, historico

    criar_pasta()

    produtos = carregar_lista(
        ARQUIVO_PRODUTOS,
        {"codigo": int, "preco_venda": float, "custo_unitario": float}
    )

    producoes = carregar_lista(
        ARQUIVO_PRODUCOES,
        {"codigo": int, "produto": int, "quantidade": int}
    )

    vendas = carregar_lista(
        ARQUIVO_VENDAS,
        {"codigo": int, "produto": int, "quantidade": int}
    )

    despesas = carregar_lista(
        ARQUIVO_DESPESAS,
        {"codigo": int, "valor": float}
    )

    historico = carregar_lista(ARQUIVO_HISTORICO)

    if not produtos:
        adicionar_dados_cadastros()
        adicionar_dados_lancamentos()


def salvar():
    salvar_lista(ARQUIVO_PRODUTOS, CAMPOS_PRODUTOS, produtos)
    salvar_lista(ARQUIVO_PRODUCOES, CAMPOS_PRODUCOES, producoes)
    salvar_lista(ARQUIVO_VENDAS, CAMPOS_VENDAS, vendas)
    salvar_lista(ARQUIVO_DESPESAS, CAMPOS_DESPESAS, despesas)
    salvar_lista(ARQUIVO_HISTORICO, CAMPOS_HISTORICO, historico)


def proximo_codigo(lista):
    maior = 0

    for registro in lista:
        if registro["codigo"] > maior:
            maior = registro["codigo"]

    return maior + 1


def registrar_historico(descricao):
    historico.append({
        "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "descricao": descricao
    })

    salvar_lista(ARQUIVO_HISTORICO, CAMPOS_HISTORICO, historico)


# Validação das informações digitadas
def ler_inteiro(mensagem, minimo=0):
    while True:
        try:
            valor = int(input(mensagem))

            if valor < minimo:
                print(f"Digite um inteiro maior ou igual a {minimo}.")
            else:
                return valor

        except ValueError:
            print("Digite um número inteiro válido.")


def ler_valor(mensagem, minimo=0.01):
    while True:
        try:
            valor = float(input(mensagem).replace(",", "."))

            if valor < minimo:
                print(f"Digite um valor maior ou igual a {minimo:.2f}.")
            else:
                return round(valor, 2)

        except ValueError:
            print("Digite um valor válido. Formato: 5,50.")


def ler_texto(mensagem, obrigatorio=True):
    while True:
        texto = " ".join(input(mensagem).strip().split())

        if texto or not obrigatorio:
            return texto

        print("Este campo é obrigatório.")


def ler_opcao(mensagem, opcoes):
    while True:
        opcao = input(mensagem).strip()

        if opcao in opcoes:
            return opcao

        print("Opção inválida.")


def dinheiro(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


# Cadastro e pesquisa de produtos
def produto_por_codigo(codigo):
    posicao, comparacoes = busca_sequencial(produtos, "codigo", codigo)

    if posicao == -1:
        return None

    return produtos[posicao]


def produto_por_nome(nome):
    for produto in produtos:
        if produto["nome"].lower() == nome.lower():
            return produto

    return None


def nome_produto(codigo):
    produto = produto_por_codigo(codigo)

    if produto is None:
        return "Produto inexistente"

    return produto["nome"]


def mostrar_produto(produto):
    print(
        f"{produto['codigo']} | "
        f"{produto['nome']:<25} | "
        f"Venda: {dinheiro(produto['preco_venda'])} | "
        f"Custo: {dinheiro(produto['custo_unitario'])}"
    )


def escolher_produto():
    if not produtos:
        print("Nenhum produto cadastrado.")
        return None

    listar_produtos()
    codigo = ler_inteiro("Código do produto: ", 1)
    produto = produto_por_codigo(codigo)

    if produto is None:
        print("Produto não encontrado.")

    return produto


def cadastrar_produto():
    print("\n--- CADASTRO DE PRODUTO ---")

    nome = ler_texto("Nome do salgado: ")
    preco_venda = ler_valor("Preço de venda por unidade: R$ ")
    custo_unitario = ler_valor("Custo de produção por unidade: R$ ")

    produto = {
        "codigo": proximo_codigo(produtos),
        "nome": nome,
        "preco_venda": preco_venda,
        "custo_unitario": custo_unitario
    }

    produtos.append(produto)
    salvar()
    registrar_historico(f"Produto cadastrado: {nome}")

    print("Produto cadastrado com sucesso.")


def listar_produtos(lista=None):
    if lista is None:
        lista = produtos

    if not lista:
        print("Nenhum produto cadastrado.")
        return

    for produto in lista:
        mostrar_produto(produto)


def pesquisar_produto():
    if not produtos:
        print("Nenhum produto cadastrado.")
        return

    print("\n1 - Pesquisa sequencial")
    print("2 - Pesquisa binária")

    opcao = ler_opcao("Opção: ", ("1", "2"))
    codigo = ler_inteiro("Código procurado: ", 1)

    if opcao == "1":
        lista_busca = produtos
        posicao, comparacoes = busca_sequencial(
            lista_busca, "codigo", codigo
        )
    else:
        lista_busca = ordenar_insercao(produtos, "codigo")
        posicao, comparacoes = busca_binaria(
            lista_busca, "codigo", codigo
        )

    if posicao == -1:
        print(f"Produto não encontrado. Comparações: {comparacoes}.")
    else:
        mostrar_produto(lista_busca[posicao])
        print(f"Comparações realizadas: {comparacoes}.")


# Produção e controle de estoque
def registrar_producao():
    print("\n--- REGISTRO DE PRODUÇÃO ---")

    produto = escolher_produto()

    if produto is None:
        return

    quantidade = ler_inteiro("Quantidade produzida: ", 1)
    data = ler_texto("Data da produção: ")

    producao = {
        "codigo": proximo_codigo(producoes),
        "produto": produto["codigo"],
        "quantidade": quantidade,
        "data": data
    }

    producoes.append(producao)
    salvar()

    registrar_historico(
        f"Produção registrada: {quantidade} unidade(s) de {produto['nome']}"
    )

    print("Produção registrada com sucesso.")


def quantidade_produzida(codigo_produto):
    total = 0

    for producao in producoes:
        if producao["produto"] == codigo_produto:
            total += producao["quantidade"]

    return total


def quantidade_vendida(codigo_produto):
    total = 0

    for venda in vendas:
        if venda["produto"] == codigo_produto:
            total += venda["quantidade"]

    return total


def estoque(codigo_produto):
    return (
        quantidade_produzida(codigo_produto)
        - quantidade_vendida(codigo_produto)
    )


def listar_estoque():
    if not produtos:
        print("Nenhum produto cadastrado.")
        return

    print("\n--- ESTOQUE ATUAL ---")

    for produto in produtos:
        quantidade = estoque(produto["codigo"])
        print(f"{produto['nome']}: {quantidade} unidade(s)")


# Registro de vendas
def registrar_venda():
    print("\n--- REGISTRO DE VENDA ---")

    produto = escolher_produto()

    if produto is None:
        return

    disponivel = estoque(produto["codigo"])
    print(f"Estoque disponível: {disponivel} unidade(s).")

    quantidade = ler_inteiro("Quantidade vendida: ", 1)

    if quantidade > disponivel:
        print("Venda não registrada: estoque insuficiente.")
        return

    cliente = ler_texto("Cliente (opcional): ", False)

    if not cliente:
        cliente = "Não informado"

    data = ler_texto("Data da venda: ")

    venda = {
        "codigo": proximo_codigo(vendas),
        "produto": produto["codigo"],
        "quantidade": quantidade,
        "cliente": cliente,
        "data": data
    }

    vendas.append(venda)
    salvar()

    registrar_historico(
        f"Venda registrada: {quantidade} unidade(s) de {produto['nome']}"
    )

    print("Venda registrada com sucesso.")


# Registro de despesas
def registrar_despesa():
    print("\n--- REGISTRO DE DESPESA ---")

    descricao = ler_texto("Descrição da despesa: ")
    valor = ler_valor("Valor da despesa: R$ ")
    data = ler_texto("Data da despesa: ")

    print("\nTipos de despesa:")
    print("1 - Fixa")
    print("2 - Variável")
    print("3 - Operacional")

    opcao = ler_opcao("Tipo: ", ("1", "2", "3"))

    tipos = {
        "1": "fixa",
        "2": "variavel",
        "3": "operacional"
    }

    despesa = {
        "codigo": proximo_codigo(despesas),
        "descricao": descricao,
        "tipo": tipos[opcao],
        "valor": valor,
        "data": data
    }

    despesas.append(despesa)
    salvar()
    registrar_historico(f"Despesa registrada: {descricao}")

    print("Despesa registrada com sucesso.")


# Dados de exemplo para testar o sistema
def adicionar_dados_cadastros():
    dados_produtos = [
        {"nome": "Coxinha de frango", "preco_venda": 5.00, "custo_unitario": 2.00},
        {"nome": "Risole de presunto e queijo", "preco_venda": 5.50, "custo_unitario": 2.20},
        {"nome": "Bolinha de queijo", "preco_venda": 4.50, "custo_unitario": 1.80}
    ]

    adicionados = 0

    for dado in dados_produtos:
        if produto_por_nome(dado["nome"]) is None:
            produtos.append({
                "codigo": proximo_codigo(produtos),
                "nome": dado["nome"],
                "preco_venda": dado["preco_venda"],
                "custo_unitario": dado["custo_unitario"]
            })
            adicionados += 1

    salvar()

    if adicionados:
        registrar_historico(
            f"Dados de cadastros adicionados: {adicionados} produto(s)"
        )
        print(f"{adicionados} produto(s) adicionado(s).")


def adicionar_dados_lancamentos():
    if not produtos:
        print("Cadastre os produtos antes dos lançamentos.")
        return

    data = datetime.now().strftime("%d/%m/%Y")
    adicionados = 0

    dados_producao = [
        ("Coxinha de frango", 100),
        ("Risole de presunto e queijo", 80),
        ("Bolinha de queijo", 60)
    ]

    for nome, quantidade in dados_producao:
        produto = produto_por_nome(nome)

        if produto is not None:
            ja_existe = False

            for producao in producoes:
                if (
                    producao["produto"] == produto["codigo"]
                    and producao["data"] == data
                    and producao["quantidade"] == quantidade
                ):
                    ja_existe = True

            if not ja_existe:
                producoes.append({
                    "codigo": proximo_codigo(producoes),
                    "produto": produto["codigo"],
                    "quantidade": quantidade,
                    "data": data
                })
                adicionados += 1

    dados_vendas = [
        ("Coxinha de frango", 30, "Cliente 1"),
        ("Risole de presunto e queijo", 20, "Cliente 2"),
        ("Bolinha de queijo", 15, "Cliente 3")
    ]

    for nome, quantidade, cliente in dados_vendas:
        produto = produto_por_nome(nome)

        if produto is not None:
            ja_existe = False

            for venda in vendas:
                if (
                    venda["produto"] == produto["codigo"]
                    and venda["quantidade"] == quantidade
                    and venda["cliente"] == cliente
                ):
                    ja_existe = True

            if not ja_existe:
                vendas.append({
                    "codigo": proximo_codigo(vendas),
                    "produto": produto["codigo"],
                    "quantidade": quantidade,
                    "cliente": cliente,
                    "data": data
                })
                adicionados += 1

    dados_despesas = [
        ("Compra de gás", "operacional", 80.00),
        ("Embalagens", "variavel", 45.00)
    ]

    for descricao, tipo, valor in dados_despesas:
        ja_existe = False

        for despesa in despesas:
            if despesa["descricao"] == descricao:
                ja_existe = True

        if not ja_existe:
            despesas.append({
                "codigo": proximo_codigo(despesas),
                "descricao": descricao,
                "tipo": tipo,
                "valor": valor,
                "data": data
            })
            adicionados += 1

    salvar()

    if adicionados:
        registrar_historico(
            f"Dados de lançamentos adicionados: {adicionados} registro(s)"
        )
        print(f"{adicionados} lançamento(s) adicionado(s).")


# Relatórios financeiros
def calcular_relatorio():
    faturamento = 0.0
    custo_produtos_vendidos = 0.0
    total_despesas = 0.0
    unidades_produzidas = 0
    unidades_vendidas = 0

    for venda in vendas:
        produto = produto_por_codigo(venda["produto"])

        if produto is not None:
            quantidade = venda["quantidade"]
            faturamento += quantidade * produto["preco_venda"]
            custo_produtos_vendidos += quantidade * produto["custo_unitario"]
            unidades_vendidas += quantidade

    for producao in producoes:
        unidades_produzidas += producao["quantidade"]

    for despesa in despesas:
        total_despesas += despesa["valor"]

    lucro_bruto = faturamento - custo_produtos_vendidos
    lucro_liquido = lucro_bruto - total_despesas

    estoque_total = 0

    for produto in produtos:
        estoque_total += estoque(produto["codigo"])

    return {
        "faturamento": round(faturamento, 2),
        "custo_produtos_vendidos": round(custo_produtos_vendidos, 2),
        "despesas": round(total_despesas, 2),
        "lucro_bruto": round(lucro_bruto, 2),
        "lucro_liquido": round(lucro_liquido, 2),
        "unidades_produzidas": unidades_produzidas,
        "unidades_vendidas": unidades_vendidas,
        "estoque_total": estoque_total
    }


def relatorio():
    if not produtos:
        print("Cadastre pelo menos um produto para gerar o relatório.")
        return

    resultado = calcular_relatorio()

    if vendas:
        media_venda = resultado["faturamento"] / len(vendas)
    else:
        media_venda = 0

    print("\n================ RELATÓRIO FINANCEIRO ================")
    print(f"Unidades produzidas:          {resultado['unidades_produzidas']}")
    print(f"Unidades vendidas:            {resultado['unidades_vendidas']}")
    print(f"Unidades em estoque:          {resultado['estoque_total']}")
    print(f"Faturamento:                  {dinheiro(resultado['faturamento'])}")
    print(f"Custo dos produtos vendidos:  {dinheiro(resultado['custo_produtos_vendidos'])}")
    print(f"Despesas:                     {dinheiro(resultado['despesas'])}")
    print(f"Lucro bruto:                  {dinheiro(resultado['lucro_bruto'])}")
    print(f"LUCRO LÍQUIDO:                {dinheiro(resultado['lucro_liquido'])}")
    print(f"Média por venda:              {dinheiro(media_venda)}")
    print("========================================================")

    print("\nFórmula utilizada:")
    print("Lucro líquido = faturamento - custo dos produtos vendidos - despesas")
    print("\nO custo das unidades ainda em estoque não reduz o lucro atual.")


def relatorio_por_produto():
    if not produtos:
        print("Nenhum produto cadastrado.")
        return

    print(
        "\nProduto                 "
        "Produz. Vend. Estoque Receita       Custo        Lucro"
    )
    print("-" * 88)

    for produto in produtos:
        produzida = quantidade_produzida(produto["codigo"])
        vendida = quantidade_vendida(produto["codigo"])

        receita = vendida * produto["preco_venda"]
        custo_vendido = vendida * produto["custo_unitario"]
        lucro = receita - custo_vendido

        print(
            f"{produto['nome'][:22]:22} "
            f"{produzida:7} "
            f"{vendida:5} "
            f"{produzida - vendida:7} "
            f"{dinheiro(receita):>12} "
            f"{dinheiro(custo_vendido):>12} "
            f"{dinheiro(lucro):>12}"
        )


def listar_historico():
    if not historico:
        print("Histórico vazio.")
        return

    print("\n--- HISTÓRICO ---")

    for item in historico[::-1]:
        print(f"[{item['data']}] {item['descricao']}")


# Menus do programa
def menu_cadastros():
    while True:
        print("\n========== CADASTROS ==========")
        print("1 - Cadastrar produto")
        print("2 - Listar produtos")
        print("3 - Pesquisar produto")
        print("0 - Voltar")

        opcao = ler_opcao("Opção: ", ("1", "2", "3", "0"))

        if opcao == "1":
            cadastrar_produto()
        elif opcao == "2":
            listar_produtos()
        elif opcao == "3":
            pesquisar_produto()
        else:
            return


def menu_lancamentos():
    while True:
        print("\n========== LANÇAMENTOS ==========")
        print("1 - Registrar produção")
        print("2 - Registrar venda")
        print("3 - Registrar despesa")
        print("4 - Ver estoque")
        print("0 - Voltar")

        opcao = ler_opcao("Opção: ", ("1", "2", "3", "4", "0"))

        if opcao == "1":
            registrar_producao()
        elif opcao == "2":
            registrar_venda()
        elif opcao == "3":
            registrar_despesa()
        elif opcao == "4":
            listar_estoque()
        else:
            return


def menu_relatorios():
    while True:
        print("\n========== RELATÓRIOS ==========")
        print("1 - Relatório financeiro geral")
        print("2 - Relatório por produto")
        print("3 - Histórico")
        print("0 - Voltar")

        opcao = ler_opcao("Opção: ", ("1", "2", "3", "0"))

        if opcao == "1":
            relatorio()
        elif opcao == "2":
            relatorio_por_produto()
        elif opcao == "3":
            listar_historico()
        else:
            return


def menu():
    carregar()

    while True:
        print("\n========== SALGADOCONTROL ==========")
        print("1 - Cadastros")
        print("2 - Lançamentos")
        print("3 - Relatórios")
        print("4 - Salvar dados")
        print("0 - Sair")

        opcao = ler_opcao("Opção: ", ("1", "2", "3", "4", "0"))

        if opcao == "1":
            menu_cadastros()
        elif opcao == "2":
            menu_lancamentos()
        elif opcao == "3":
            menu_relatorios()
        elif opcao == "4":
            salvar()
            print("Dados salvos com sucesso.")
        else:
            salvar()
            print("Dados salvos. Até logo!")
            break


if __name__ == "__main__":
    menu()
