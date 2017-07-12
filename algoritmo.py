import math
from copy import deepcopy

INF = 999999

def atrasoTransmissao(banda):
    kComprimentoPacote = 100000000.0 #0.1Gb
    atraso = kComprimentoPacote / (banda * 1000000000)
    return atraso

def atrasoPropragacao(distancia):
    kVelocidadePropagacao = 299792458.00 #Velocidade da Luz
    atraso = distancia / kVelocidadePropagacao;
    return atraso

def linhaParaVetor(linha):
    retorno = linha.strip('/n').split()
    if len(retorno) > 0:
        return retorno
    else:
        return [""]

def criaVertices(nomes):
    vertices = {}
    id_vertice = 0
    for nome in nomes:
        vertices[nome] = id_vertice
        id_vertice += 1
    return vertices

def criaAdjacencia(vertices, adjacencia, nova):
    adjacencia[vertices[nova[0]]].append({
        "vertice":   nova[1],
        "banda":     int(nova[2]),
        "distancia": int(nova[3])
    })
    return adjacencia

def carregaGrafo(nome_arquivo):
    arquivo = open(nome_arquivo, "r")
    linhas = arquivo.readlines()
    vertices = {}
    adjacencia = []

    vertices = criaVertices(linhaParaVetor(linhas[0]))
    for _ in range(len(vertices)):
        adjacencia.append([]);

    i = 1
    while i < len(linhas):
        linha = linhaParaVetor(linhas[i])
        if len(linha) > 1:
            criaAdjacencia(vertices, adjacencia, linha)
        i += 1

    return vertices, adjacencia

def criaMatriz(vertices, adjacencia):
    matrizD = []
    matrizS = []

    for v in range(len(vertices)):
        matrizD.append([])
        matrizS.append([])
        for x in range(len(vertices)):
            matrizD[v].append(INF)
            matrizS[v].append(x)

    i = 0;
    for v in vertices:
        for j in adjacencia[i]:
            matrizD[i][vertices[j["vertice"]]] = atrasoTransmissao(j["banda"]) + atrasoPropragacao(j["distancia"])
        i = i + 1
    return matrizD, matrizS

def floydwarshall(matrizD, matrizS):

    # Initialize dist and pred:
    # copy graph into dist, but add infinite where there is
    # no edge, and 0 in the diagonal
    for iteracao in range(len(matrizD)):
        for linha in range(len(matrizD)):
            for coluna in range(len(matrizD)):
                novoValor = matrizD[linha][iteracao] +  matrizD[iteracao][coluna]
                if(novoValor < matrizD[linha][coluna]):
                    matrizD[linha][coluna] = novoValor
                    matrizS[linha][coluna] = iteracao

    return matrizD, matrizS

def calculaMenorCustoTotal(matrizD):
    menor  = INF;
    posMenor = -1
    for i in range(len(matrizD)):
        soma = 0;
        for j in range(len(matrizD)):
            if(i != j):
                soma = soma + matrizD[i][j]
        #print i , " - " , soma
        if soma < menor:
            menor = soma
            posMenor = i
    return menor, posMenor

def aumentaFibra(valor):
    if(valor == 1):
        return 3
    if(valor == 3):
        return 10
    return 20

def trocaCabos(adjacenciaOriginal, vertices, origem, destino):
    adjacencia = deepcopy(adjacenciaOriginal)
    

    for aresta in adjacencia[origem]:
        if(vertices[aresta["vertice"]] == destino):
            precoO = calculoPreco(aresta["distancia"], aresta["banda"])
            aresta["banda"] = aumentaFibra(aresta["banda"])
            precoN = calculoPreco(aresta["distancia"], aresta["banda"])

    for aresta in adjacencia[destino]:
        if(vertices[aresta["vertice"]] == origem):
            aresta["banda"] = aumentaFibra(aresta["banda"])

    matrizD, matrizS = criaMatriz(vertices, adjacencia)
    matrizD, matrizS = floydwarshall(matrizD, matrizS)
    menor, posMenor = calculaMenorCustoTotal(matrizD)
    return menor, posMenor, (precoN - precoO)

def calculoPreco(distancia, banda):
    valorPorMetro = 6.00
    valorPorBanda = {1 : 15000, 3 : 35000, 10 : 60000, 20 : 90000}
    return valorPorBanda[banda] + (valorPorMetro * distancia)


def nomeVertice(id_v, vertices):
    for key, value in vertices.iteritems():
        if(value == id_v):
            return key

def nomeAresta(banda, id_o, id_d, vertices):
    valorBanda = str(banda)
    retorno = "(" + "{:>2}".format(valorBanda) + "Gb/s) - " + nomeVertice(id_o, vertices) + " -> " + nomeVertice(id_d, vertices)
    return "{:<42}".format(retorno)

vertices, adjacencia = carregaGrafo("rede_ipe.txt")

matrizD, matrizS = criaMatriz(vertices, adjacencia)
matrizD, matrizS = floydwarshall(matrizD, matrizS);
menorO, posMenorO = calculaMenorCustoTotal(matrizD)

custoTotalOriginal = 0
for i in range(len(vertices)):
    for aresta in adjacencia[i]:
	custoTotalOriginal += calculoPreco(aresta["distancia"], aresta["banda"])
custoTotalOriginal /= 2

print "================================================================================================================================"
print "Grafo Original:"
print "Menor tempo de broadcast (s)\tVertice de origem do broadcast\tCusto total (R$)"
print menorO, "\t\t\t", nomeVertice(posMenorO, vertices), "\t", custoTotalOriginal
print "================================================================================================================================"
print "Upgrade de arestas:"
print "(Nova banda) - Aresta atualizada\t\tMelhor broadcast (s)\tCusto upgrade\tCusto-beneficio (ms/R$)"
print "================================================================================================================================"

maiorCustoBeneficio = 0
menorTempoDeBroadcast = INF

for i in range(len(vertices)):
    for aresta in adjacencia[i]:
	if (aresta["banda"] < 20):
            menorTempo, posM, dif = trocaCabos(adjacencia, vertices, i, vertices[aresta["vertice"]])
            if(dif != 0):
                custoBeneficio = (menorO - menorTempo)/dif * 1000 #ms/R$, nao s/R$
		print nomeAresta(aresta["banda"], i, vertices[aresta["vertice"]], vertices), "\t", menorTempo, "\t\tR$%.2f" % (dif), "\t", custoBeneficio
                if (custoBeneficio > maiorCustoBeneficio):
                    maiorCustoBeneficio = custoBeneficio
                    maiorCustoBeneficio_Tempo = menorTempo
                    maiorCustoBeneficio_nome = nomeAresta(aresta["banda"], i, vertices[aresta["vertice"]], vertices)
                    maiorCustoBeneficio_custo = dif
                if (menorTempo < menorTempoDeBroadcast):
                    menorTempoDeBroadcast_CustoBeneficio = custoBeneficio
                    menorTempoDeBroadcast = menorTempo
                    menorTempoDeBroadcast_nome = nomeAresta(aresta["banda"], i, vertices[aresta["vertice"]], vertices)
                    menorTempoDeBroadcast_custo = dif

print "================================================================================================================================"
print
print "================================================================================================================================"
print "Resultados:"
print "================================================================================================================================"
print "Aresta com maior Custo-beneficio (ms/R$):"
print "(Nova banda) - Aresta atualizada\t\tMelhor broadcast (s)\tCusto upgrade\tCusto-beneficio (ms/R$)"
print maiorCustoBeneficio_nome, "\t", maiorCustoBeneficio_Tempo, "\t\tR$%.2f" % (maiorCustoBeneficio_custo), "\t", maiorCustoBeneficio
print "================================================================================================================================"
print "Aresta com menor tempo de broadcast (s):"
print "(Nova banda) - Aresta atualizada\t\tMelhor broadcast (s)\tCusto upgrade\tCusto-beneficio (ms/R$)"
print menorTempoDeBroadcast_nome, "\t", menorTempoDeBroadcast, "\t\tR$%.2f" % (menorTempoDeBroadcast_custo), "\t", menorTempoDeBroadcast_CustoBeneficio
print "================================================================================================================================"

#print "Menor atraso total: ", x , "Posicao: ", y, "Origem: ", nomeVertice(origem, vertices), "Destino: ", nomeVertice(destino, vertices), "CustoBeneficio: ", maiorCustoBeneficio
