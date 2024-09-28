# src/carregar_dados.py

import streamlit as st
from statsbombpy import sb
import pandas as pd

@st.cache_data(ttl=3600)
def obter_competicoes():
    """
    Retorna um DataFrame com todas as competições disponíveis.
    """
    competicoes = sb.competitions()
    return competicoes

@st.cache_data(ttl=3600)
def obter_temporadas(competition_id):
    """
    Retorna uma lista de tuplas (season_id, season_name) com as temporadas disponíveis para uma competição específica.
    """
    competicoes = sb.competitions()
    competencia = competicoes[competicoes['competition_id'] == competition_id]
    if competencia.empty:
        st.error(f"Nenhuma competição encontrada com competition_id: {competition_id}")
        return []
    # Extrair 'season_id' e 'season_name'
    temporadas = competencia[['season_id', 'season_name']].drop_duplicates()
    # Converter para lista de tuplas
    season_list = list(zip(temporadas['season_id'], temporadas['season_name']))
    return season_list

@st.cache_data(ttl=3600)
def obter_partidas(competition_id, season_id):
    """
    Retorna um DataFrame com as partidas disponíveis para uma competição e temporada específicas.
    """
    with st.spinner('Carregando partidas...'):
        partidas = sb.matches(competition_id=competition_id, season_id=season_id)
    return partidas

@st.cache_data(ttl=3600)
def obter_eventos(match_id):
    """
    Retorna um DataFrame com os eventos de uma partida específica.
    """
    with st.spinner('Carregando eventos da partida...'):
        eventos = sb.events(match_id=match_id)
    return eventos

@st.cache_data(ttl=3600)
def obter_estatisticas_jogador(eventos, jogador):
    """
    Retorna um dicionário com estatísticas do jogador na partida.
    """
    eventos_jogador = eventos[eventos['player'] == jogador]
    passes_jogador = eventos_jogador[eventos_jogador['type'] == 'Pass']
    passes_sucesso = passes_jogador[passes_jogador['pass_outcome'].isna()]
    total_passes = len(passes_jogador)
    total_passes_sucesso = len(passes_sucesso)

    chutes_jogador = eventos_jogador[eventos_jogador['type'] == 'Shot']
    gols_jogador = chutes_jogador[chutes_jogador['shot_outcome'] == 'Goal']
    total_chutes = len(chutes_jogador)
    total_gols = len(gols_jogador)
    taxa_conversao = (total_gols / total_chutes) * 100 if total_chutes > 0 else 0

    estatisticas = {
        'passes': total_passes,
        'passes_sucesso': total_passes_sucesso,
        'chutes': total_chutes,
        'gols': total_gols,
        'taxa_conversao': taxa_conversao
    }
    return estatisticas

