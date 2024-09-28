# src/dashboard.py

import streamlit as st
from carregar_dados import (
    obter_competicoes,
    obter_temporadas,
    obter_partidas,
    obter_eventos,
    obter_estatisticas_jogador
)
from visualizacoes import plot_pass_map, plot_shot_map, plot_passes_vs_goals

# Configuração da página
st.set_page_config(page_title='Dashboard de Análise de Futebol', layout='wide')

# Função para inicializar o Session State
def inicializar_session_state():
    if 'competicao_nome' not in st.session_state:
        st.session_state.competicao_nome = None
    if 'temporada_nome' not in st.session_state:
        st.session_state.temporada_nome = None
    if 'partida_nome' not in st.session_state:
        st.session_state.partida_nome = None
    if 'jogador_selecionado' not in st.session_state:
        st.session_state.jogador_selecionado = 'Todos'

inicializar_session_state()

# Título do Dashboard
st.title('Dashboard Interativo de Análise de Futebol')

# Obter competições
competicoes = obter_competicoes()
competicao_opcoes = competicoes['competition_name'].unique().tolist()

# Selecionar competição
st.sidebar.header('Seleção de Competição')
st.session_state.competicao_nome = st.sidebar.selectbox(
    'Selecione a Competição',
    options=competicao_opcoes,
    index=0 if st.session_state.competicao_nome is None else competicao_opcoes.index(st.session_state.competicao_nome)
)

# Filtrar competição selecionada
competicao_id = competicoes[competicoes['competition_name'] == st.session_state.competicao_nome]['competition_id'].values[0]

# Obter temporadas
temporadas = obter_temporadas(competicao_id)
temporada_opcoes = [nome for _, nome in temporadas]

# Selecionar temporada
st.sidebar.header('Seleção de Temporada')
if temporadas:
    st.session_state.temporada_nome = st.sidebar.selectbox(
        'Selecione a Temporada',
        options=temporada_opcoes,
        index=0 if st.session_state.temporada_nome is None else temporada_opcoes.index(st.session_state.temporada_nome)
    )
    temporada_id = temporadas[temporada_opcoes.index(st.session_state.temporada_nome)][0]
else:
    st.warning("Nenhuma temporada encontrada para a competição selecionada.")
    st.stop()

# Obter partidas
partidas = obter_partidas(competicao_id, temporada_id)
if partidas.empty:
    st.warning("Nenhuma partida encontrada para a temporada selecionada.")
    st.stop()

# Criar nome da partida
partidas['match_name'] = partidas['home_team'] + ' vs ' + partidas['away_team']
partida_opcoes = partidas['match_name'].unique().tolist()

# Selecionar partida
st.sidebar.header('Seleção de Partida')
st.session_state.partida_nome = st.sidebar.selectbox(
    'Selecione a Partida',
    options=partida_opcoes,
    index=0 if st.session_state.partida_nome is None else partida_opcoes.index(st.session_state.partida_nome)
)
partida_selecionada = partidas[partidas['match_name'] == st.session_state.partida_nome]
match_id = partida_selecionada['match_id'].values[0]

# Exibir informações básicas
st.header(f'{st.session_state.partida_nome} - {st.session_state.temporada_nome}')

# Métricas da partida
gols_casa = partida_selecionada['home_score'].values[0]
gols_fora = partida_selecionada['away_score'].values[0]
col1, col2 = st.columns(2)
col1.metric(partida_selecionada['home_team'].values[0], gols_casa)
col2.metric(partida_selecionada['away_team'].values[0], gols_fora)

# Obter eventos
eventos = obter_eventos(match_id)

# Filtros adicionais
st.sidebar.markdown('---')
st.sidebar.header('Filtros Adicionais')

# Filtro de jogador
jogadores = eventos['player'].dropna().unique().tolist()
jogador_opcoes = ['Todos'] + jogadores
st.session_state.jogador_selecionado = st.sidebar.selectbox(
    'Selecione o Jogador',
    options=jogador_opcoes,
    index=0 if st.session_state.jogador_selecionado == 'Todos' else jogador_opcoes.index(st.session_state.jogador_selecionado)
)

# Filtro de tipos de evento
tipos_evento = eventos['type'].unique().tolist()
tipos_selecionados = st.sidebar.multiselect(
    'Selecione os Tipos de Evento',
    options=tipos_evento,
    default=tipos_evento
)

# Aplicar filtros
if st.session_state.jogador_selecionado != 'Todos':
    eventos = eventos[eventos['player'] == st.session_state.jogador_selecionado]
eventos = eventos[eventos['type'].isin(tipos_selecionados)]

# Botão de download
csv = eventos.to_csv(index=False)
st.sidebar.download_button(
    label="Baixar Dados Filtrados",
    data=csv,
    file_name='dados_filtrados.csv',
    mime='text/csv'
)

# Exibir métricas do jogador selecionado
if st.session_state.jogador_selecionado != 'Todos':
    estatisticas = obter_estatisticas_jogador(eventos, st.session_state.jogador_selecionado)
    st.markdown(f"### Estatísticas de {st.session_state.jogador_selecionado}")
    col1, col2, col3 = st.columns(3)
    col1.metric('Passes', estatisticas['passes'])
    col2.metric('Passes Bem-sucedidos', estatisticas['passes_sucesso'])
    col3.metric('Taxa de Conversão', f"{estatisticas['taxa_conversao']:.1f}%")

# Visualizações
st.markdown('## Visualizações')

tab1, tab2, tab3 = st.tabs(['Mapa de Passes', 'Mapa de Chutes', 'Análise de Passes vs Gols'])

with tab1:
    st.subheader('Mapa de Passes')
    fig_passes = plot_pass_map(eventos)
    st.pyplot(fig_passes)

with tab2:
    st.subheader('Mapa de Chutes')
    fig_shots = plot_shot_map(eventos)
    st.pyplot(fig_shots)

with tab3:
    st.subheader('Relação entre Passes e Gols')
    fig_relation = plot_passes_vs_goals(eventos)
    st.pyplot(fig_relation)

# Formulário interativo para comparação entre jogadores
st.sidebar.markdown('---')
st.sidebar.header('Comparação entre Jogadores')
with st.sidebar.form(key='form_comparacao'):
    jogadores_selecionados = st.multiselect(
        'Selecione até Dois Jogadores para Comparar',
        options=jogadores,
        max_selections=2
    )
    submit_button = st.form_submit_button(label='Comparar')

if submit_button and len(jogadores_selecionados) == 2:
    jogador1, jogador2 = jogadores_selecionados
    estatisticas1 = obter_estatisticas_jogador(eventos, jogador1)
    estatisticas2 = obter_estatisticas_jogador(eventos, jogador2)
    st.markdown(f"### Comparação entre {jogador1} e {jogador2}")
    col1, col2 = st.columns(2)
    with col1:
        st.header(jogador1)
        st.metric('Passes', estatisticas1['passes'])
        st.metric('Passes Bem-sucedidos', estatisticas1['passes_sucesso'])
        st.metric('Gols', estatisticas1['gols'])
        st.metric('Taxa de Conversão', f"{estatisticas1['taxa_conversao']:.1f}%")
    with col2:
        st.header(jogador2)
        st.metric('Passes', estatisticas2['passes'])
        st.metric('Passes Bem-sucedidos', estatisticas2['passes_sucesso'])
        st.metric('Gols', estatisticas2['gols'])
        st.metric('Taxa de Conversão', f"{estatisticas2['taxa_conversao']:.1f}%")
elif submit_button and len(jogadores_selecionados) != 2:
    st.warning("Por favor, selecione exatamente dois jogadores para comparar.")
