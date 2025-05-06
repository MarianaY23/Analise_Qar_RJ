# -*- coding: utf-8 -*-
"""
Created on Sat May  3 2025

Executa o processo completo de análise da qualidade do ar, incluindo:
- Análise univariada
- Geração de gráficos e decomposição de séries temporais

Lembre-se de criar as pastas corretamente.

@author: Debor
"""


    #%%
import sys
import seaborn as sns
import os
import pandas as pd
import matplotlib.pyplot as plt
from pmdarima import auto_arima 


repoPath = r"C:\PYTHON\ENS5132\ENS5132\Trabalho_1"
scriptsPath = os.path.join(repoPath, 'scripts')

print(f"Caminho dos scripts: {scriptsPath}")
sys.path.append(scriptsPath)

# Importação das funções
from airQualityFigures import airQualityHist, airQualityTimeSeries, airQualityBoxplot
from univariateStatistics import univariateStatistics, timeSeriesDecompose
from airQualityAnalysis import airQualityAnalysis


dataPath = os.path.join(repoPath, 'outputs', 'cidades_RJ')
print(f"Caminho dos dados: {dataPath}")


if not os.path.exists(dataPath):
    print(f"Diretório {dataPath} não encontrado.")
else:
    arquivos_csv = [f for f in os.listdir(dataPath) if f.endswith('.csv')]

    figurasPath = os.path.join(repoPath, 'figuras')
    os.makedirs(figurasPath, exist_ok=True)

    for arquivo in arquivos_csv:
        cidade = arquivo.split('.')[0].strip()
        print(f"\n Iniciando análise para: {cidade}")
    
        cidade_path = os.path.join(dataPath, arquivo)
        
        try:
            aqData = pd.read_csv(cidade_path)
            if aqData is None or aqData.empty:
                print(f"Erro ao ler o arquivo {arquivo}. O DataFrame está vazio.")
                continue
            
            aqData['DateTime'] = pd.to_datetime(aqData['DateTime'])

            #  Gera os boxplots por poluente e salva nas pastas por cidade
            airQualityBoxplot(aqData, cidade, repoPath)

            poluentes = [col for col in aqData.columns if col != 'DateTime']

            # 🔧 Criar um único DataFrame com todos os poluentes empilhados
            dados_formatados = pd.DataFrame()

            for poluente in poluentes:
                df_temp = aqData[['DateTime', poluente]].copy()
                df_temp['Poluente'] = poluente
                df_temp['Valor'] = df_temp[poluente]
                dados_formatados = pd.concat([dados_formatados, df_temp[['DateTime', 'Poluente', 'Valor']]], ignore_index=True)
                #timeSeriesDecompose(aqData, poluente, repoPath, cidade)
                
            #  Chamada única com todos os poluentes empilhados
            airQualityTimeSeries(dados_formatados, [cidade], repoPath)

            # Realizando a previsão ARIMA para cada poluente
            for poluente in poluentes:
                print(f" Realizando previsão de série temporal para {poluente} em {cidade}")


            # Outras análises podem continuar sendo feitas com aqData
            univariateStatistics(aqData,[cidade],repoPath)
            airQualityHist(dados_formatados, [cidade], repoPath)

        except Exception as e:
            print(f"Erro ao processar o arquivo {arquivo}: {e}")
            continue

        print(f" Análise finalizada para: {cidade}")

    print("\n Processo completo concluído!")

