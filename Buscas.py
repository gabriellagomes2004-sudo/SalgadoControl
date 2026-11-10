def busca_sequencial(registros, chave, valor):
    comparacoes = 0

    for i in range(len(registros)):
        comparacoes += 1

        if registros[i][chave] == valor:
            return i, comparacoes

    return -1, comparacoes


def busca_binaria(registros, chave, valor):
    inicio = 0
    fim = len(registros) - 1
    comparacoes = 0

    while inicio <= fim:
        meio = (inicio + fim) // 2
        comparacoes += 1

        if registros[meio][chave] == valor:
            return meio, comparacoes

        if registros[meio][chave] < valor:
            inicio = meio + 1
        else:
            fim = meio - 1

    return -1, comparacoes


def ordenar_insercao(registros, chave):
    """
    Ordenação manual por inserção.
    Não utiliza sorted() nem sort().
    """

    lista = registros[:]

    for i in range(1, len(lista)):
        atual = lista[i]
        j = i - 1

        while j >= 0 and lista[j][chave] > atual[chave]:
            lista[j + 1] = lista[j]
            j -= 1

        lista[j + 1] = atual

    return lista
