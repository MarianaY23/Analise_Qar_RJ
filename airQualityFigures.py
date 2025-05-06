# -*- coding: utf-8 -*-
"""
Script para gerar gráficos e realizar análises dos dados de qualidade do ar
para cada estação e poluente.
"""



#%%
import matplotlib.pyplot as plt
import os
import numpy as np
from scipy import stats
import statsmodels.api as sm
import pandas as pd
from pmdarima.arima import auto_arima
import seaborn as sns


print("Todos os pacotes importados com sucesso!")


def airQualityHist(aqData, cidades, repoPath):
    os.makedirs(os.path.join(repoPath, 'figuras'), exist_ok=True)

    for cidade in cidades:
        try:
            print(f"\n Iniciando geração de gráficos de barras para {cidade}...")

            cidade_path = os.path.join(repoPath, 'figuras', cidade)
            os.makedirs(cidade_path, exist_ok=True)
      
            poluentes_unicos = aqData['Poluente'].unique()

            for poluente in poluentes_unicos:
                print(f"  ▶ Gerando gráfico de barras para poluente: {poluente}")

                dados = aqData[aqData['Poluente'] == poluente].copy()
                dados = dados.sort_values('datetime')  # Garante ordenação por tempo

                fig, ax = plt.subplots(figsize=(12, 5))
                ax.bar(dados['datetime'], dados['Valor'], width=0.05, color='tab:blue')  # Largura aumentada

                ax.set_title(f"{cidade} - {poluente}")
                ax.set_xlabel("Data e Hora")
                ax.set_ylabel("Concentração")
                ax.grid(True)
                plt.xticks(rotation=45)

                fig.tight_layout()
                nome_arquivo = os.path.join(cidade_path, f'Hist_{cidade}_{poluente}.png')
                fig.savefig(nome_arquivo)
                print(f" Gráfico salvo em: {nome_arquivo}")
                plt.close(fig)

        except Exception as e:
            print(f" Erro ao gerar gráfico de barras para {cidade}: {e}")


def airQualityTimeSeries(aqData_poluente, cidades, repoPath):
    """
    Geração de séries temporais com múltiplos subgráficos (um por poluente) em uma única imagem.
    """
    for cidade in cidades:
        print(f"\n Iniciando geração de séries temporais para: {cidade}")
        
        cidade_path = os.path.join(repoPath, 'figuras', cidade)
        os.makedirs(cidade_path, exist_ok=True)

        # Obtem os poluentes únicos
        poluentes = aqData_poluente['Poluente'].unique()
        num_poluentes = len(poluentes)

        if num_poluentes == 0:
            print(f"Nenhum poluente encontrado para {cidade}.")
            continue

        # Define a figura e os subplots
        fig, axs = plt.subplots(num_poluentes, 1, figsize=(12, 4 * num_poluentes), sharex=True)

        # Garante que axs é sempre uma lista
        if num_poluentes == 1:
            axs = [axs]

        for i, poluente in enumerate(poluentes):
            dados = aqData_poluente[aqData_poluente['Poluente'] == poluente]
            axs[i].plot(dados['DateTime'], dados['Valor'], label=poluente)
            axs[i].set_title(f"{cidade} - {poluente}")
            axs[i].set_ylabel("Concentração")
            axs[i].grid(True)
            axs[i].legend()

        axs[-1].set_xlabel("Data")
        plt.xticks(rotation=45)
        plt.tight_layout()

        # Define o nome do arquivo e o caminho
        nome_arquivo = os.path.join(cidade_path, f'SerieTemporal_{cidade}.png')

        # Verifica se o arquivo já existe e o remove antes de salvar
        if os.path.exists(nome_arquivo):
            os.remove(nome_arquivo)
            print(f" Arquivo existente encontrado e removido: {nome_arquivo}")

        # Salva a imagem final com todos os poluentes
        plt.savefig(nome_arquivo)
        plt.close(fig)
        print(f" Série temporal salva: {nome_arquivo}")

def obter_estacao_do_ano(data):
    mes = data.month
    if mes in [12, 1, 2]:
        return 'Verão'
    elif mes in [3, 4, 5]:
        return 'Outono'
    elif mes in [6, 7, 8]:
        return 'Inverno'
    else:
        return 'Primavera'

def airQualityBoxplot(aqData, cidade, repoPath):
    """
    Gera e salva boxplots por estação do ano para cada poluente em um DataFrame de qualidade do ar,
    salvando os gráficos na mesma estrutura de pastas da função airQualityHist.
    """
    # Criar diretório
    cidade_path = os.path.join(repoPath, 'figuras', cidade)
    os.makedirs(cidade_path, exist_ok=True)

    # Criar coluna 'Estacao' com base na data
    aqData['Estacao'] = pd.to_datetime(aqData['DateTime']).apply(obter_estacao_do_ano)

    # Selecionar colunas de poluentes
    poluentes = [col for col in aqData.columns if col not in ['DateTime', 'Estacao']]

    for poluente in poluentes:
        plt.figure(figsize=(10, 5))
        sns.boxplot(x='Estacao', y=poluente, data=aqData, palette='pastel')
        plt.title(f"{cidade} - Boxplot de {poluente} por Estação")
        plt.xlabel("Estação do Ano")
        plt.ylabel("Concentração")
        plt.grid(True)

        nome_arquivo = os.path.join(cidade_path, f'Boxplot_{cidade}_{poluente}_por_estacao.png')
        plt.savefig(nome_arquivo)
        print(f" Boxplot por estação salvo em: {nome_arquivo}")
        plt.close()
def normalityCheck(aqTableAlvo, repoPath, cidadeAlvo, pol):
    """
    Verifica a normalidade dos dados através de histogramas (Log, Box-Cox, Dados originais).
    """
    fig, ax = plt.subplots(3, figsize=(8, 6))

    # Log
    try:
        ax[0].hist(np.log(aqTableAlvo[pol].dropna()), facecolor='red', edgecolor='black')
        ax[0].set_title('Log')
    except Exception:
        ax[0].set_title('Log (erro)')

    # Box-Cox (somente valores positivos)
    data_boxcox = aqTableAlvo[pol].dropna()
    data_boxcox = data_boxcox[data_boxcox > 0]
    if len(data_boxcox) > 0:
        transformed, _ = stats.boxcox(data_boxcox)
        ax[1].hist(transformed, facecolor='green', edgecolor='black')
        ax[1].set_title('Box-Cox')
    else:
        ax[1].set_title('Box-Cox (sem dados válidos)')

    # Original
    ax[2].hist(aqTableAlvo[pol].dropna(), facecolor='blue', edgecolor='black')
    ax[2].set_title('Original')

    for a in ax:
        a.set_ylabel('Frequência')

    fig.tight_layout()
    fig.savefig(f'{repoPath}/figuras/histogramDataNormalization_{pol}_{cidadeAlvo}.png')
    plt.close(fig)
    return fig


def trendFigures(data, result):
    """
    Gera o gráfico de tendência (ACF e linha de tendência).
    """
    fig, ax = plt.subplots(2, figsize=(10, 6))

    sm.graphics.tsa.plot_acf(data, lags=5, ax=ax[0])
    ax[0].set_title('Autocorrelação ACF')

    trend_line = np.arange(len(data)) * result.slope + result.intercept
    data.plot(ax=ax[1])
    ax[1].plot(data.index, trend_line, color='red')
    ax[1].legend(['Dados', 'Tendência'])
    ax[1].set_title('Tendência')

    plt.tight_layout()
    return fig


