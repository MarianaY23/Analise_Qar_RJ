# -*- coding: utf-8 -*-
"""
Created on Fri May  2 14:16:58 2025

@author: marit
"""

#%% Importando pacotes
import pandas as pd 
import numpy as np 
import os

#%% Função para Análise de Qualidade do Ar

def airQualityAnalysis(cidade, repoPath):
    repoPath = r"C:\PYTHON\ENS5132\ENS5132\Trabalho_1"
    cidades = 'cidades_RJ'  # Aparentemente, você vai passar a cidade de interesse.

    # Caminho para a pasta de dados por estado
    dataDir = os.path.join(repoPath, 'outputs', cidades)

    if not os.path.exists(dataDir):
        print(f"Pasta não encontrada: {dataDir}")
        return None, None

    # Lê todos os arquivos CSV da pasta
    allFiles = []
    for fileInList in os.listdir(dataDir):
        if fileInList.endswith('.csv'):
            file_path = os.path.join(dataDir, fileInList)
            print(f"Lendo: {file_path}")
            dfConc = pd.read_csv(file_path, encoding='latin1')
            allFiles.append(dfConc)

    if len(allFiles) == 0:
        print(f"Nenhum arquivo CSV encontrado em {dataDir}")
        return None, None

    aqData = pd.concat(allFiles, ignore_index=True)

    # Verificar se a coluna 'DateTime' existe
    if 'DateTime' not in aqData.columns:
        print("Erro: A coluna 'DateTime' não foi encontrada.")
        return None, None

    # Garantir que 'DateTime' seja a coluna de data e hora
    aqData['DateTime'] = pd.to_datetime(aqData['DateTime'], errors='coerce')
    if aqData['DateTime'].isnull().any():
        print("Erro: Algumas datas não puderam ser convertidas.")
        return None, None
#datetime
    aqData['year'] = aqData['DateTime'].dt.year
    aqData['month'] = aqData['DateTime'].dt.month
    aqData['day'] = aqData['DateTime'].dt.day
    aqData['hour'] = aqData['DateTime'].dt.hour
    

    aqData['Season'] = np.nan
    aqData.loc[aqData['month'].isin([12, 1, 2]), 'Season'] = 'Verão'
    aqData.loc[aqData['month'].isin([3, 4, 5]), 'Season'] = 'Outono'
    aqData.loc[aqData['month'].isin([6, 7, 8]), 'Season'] = 'Inverno'
    aqData.loc[aqData['month'].isin([9, 10, 11]), 'Season'] = 'Primavera'

    # Identificar os poluentes a partir das colunas restantes 
    pollutants = [col for col in aqData.columns if col not in ['DateTime', 'Season', 'year', 'month', 'day', 'hour']]

    print(aqData.head())  
    
    # Caminho para salvar os resultados
    outputPath = os.path.join(repoPath, 'outputs')
    os.makedirs(outputPath, exist_ok=True)

    # Estatísticas por poluente
    statAll = []
    for pol in pollutants:
        basicStat = aqData[pol].describe()  
        statAll.append(pd.DataFrame(basicStat, columns=[pol]))
    dfmerge = pd.concat(statAll, axis=1)
    dfmerge.to_csv(os.path.join(outputPath, f'basicStat_{cidade}.csv'))

    # Estatísticas gerais por poluente
    statGroup = aqData[pollutants].describe()  
    statGroup.to_csv(os.path.join(outputPath, 'basicStat_ALL.csv'))

    # Tabela com poluentes como colunas (datetime como índice)
    aqTable = aqData[pollutants].copy()  
    aqTable['Season'] = aqData['Season'].values 
    aqTable.to_csv(os.path.join(outputPath, 'aqTable_with_season.csv'))

    print("Todos os arquivos CSV foram gerados com sucesso.")
    return aqData, aqTable
