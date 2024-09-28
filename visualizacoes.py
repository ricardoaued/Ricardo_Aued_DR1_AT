# src/visualizacoes.py

from mplsoccer import Pitch
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import streamlit as st

def plot_pass_map(eventos):
    """
    Gera um mapa de passes usando mplsoccer.
    """
    # Filtrar passes
    passes = eventos[eventos['type'] == 'Pass']
    if passes.empty:
        fig, ax = plt.subplots(figsize=(10, 7))
        ax.text(0.5, 0.5, 'Nenhum passe encontrado para esta partida.',
                horizontalalignment='center', verticalalignment='center', fontsize=12, color='red')
        ax.axis('off')
        return fig
    # Criar campo
    pitch = Pitch(pitch_type='statsbomb', pitch_color='#aabb97', line_color='white')
    fig, ax = plt.subplots(figsize=(10, 7))
    pitch.draw(ax=ax)
    # Plotar passes
    pitch.arrows(
        xstart=passes['location'].apply(lambda loc: loc[0]),
        ystart=passes['location'].apply(lambda loc: loc[1]),
        xend=passes['pass_end_location'].apply(lambda loc: loc[0]),
        yend=passes['pass_end_location'].apply(lambda loc: loc[1]),
        width=2,
        headwidth=10,
        color='blue',
        ax=ax,
        alpha=0.7
    )
    ax.set_title('Mapa de Passes', fontsize=16)
    return fig

def plot_shot_map(eventos):
    """
    Gera um mapa de chutes usando mplsoccer.
    """
    # Filtrar chutes
    chutes = eventos[eventos['type'] == 'Shot']
    if chutes.empty:
        fig, ax = plt.subplots(figsize=(10, 7))
        ax.text(0.5, 0.5, 'Nenhum chute encontrado para esta partida.',
                horizontalalignment='center', verticalalignment='center', fontsize=12, color='red')
        ax.axis('off')
        return fig
    # Criar campo
    pitch = Pitch(pitch_type='statsbomb', pitch_color='#aabb97', line_color='white')
    fig, ax = plt.subplots(figsize=(10, 7))
    pitch.draw(ax=ax)
    # Plotar chutes
    for _, chute in chutes.iterrows():
        x, y = chute['location']
        outcome = chute['shot_outcome']
        color = 'red' if outcome == 'Goal' else 'blue'
        pitch.scatter(x, y, ax=ax, c=color, s=100, edgecolors='black', linewidth=1, alpha=0.7)
    ax.set_title('Mapa de Chutes', fontsize=16)
    return fig

def plot_passes_vs_goals(eventos):
    """
    Cria um gráfico de dispersão entre número de passes e gols por jogador.
    """
    # Passes por jogador
    passes_por_jogador = eventos[eventos['type'] == 'Pass'].groupby('player').size().reset_index(name='passes')
    # Gols por jogador
    gols_por_jogador = eventos[(eventos['type'] == 'Shot') & (eventos['shot_outcome'] == 'Goal')].groupby('player').size().reset_index(name='gols')
    # Combinar dados
    dados = passes_por_jogador.merge(gols_por_jogador, on='player', how='inner')
    if dados.empty:
        fig, ax = plt.subplots()
        ax.text(0.5, 0.5, 'Dados insuficientes para gerar o gráfico.',
                horizontalalignment='center', verticalalignment='center', fontsize=12, color='red')
        ax.axis('off')
        return fig
    # Plotar gráfico
    fig, ax = plt.subplots()
    sns.scatterplot(data=dados, x='passes', y='gols', ax=ax)
    ax.set_title('Relação entre Passes e Gols', fontsize=16)
    ax.set_xlabel('Número de Passes')
    ax.set_ylabel('Número de Gols')
    return fig

