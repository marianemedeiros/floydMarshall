import math

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

def trocaCabos(adjacencia, vertices, origem, destino):
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
    valorPorMetro = {1 : 1.00, 3 : 1.50, 10 : 2.00, 20 : 2.50}
    return valorPorMetro[banda] * distancia


def nomeVertice(id_v, vertices):
    for key, value in vertices.iteritems():
        if(value == id_v):
            return key

#test = math.inf
vertices, adjacencia = carregaGrafo("rede_ipe.txt")

matrizD, matrizS = criaMatriz(vertices, adjacencia)
matrizD, matrizS = floydwarshall(matrizD, matrizS);
menorO, posMenorO = calculaMenorCustoTotal(matrizD)


maiorCustoBeneficio = 0

for i in range(len(vertices)):
    for aresta in adjacencia[i]:
        menor, posM, dif = trocaCabos(adjacencia, vertices, i, vertices[aresta["vertice"]])
        if(dif != 0):
            custoBeneficio = (menorO - menor)/dif
            #print "menor: ", menor, "posMenor: ", posM, "custo beneficio (ms/Reais) ", custoBeneficio
            if (custoBeneficio > maiorCustoBeneficio):
                maiorCustoBeneficio = custoBeneficio
                x = menor
                y = posM
                origem = i
                destino = vertices[aresta["vertice"]]

print "Menor atraso total: ", x , "Posicao: ", y, "Origem: ", nomeVertice(origem, vertices), "Destino: ", nomeVertice(destino, vertices), "CustoBeneficio: ", maiorCustoBeneficio

#for aresta in adjacencia[vertices['Salvador']]:
#    print("Atraso total de Salvador a "+aresta["vertice"]+":")
#    print(atrasoTransmissao(aresta["banda"]) + atrasoPropragacao(aresta["distancia"]))
