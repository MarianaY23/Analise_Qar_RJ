# -*- coding: utf-8 -*-
"""
Created on Fri Apr 25 17:43:58 2025

@author: marit

NESTE CÓDIGO SERÁ FEITA A ORGANIZAÇÃO DOS DADOS PARA A ANÁLISE
"""
#%% Importando pacotes
import pandas as pd 
import os

#%% Organizando os dados 
# escolhendo e estado que vamos trabalhar 
uf = 'RJ'

#caminho para as pastas de dados 
dataDir = r"C:\PYTHON\ENS5132\ENS5132\Trabalho_1\inputs" + '/' + uf

# Caminho para salvar os arquivos separados por estação
outputDir = r"C:\PYTHON\ENS5132\ENS5132\Trabalho_1\outputs\csv_estacao_RJ"
os.makedirs(outputDir, exist_ok=True)  # Cria a pasta se não existir

dataList = os.listdir(dataDir)
os.chdir(dataDir)

allFiles = []
for arquivo in dataList:
    print (f"Lendo:{arquivo}")
    dfConc =pd.read_csv(arquivo, encoding = 'Latin1')
    allFiles.append(dfConc)

allFiles = pd.concat(allFiles,ignore_index=True)
stations = pd.unique(allFiles['Estacao'])
 
#salvando um CSV separado para cada estacao 
for est in stations:
    df_est = allFiles[allFiles['Estacao'] == est]

    nome_arquivo = est.replace('/','_').replace('\\','_').replace(':','_').replace('*','_')
    caminho_completo = os.path.join(outputDir, f'{nome_arquivo}.csv')
    df_est.to_csv(caminho_completo, index=False, encoding='utf-8')
    print(f"Arquivo salvo: {caminho_completo}")

#%% Tratando os dados juntando os bairros em apenas um csv por cidade (média dos valores de cada poluente do DateTime)
#série temporal 

import os
import pandas as pd
#formatando a hora para ser gerada corretamente no csv 
def formatar_hora(hora):
    try:
        partes = str(hora).strip().split(":")
        if len(partes) == 2:
            h = int(partes[0])
            m = int(partes[1])
            return f"{h:02d}:{m:02d}"  
    except:
        pass
    return ""  # se inválido, deixamos vazio por enquanto

def agrupar_poluente(df):

    df['Hora'] = df['Hora'].astype(str).apply(formatar_hora)
    df['datetime'] = pd.to_datetime(df['Data'] + ' ' + df['Hora'], errors='coerce')
    df = df.dropna(subset=['datetime'])
    df_agrupado = df.groupby(['datetime', 'Poluente'])['Valor'].mean().reset_index()
    df_agrupado.rename(columns={'datetime': 'DateTime', 'Valor': 'Concentracao_Media'}, inplace=True)
    df_pivotado = df_agrupado.pivot(index='DateTime', columns='Poluente', values='Concentracao_Media').reset_index()
    df_pivotado['only_date'] = df_pivotado['DateTime'].dt.date

    # Cria uma máscara booleana para identificar datas com apenas hora 00:00
    dates_with_only_midnight = df_pivotado.groupby('only_date')['DateTime'].apply(
        lambda x: all(t.hour == 0 and t.minute == 0 for t in x)
    )

    def format_datetime_condicional(row):
        date = row['only_date']
        if dates_with_only_midnight.get(date, False):
            return date.strftime('%Y-%m-%d 00:00')
        else:
            return row['DateTime'].strftime('%Y-%m-%d %H:%M')

    df_pivotado['DateTime'] = df_pivotado.apply(format_datetime_condicional, axis=1)
    df_pivotado.drop(columns=['only_date'], inplace=True)
    return df_pivotado

caminho_arquivos = r"C:\PYTHON\ENS5132\ENS5132\Trabalho_1\outputs\csv_estacao_RJ"
dados_por_cidade = r"C:\PYTHON\ENS5132\ENS5132\Trabalho_1\outputs\cidades_RJ"
os.makedirs(dados_por_cidade, exist_ok=True)
arquivos = os.listdir(caminho_arquivos)

cidades = set()
for arquivo in arquivos:
    if "-" in arquivo and arquivo.endswith(".csv"):
        cidade = arquivo.split("-")[0]
        cidades.add(cidade)

print("Cidades encontradas:", cidades)


for cidade in cidades:
    dfs = []

    for arquivo in arquivos:
        if arquivo.startswith(cidade + "-") and arquivo.endswith(".csv"):
            caminho = os.path.join(caminho_arquivos, arquivo)
            print(f"Lendo arquivo: {caminho}")
            df= pd.read_csv(caminho)
            dfs.append(df)

    if dfs:
        df_total = pd.concat(dfs, ignore_index=True)

        # Verificar se as colunas necessárias existem
        colunas_necessarias = {'Poluente', 'Data', 'Hora'}
        if not colunas_necessarias.issubset(df_total.columns):
            print(f"Colunas necessárias não encontradas nos dados de {cidade}")
            continue

        # Verificar se a coluna de concentração existe
        if 'Valor' in df_total.columns:
            # Agrupar os dados por DataHora e Poluente, calculando a média de concentração
            df_agrupado = agrupar_poluente(df_total)
            
            # Salvar o CSV
            nome_saida = os.path.join(dados_por_cidade, f"{cidade}_emissoes.csv")
            try:
                df_agrupado.to_csv(nome_saida, index=False)
                print(f"Arquivo gerado para {cidade}: {nome_saida}")
            except Exception as e:
                print(f"Erro ao salvar arquivo para {cidade}: {e}")
        else:
            print(f"Coluna 'Valor' não encontrada nos dados de {cidade}, não foi possível gerar o arquivo.")


