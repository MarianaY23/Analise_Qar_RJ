
# -*- coding: utf-8 -*-
"""
Created on Sat May  3 20:52:13 2025

@author: debor
"""

# -*- coding: utf-8 -*-
"""
Script para realizar estatística univariada dos dados de qualidade do ar para
cada estação e poluente.

"""
import os
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose
from datetime import datetime
import numpy as np
from airQualityFigures import airQualityTimeSeries



# Função para calcular o Índice de Sazonalidade de Markham
def markham_index(monthly_values):
    """
    Calcula o Índice de Sazonalidade de Markham.
    """
    monthly_values = np.array(monthly_values)
    mean_value = np.nanmean(monthly_values)
    numerator = np.nansum(np.abs(monthly_values - mean_value))
    denominator = 2 * np.nansum(monthly_values)
    return (numerator / denominator) * 100

# Função para decompor a série temporal
def timeSeriesDecompose(aqTableAlvo, pol, repoPath, cidadeAlvo):
    """
    Realiza a decomposição da série temporal de um poluente e salva o gráfico.
    """
    dataDecompose = aqTableAlvo[['DateTime', pol]].copy()
    dataDecompose['DateTime'] = pd.to_datetime(dataDecompose['DateTime'])

    dataDecomposeMonthly = dataDecompose.groupby(
        pd.PeriodIndex(dataDecompose['DateTime'], freq="M")
    )[pol].mean()

    full_index = pd.period_range(
        start=dataDecomposeMonthly.index.min(),
        end=dataDecomposeMonthly.index.max(),
        freq='M'
    )

    complete_data = dataDecomposeMonthly.reindex(full_index).interpolate().dropna()
    complete_data.index = complete_data.index.to_timestamp()

    res = seasonal_decompose(complete_data, model='additive', period=12)

    # Criação da pasta específica da cidade
    cidade_path = os.path.join(repoPath, 'figuras', cidadeAlvo)
    os.makedirs(cidade_path, exist_ok=True)

    # Plotando
    fig, axes = plt.subplots(ncols=1, nrows=4, sharex=True, figsize=(10, 8))

    res.observed.plot(ax=axes[0], legend=False, color='blue')
    axes[0].set_ylabel('Observed')
    res.trend.plot(ax=axes[1], legend=False, color='red')
    axes[1].set_ylabel('Trend')
    res.seasonal.plot(ax=axes[2], legend=False, color='yellow')
    axes[2].set_ylabel('Seasonal')
    res.resid.plot(ax=axes[3], legend=False, color='gray')
    axes[3].set_ylabel('Residual')

    fig.suptitle(f'Decomposição: {cidadeAlvo} - {pol}', fontsize=14)
    fig.tight_layout()
    fig.subplots_adjust(top=0.93)

    output_path = os.path.join(cidade_path, f'decompose_{pol}_{cidadeAlvo}.png')
    fig.savefig(output_path)
    plt.close(fig)

    print(f"  Decomposição salva em: {output_path}")
    return res, complete_data

