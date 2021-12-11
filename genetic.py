import math
import time
import os
import itertools
import random

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
        
        inicio = time.time()
        resultado = calcularHeuristica(coordenadas, att)
        tempoGasto = time.time() - inicio
        print("Resultado encontrado para o arquivo", filename, ":", resultado)
        print("Tempo gasto para o arquivo", filename, ":", tempoGasto*1000.0, "ms")
        print()

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

def gerarIndividuo(matrizDistancias):
    solucaoInicial = random.shuffle([i for i in range(len(matrizDistancias))])
    custoSolucao = calcularCustoSolucao(solucaoInicial, matrizDistancias)
    while True:
        solucaoInicial, custoSolucao, melhora = vizinhos2Opt(custoSolucao, solucao, matrizDistancias)
        if not melhora:
            return (solucaoInicial, custoSolucao)

def populacaoInicial(matrizDistancias, tamanhoPopulacao = 10):
    return [gerarIndividuo(matrizDistancias) for _ in range(tamanhoPopulacao)]

# Seleciona com o método de torneio
def selecionaPais(populacao, k = 3):
    possiveisPais = random.sample(populacao, k)
    pai = ([], math.inf)
    for possivelPai in possiveisPais:
        if possivelPai[1] < pai[1]:
            pai = possivelPai
    
    possiveisMaes = random.sample(populacao, k)
    mae = ([], math.inf)
    for possivelMae in possiveisMaes:
        if possivelMae[1] < pai[1]:
            mae = possivelMae

    return pai, mae

def recombinacao(pai, mae):

    return None

def mutacao(filho):

    return None

def gerarNovaPopulacao(populacao, filho):

    return None

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
    while True:
        pai, mae = selecionaPais(populacao)
        filho = recombinacao(pai, mae)
        filho = mutacao(filho)
        populacao = gerarNovaPopulacao(populacao, filho)
    return custoSolucao