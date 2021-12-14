import math
import time
import os
import itertools
import random
import numpy as np

# Lê os arquivos do diretório indicado, executa a heurística para cada um deles e imprime o resultado
def lerArquivosDiretorio(diretorio, att = False):
    for filename in os.listdir(diretorio):
        coordenadas = []
        cont = 0
        with open(diretorio+filename) as file:
            for line in file:
                line = line.strip()
                if line == 'EOF':
                    break
                if cont < 6:
                    cont+=1
                else:
                    partes = line.split()
                    x = float(partes[1])
                    y = float(partes[2])
                    coordenadas.append((x, y))
        
        totalTempo = 0
        totalSolucao = 0

        for _ in range(1):
            inicio = time.time()
            resultado = calcularHeuristica(coordenadas, att)
            tempoGasto = time.time() - inicio
            totalTempo += tempoGasto
            totalSolucao += resultado
        print("Resultado encontrado para o arquivo", filename, ":", totalSolucao/1)
        print("Tempo gasto para o arquivo", filename, ":", totalTempo*1000.0, "ms")
        print()

# Calcula a distância de acordo com a formula correta do arquivo
def distancia(p1, p2, att):
    if att:
        xd = p1[0]-p2[0]
        yd = p1[1]-p2[1]
        r = math.sqrt((xd*xd + yd*yd)/10.0)
        t = int(round(r))
        if t < r:
            return t+1
        else:
            return t 
    else:
        xd = p1[0]-p2[0]
        yd = p1[1]-p2[1]
        return int(round(math.sqrt(xd*xd + yd*yd)))

# Implementa a função de vizinhança de 2-Opt
def vizinhos2Opt(custoSolucao, solucao, matrizDistancias):
    combinacoes = list(itertools.combinations(range(0, len(matrizDistancias)), 2))
    for i, j in combinacoes:
        v1 = solucao[i]
        v2 = solucao[i+1]
        u1 = solucao[j]
        u2 = solucao[j+1]

        mudanca = matrizDistancias[v1][u1] + matrizDistancias[v2][u2] - matrizDistancias[v1][v2] - matrizDistancias[u1][u2]
        if mudanca < 0:
            # Achou aprimorante
            novaSolucao = solucao[:i+1]
            novaSolucao.extend(reversed(solucao[i+1:j+1]))
            novaSolucao.extend(solucao[j+1:])
            custoSolucao += mudanca
            return novaSolucao, custoSolucao, True
    return solucao, custoSolucao, False

# Calcula o custo de uma solução definida pela lista com a ordem de visitação dos vértices
def calcularCustoSolucao(solucao, matrizDistancias):
    custo = 0
    for i in range(len(solucao)-1):
        custo += matrizDistancias[solucao[i]][solucao[i+1]]
    return custo

def buscaLocal(solucao, custoSolucao, matrizDistancias):
    while True:
        solucao, custoSolucao, melhora = vizinhos2Opt(custoSolucao, solucao, matrizDistancias)
        if not melhora:
            return solucao, custoSolucao

def gerarIndividuo(matrizDistancias):
    visitados = set()
    noInicial = random.randint(0, len(matrizDistancias)-1) # Escolhe o nÃ³ de inicio aleatoriamente
    noAtual = noInicial
    custoSolucao = 0
    solucao = [noInicial]
    visitados.add(noInicial)
    while len(visitados) != len(matrizDistancias):
        proximoNo = -1
        menorDistancia = math.inf
        for i in range(len(matrizDistancias)):
            if i not in visitados:
                if matrizDistancias[noAtual][i] < menorDistancia:
                    menorDistancia = matrizDistancias[noAtual][i]
                    proximoNo = i
        visitados.add(proximoNo)
        solucao.append(proximoNo)
        custoSolucao+=menorDistancia
        noAtual = proximoNo
    custoSolucao += matrizDistancias[noAtual][noInicial]
    solucao.append(noInicial)

    return buscaLocal(solucao, custoSolucao, matrizDistancias)
    

def populacaoInicial(matrizDistancias, tamanhoPopulacao = 15):
    return [gerarIndividuo(matrizDistancias) for _ in range(tamanhoPopulacao)]

# Seleciona com o método de torneio
def selecionaPais(populacao, k = 2):
    tempPop = populacao.copy()
    possiveisPais = random.sample(tempPop, k)
    pai = ([], math.inf)
    for possivelPai in possiveisPais:
        if possivelPai[1] < pai[1]:
            pai = possivelPai
    
    tempPop.remove(pai)
    possiveisMaes = random.sample(tempPop, k)
    mae = ([], math.inf)
    for possivelMae in possiveisMaes:
        if possivelMae[1] < mae[1]:
            mae = possivelMae
    return pai, mae

# Estrategia OX
def recombinacao(pai, mae, matrizDistancias):
    pai = pai[0].copy()
    mae = mae[0].copy()
    # Salva a última cidade do pai
    ultimaCidade = pai[-1]
    # Deleta a última cidade da mãe
    del mae[len(mae)-1]
    k = int(1/3 * len(pai)) 
    filho = []
    # As repetições são n / k arredondada para cima
    while pai:
        tamanho = min(len(pai),k)
        paiTemp = pai[:tamanho]
        filho.extend(paiTemp)
        pai = pai[tamanho:]
        # O(kn) 
        mae = [city for city in mae if city not in paiTemp]
        # Inverte o pai e a mae
        pai, mae = mae, pai
    filho.append(ultimaCidade)
    custoFilho = calcularCustoSolucao(filho, matrizDistancias)
    return buscaLocal(filho, custoFilho, matrizDistancias)

def mutacao(filho, matrizDistancias):
    solucao = filho[0]
    custoSolucao = filho[1]
    i = random.choice(solucao[:-1])
    j = random.choice(solucao[:-1])
    if i == j:
        return filho
    
    if i > j:
        i, j = j, i
    
    v1 = solucao[i]
    v2 = solucao[i+1]
    u1 = solucao[j]
    u2 = solucao[j+1]

    mudanca = matrizDistancias[v1][u1] + matrizDistancias[v2][u2] - matrizDistancias[v1][v2] - matrizDistancias[u1][u2]
    novaSolucao = solucao[:i+1]
    novaSolucao.extend(reversed(solucao[i+1:j+1]))
    novaSolucao.extend(solucao[j+1:])
    custoSolucao += mudanca
    return novaSolucao, custoSolucao

def gerarNovaPopulacao(populacao, pai, mae, filho):
    populacao.remove(pai)
    if mae in populacao:
        populacao.remove(mae)
    if pai[1] < mae[1]:
        populacao.append(filho)
        populacao.append(mae)
    else:
        populacao.append(filho)
        populacao.append(pai)
    return populacao

# Implementação da heurística de Algoritmo Genético
def calcularHeuristica(coordenadas, att):
    # Calcula a matriz de distâncias do grafo
    matrizDistancias = []
    for i in range(len(coordenadas)):
        temp = []
        for j in range(len(coordenadas)):
            if i == j:
                temp.append(0)
            else:
                temp.append(distancia(coordenadas[i], coordenadas[j], att))
        matrizDistancias.append(temp)

    populacao = populacaoInicial(matrizDistancias)
    
    # Executa o algoritmo genetico
    it = 0
    while True:
        pai, mae = selecionaPais(populacao)
        filho = recombinacao(pai, mae, matrizDistancias)
        filho = mutacao(filho, matrizDistancias)
        populacao = gerarNovaPopulacao(populacao, pai, mae, filho)
        it+=1
        if it == 1e4:
            break
    melhorSolucao = (math.inf, [])
    for indiviuo in populacao:
        melhorSolucao = min(melhorSolucao, (indiviuo[1], indiviuo[0]))
    return melhorSolucao[0]

lerArquivosDiretorio("ATT/", True)
lerArquivosDiretorio("EUC_2D/")