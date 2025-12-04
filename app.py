import streamlit as st
import pandas as pd
import os
import folium
from streamlit_folium import st_folium

# Configuração da página
logo_icon_path = os.path.join(os.path.dirname(__file__), "image", "app", "Logo.png")
st.set_page_config(
    page_title="SIOUT-RS - Análise de Dados",
    page_icon=logo_icon_path if os.path.exists(logo_icon_path) else "🌊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Título principal
st.markdown("<h1 style='text-align: center;'>Ferramenta de Comparação de Registros - SNISB vs SIOUT-RS</h1>", unsafe_allow_html=True)
st.markdown("---")

# Função para carregar os dados com cache
@st.cache_data
def carregar_dados():
    """Carrega o arquivo de dados (CSV ou Excel) e retorna um DataFrame"""
    try:
        # Tentar carregar CSV primeiro (sem limite de caracteres)
        csv_path = os.path.join(os.path.dirname(__file__), "RELATORIO_FINAL_SNISB_SIOUT.csv")
        xlsx_path = os.path.join(os.path.dirname(__file__), "RELATORIO_FINAL_SNISB_SIOUT.xlsx")
        
        # Configurar pandas para não truncar strings longas
        pd.set_option('display.max_colwidth', None)
        
        if os.path.exists(csv_path):
            # Carregar CSV (preferencial - sem limite de 32.767 caracteres)
            df = pd.read_csv(csv_path, dtype={'POLIGONO_ANA': str}, encoding='utf-8-sig')
            return df
        elif os.path.exists(xlsx_path):
            # Fallback para Excel (pode ter polígonos truncados)
            df = pd.read_excel(xlsx_path, dtype={'POLIGONO_ANA': str})
            return df
        else:
            st.error("Arquivo de dados não encontrado. Procure por RELATORIO_FINAL_SNISB_SIOUT.csv ou .xlsx")
            return None
    except Exception as e:
        st.error(f"Erro ao carregar o arquivo: {e}")
        return None

# Carregar os dados
df = carregar_dados()

if df is not None:
    # Tabs para diferentes visualizações
    tab1, tab2 = st.tabs(["Visualizar Dados", "Ajuda/Glossário"])
    
    with tab1:
        st.markdown("<h3 style='text-align: center;'>Filtros de Dados</h3>", unsafe_allow_html=True)
        st.markdown("")
        
        # Primeira linha: Filtro de Data
        st.markdown("<p style='text-align: center; margin-bottom: 5px;'><small>Período de Cadastro</small></p>", unsafe_allow_html=True)
        col_data1, col_data2, col_data3 = st.columns([1, 1, 1])
        
        # Converter coluna de data se existir
        if 'DATA_DO_CADASTRO' in df.columns:
            df['DATA_DO_CADASTRO'] = pd.to_datetime(df['DATA_DO_CADASTRO'], errors='coerce')
            data_min = df['DATA_DO_CADASTRO'].min()
            data_max = df['DATA_DO_CADASTRO'].max()
            
            with col_data2:
                col_inicio, col_fim = st.columns(2)
                with col_inicio:
                    data_inicio = st.date_input(
                        "Data Inicial",
                        value=data_min,
                        min_value=data_min,
                        max_value=data_max,
                        format="DD/MM/YYYY",
                        label_visibility="visible"
                    )
                
                with col_fim:
                    data_fim = st.date_input(
                        "Data Final",
                        value=data_max,
                        min_value=data_min,
                        max_value=data_max,
                        format="DD/MM/YYYY",
                        label_visibility="visible"
                    )
        
        st.markdown("")
        
        # Segunda linha: Filtros de Características Físicas (4 filtros na mesma linha)
        st.markdown("<p style='text-align: center; margin-bottom: 5px;'><small>Filtros de Características Físicas</small></p>", unsafe_allow_html=True)
        col_fis1, col_fis2, col_fis3, col_fis4 = st.columns(4)
        
        with col_fis1:
            st.markdown("<p style='text-align: center; margin-bottom: 0;'><small>Situação Cadastro SNISB</small></p>", unsafe_allow_html=True)
            if 'SITUACAO_CADASTRO_SNISB' in df.columns:
                opcoes_cadastro = sorted(df['SITUACAO_CADASTRO_SNISB'].dropna().unique().tolist())
                filtro_cadastro = st.multiselect(
                    "Situação Cadastro SNISB",
                    opcoes_cadastro,
                    default=[],
                    label_visibility="collapsed",
                    placeholder="Selecione..."
                )
            else:
                filtro_cadastro = []
        
        with col_fis2:
            st.markdown("<p style='text-align: center; margin-bottom: 0;'><small>Situação Massa D'água</small></p>", unsafe_allow_html=True)
            if 'SITUACAO_MASSA_DAGUA' in df.columns:
                opcoes_massa = sorted(df['SITUACAO_MASSA_DAGUA'].dropna().unique().tolist())
                filtro_massa = st.multiselect(
                    "Situação Massa D'água",
                    opcoes_massa,
                    default=[],
                    label_visibility="collapsed",
                    placeholder="Selecione..."
                )
            else:
                filtro_massa = []
        
        with col_fis3:
            st.markdown("<p style='text-align: center; margin-bottom: 0;'><small>Situação Comparação SIOUT</small></p>", unsafe_allow_html=True)
            if 'SITUACAO_COMPARACAO_SIOUT' in df.columns:
                opcoes_comparacao = sorted(df['SITUACAO_COMPARACAO_SIOUT'].dropna().unique().tolist())
                filtro_comparacao = st.multiselect(
                    "Situação Comparação SIOUT",
                    opcoes_comparacao,
                    default=[],
                    label_visibility="collapsed",
                    placeholder="Selecione..."
                )
            else:
                filtro_comparacao = []
        
        with col_fis4:
            st.markdown("<p style='text-align: center; margin-bottom: 0;'><small>Código SNISB</small></p>", unsafe_allow_html=True)
            if 'CODIGO_SNISB' in df.columns:
                # Obter lista de códigos únicos
                codigos_unicos = sorted(df['CODIGO_SNISB'].dropna().astype(str).unique().tolist())
                
                # Campo de busca com multiseleção
                filtro_codigo = st.multiselect(
                    "Código SNISB",
                    codigos_unicos,
                    default=[],
                    label_visibility="collapsed",
                    placeholder="Selecione...",
                    key="filtro_codigo_snisb"
                )
            else:
                filtro_codigo = []
        
        st.markdown("")
        
        # Terceira linha: Novos filtros (Uso, Material e Empreendedor)
        st.markdown("<p style='text-align: center; margin-bottom: 5px;'><small>Filtros de Uso e Empreendedor</small></p>", unsafe_allow_html=True)
        col_uso1, col_uso2, col_uso3 = st.columns(3)
        
        with col_uso1:
            st.markdown("<p style='text-align: center; margin-bottom: 0;'><small>Finalidade de Uso (SNISB)</small></p>", unsafe_allow_html=True)
            if 'USO_SNISB' in df.columns:
                opcoes_uso = sorted(df['USO_SNISB'].dropna().unique().tolist())
                filtro_uso = st.multiselect(
                    "Finalidade de Uso",
                    opcoes_uso,
                    default=[],
                    label_visibility="collapsed",
                    placeholder="Selecione...",
                    key="filtro_uso_snisb"
                )
            else:
                filtro_uso = []
        
        with col_uso2:
            st.markdown("<p style='text-align: center; margin-bottom: 0;'><small>Tipo de Material</small></p>", unsafe_allow_html=True)
            if 'TIPO_DE_MATERIAL' in df.columns:
                opcoes_material = sorted(df['TIPO_DE_MATERIAL'].dropna().unique().tolist())
                filtro_material = st.multiselect(
                    "Tipo de Material",
                    opcoes_material,
                    default=[],
                    label_visibility="collapsed",
                    placeholder="Selecione...",
                    key="filtro_tipo_material"
                )
            else:
                filtro_material = []
        
        with col_uso3:
            st.markdown("<p style='text-align: center; margin-bottom: 0;'><small>Empreendedor</small></p>", unsafe_allow_html=True)
            if 'EMPREENDEDOR_SNISB' in df.columns:
                # Obter lista de empreendedores únicos
                empreendedores_unicos = sorted(df['EMPREENDEDOR_SNISB'].dropna().astype(str).unique().tolist())
                
                filtro_empreendedor = st.multiselect(
                    "Empreendedor",
                    empreendedores_unicos,
                    default=[],
                    label_visibility="collapsed",
                    placeholder="Selecione...",
                    key="filtro_empreendedor_snisb"
                )
            else:
                filtro_empreendedor = []
        
        # Aplicar os filtros
        df_filtrado = df.copy()
        
        # Verificar se algum filtro está ativo
        filtros_ativos = []
        
        # Filtro de data
        if 'DATA_DO_CADASTRO' in df.columns:
            data_inicio_dt = pd.to_datetime(data_inicio)
            data_fim_dt = pd.to_datetime(data_fim)
            
            # Verificar se o filtro de data está ativo (diferente do range completo)
            if data_inicio_dt > data_min or data_fim_dt < data_max:
                df_filtrado = df_filtrado[
                    (df_filtrado['DATA_DO_CADASTRO'] >= data_inicio_dt) & 
                    (df_filtrado['DATA_DO_CADASTRO'] <= data_fim_dt)
                ]
                filtros_ativos.append('DATA_DO_CADASTRO')
        
        # Filtro de Código SNISB
        if filtro_codigo:
            if 'CODIGO_SNISB' in df_filtrado.columns:
                df_filtrado = df_filtrado[df_filtrado['CODIGO_SNISB'].astype(str).isin(filtro_codigo)]
                filtros_ativos.append('CODIGO_SNISB')
        
        if filtro_cadastro:
            df_filtrado = df_filtrado[df_filtrado['SITUACAO_CADASTRO_SNISB'].isin(filtro_cadastro)]
            filtros_ativos.append('SITUACAO_CADASTRO_SNISB')
        
        if filtro_massa:
            df_filtrado = df_filtrado[df_filtrado['SITUACAO_MASSA_DAGUA'].isin(filtro_massa)]
            filtros_ativos.append('SITUACAO_MASSA_DAGUA')
        
        if filtro_comparacao:
            df_filtrado = df_filtrado[df_filtrado['SITUACAO_COMPARACAO_SIOUT'].isin(filtro_comparacao)]
            filtros_ativos.append('SITUACAO_COMPARACAO_SIOUT')
        
        # Filtro de Uso SNISB
        if filtro_uso:
            if 'USO_SNISB' in df_filtrado.columns:
                df_filtrado = df_filtrado[df_filtrado['USO_SNISB'].isin(filtro_uso)]
                filtros_ativos.append('USO_SNISB')
        
        # Filtro de Tipo de Material
        if filtro_material:
            if 'TIPO_DE_MATERIAL' in df_filtrado.columns:
                df_filtrado = df_filtrado[df_filtrado['TIPO_DE_MATERIAL'].isin(filtro_material)]
                filtros_ativos.append('TIPO_DE_MATERIAL')
        
        # Filtro de Empreendedor
        if filtro_empreendedor:
            if 'EMPREENDEDOR_SNISB' in df_filtrado.columns:
                df_filtrado = df_filtrado[df_filtrado['EMPREENDEDOR_SNISB'].astype(str).isin(filtro_empreendedor)]
                filtros_ativos.append('EMPREENDEDOR_SNISB')
        
        # Definir texto baseado se há filtros ativos
        tem_filtros = len(filtros_ativos) > 0
        titulo_tabela = "Dados Filtrados" if tem_filtros else "Tabela Completa"
        
        # Mostrar contador de registros filtrados
        st.markdown(f"<p style='text-align: center;'>Mostrando <strong>{len(df_filtrado):,}</strong> registros de um total de <strong>{len(df):,}</strong></p>", unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown(f"<h3 style='text-align: center;'>{titulo_tabela}</h3>", unsafe_allow_html=True)
        
        if len(df_filtrado) > 0:
            # Sistema de paginação
            registros_por_pagina = 50
            total_paginas = (len(df_filtrado) - 1) // registros_por_pagina + 1
            
            # Inicializar página atual no session_state
            if 'pagina_atual' not in st.session_state:
                st.session_state.pagina_atual = 1
            
            # Calcular índices para a página atual
            inicio = (st.session_state.pagina_atual - 1) * registros_por_pagina
            fim = min(inicio + registros_por_pagina, len(df_filtrado))
            
            # Mostrar informação da paginação
            st.markdown(f"<p style='text-align: center;'><small>Exibindo registros {inicio + 1} a {fim} de {len(df_filtrado):,}</small></p>", unsafe_allow_html=True)
            
            # Obter dados da página atual
            df_pagina = df_filtrado.iloc[inicio:fim].copy()
            
            # Aplicar estilização na tabela
            def colorir_situacao(val):
                """Aplica cores baseadas no valor da situação"""
                if pd.isna(val):
                    return ''
                val_str = str(val).lower()
                if 'totalmente compatível' in val_str or 'selecionado' in val_str or 'compatível com polígono' in val_str:
                    return 'background-color: #d4edda; color: #155724'
                elif 'parcialmente' in val_str or 'apenas geograficamente' in val_str:
                    return 'background-color: #fff3cd; color: #856404'
                elif 'incompatível' in val_str or 'descartado' in val_str:
                    return 'background-color: #f8d7da; color: #721c24'
                return ''
            
            # Aplicar estilização se as colunas existirem
            colunas_estilo = []
            if 'SITUACAO_CADASTRO_SNISB' in df_pagina.columns:
                colunas_estilo.append('SITUACAO_CADASTRO_SNISB')
            if 'SITUACAO_MASSA_DAGUA' in df_pagina.columns:
                colunas_estilo.append('SITUACAO_MASSA_DAGUA')
            if 'SITUACAO_COMPARACAO_SIOUT' in df_pagina.columns:
                colunas_estilo.append('SITUACAO_COMPARACAO_SIOUT')
            
            if colunas_estilo:
                styled_df = df_pagina.style.map(colorir_situacao, subset=colunas_estilo)
                st.dataframe(styled_df, width='stretch', height=600, column_config={
                    col: st.column_config.TextColumn(width="medium") for col in df_pagina.columns
                })
            else:
                st.dataframe(df_pagina, width='stretch', height=600, column_config={
                    col: st.column_config.TextColumn(width="medium") for col in df_pagina.columns
                })
            
            # Controles de paginação abaixo da tabela (próximo ao dataset)
            # Função para gerar os números de página
            def gerar_paginas_visiveis(pagina_atual, total_paginas):
                """Gera lista de páginas visíveis com reticências"""
                paginas = []
                
                # Sempre mostrar primeira página
                paginas.append(1)
                
                # Mostrar páginas ao redor da atual
                inicio_range = max(2, pagina_atual - 2)
                fim_range = min(total_paginas - 1, pagina_atual + 2)
                
                # Adicionar reticências antes se necessário
                if inicio_range > 2:
                    paginas.append('...')
                
                # Adicionar páginas do range
                for p in range(inicio_range, fim_range + 1):
                    paginas.append(p)
                
                # Adicionar reticências depois se necessário
                if fim_range < total_paginas - 1:
                    paginas.append('...')
                
                # Sempre mostrar última página se houver mais de uma
                if total_paginas > 1:
                    paginas.append(total_paginas)
                
                return paginas
            
            paginas_visiveis = gerar_paginas_visiveis(st.session_state.pagina_atual, total_paginas)
            
            # Estilo CSS para os botões de paginação
            st.markdown("""
            <style>
            /* Botões de paginação - Secondary */
            div[data-testid="column"] button[kind="secondary"] {
                background-color: #f8f9fa !important;
                color: #495057 !important;
                border: 1px solid #dee2e6 !important;
                padding: 0.25rem 0.5rem !important;
                font-size: 0.875rem !important;
                height: 2rem !important;
            }
            
            /* Botões de paginação - Primary (página selecionada) */
            button[kind="primary"], div[data-testid="column"] button[kind="primary"] {
                background-color: #cfe2ff !important;
                color: #084298 !important;
                border: 1px solid #9ec5fe !important;
                padding: 0.25rem 0.5rem !important;
                font-size: 0.875rem !important;
                font-weight: 600 !important;
                height: 2rem !important;
            }
            
            button[kind="primary"]:hover {
                background-color: #b6d4fe !important;
                color: #052c65 !important;
            }
            
            .stButton button[kind="primary"] p {
                color: #084298 !important;
            }
            </style>
            """, unsafe_allow_html=True)
            
            # Criar colunas centralizadas para os botões de paginação
            total_botoes = len(paginas_visiveis) + 2  # +2 para botões anterior/próximo
            espaco_lateral = (10 - total_botoes) / 2 if total_botoes < 10 else 0.5
            
            colunas_layout = [espaco_lateral] + [0.5] + [0.8] * len(paginas_visiveis) + [0.5] + [espaco_lateral]
            colunas = st.columns(colunas_layout)
            
            col_offset = 1  # Começar após o espaço lateral
            
            # Botão Anterior
            with colunas[col_offset]:
                if st.button("◀", key="prev", disabled=(st.session_state.pagina_atual == 1), use_container_width=True):
                    st.session_state.pagina_atual -= 1
                    st.rerun()
            
            # Botões de número de página
            for idx, pagina in enumerate(paginas_visiveis, start=1):
                with colunas[col_offset + idx]:
                    if pagina == '...':
                        st.markdown("<p style='text-align: center; margin-top: 0.25rem;'>...</p>", unsafe_allow_html=True)
                    else:
                        if st.button(
                            str(pagina),
                            key=f"page_{pagina}",
                            type="primary" if pagina == st.session_state.pagina_atual else "secondary",
                            use_container_width=True
                        ):
                            st.session_state.pagina_atual = pagina
                            st.rerun()
            
            # Botão Próximo
            with colunas[col_offset + len(paginas_visiveis) + 1]:
                if st.button("▶", key="next", disabled=(st.session_state.pagina_atual == total_paginas), use_container_width=True):
                    st.session_state.pagina_atual += 1
                    st.rerun()
            
            # Botão de download abaixo da paginação
            st.markdown("")
            
            col1, col2, col3 = st.columns([1, 1, 1])
            
            with col2:
                # Texto do botão
                texto_botao = "Baixar Dados Filtrados" if tem_filtros else "Baixar Todos os Dados"
                
                # Usar popover para mostrar opções de formato
                with st.popover(texto_botao, use_container_width=True):
                    st.markdown("**Escolha o formato do arquivo:**")
                    
                    from io import BytesIO, StringIO
                    
                    timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
                    prefixo = "dados_filtrados" if tem_filtros else "dados_completos"
                    
                    # Botão Excel
                    buffer_xlsx = BytesIO()
                    with pd.ExcelWriter(buffer_xlsx, engine='openpyxl') as writer:
                        df_filtrado.to_excel(writer, index=False, sheet_name='Dados')
                    buffer_xlsx.seek(0)
                    
                    st.download_button(
                        label="Excel (.xlsx)",
                        data=buffer_xlsx,
                        file_name=f"{prefixo}_{timestamp}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True,
                        key="download_xlsx"
                    )
                    
                    # Botão CSV
                    buffer_csv = StringIO()
                    df_filtrado.to_csv(buffer_csv, index=False, encoding='utf-8-sig', sep=';')
                    dados_csv = buffer_csv.getvalue().encode('utf-8-sig')
                    
                    st.download_button(
                        label="CSV (.csv)",
                        data=dados_csv,
                        file_name=f"{prefixo}_{timestamp}.csv",
                        mime="text/csv",
                        use_container_width=True,
                        key="download_csv"
                    )
                    
                    # Botão JSON
                    buffer_json = StringIO()
                    df_filtrado.to_json(buffer_json, orient='records', force_ascii=False, indent=2, date_format='iso')
                    dados_json = buffer_json.getvalue().encode('utf-8')
                    
                    st.download_button(
                        label="JSON (.json)",
                        data=dados_json,
                        file_name=f"{prefixo}_{timestamp}.json",
                        mime="application/json",
                        use_container_width=True,
                        key="download_json"
                    )
            
            # Mapa de localização
            st.markdown("---")
            st.markdown("<h3 style='text-align: center;'>Mapa de Localização</h3>", unsafe_allow_html=True)
            st.markdown("")
            
            # Adicionar CSS para o spinner de carregamento
            st.markdown("""
            <style>
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            .loading-spinner {
                text-align: center;
                padding: 40px;
            }
            .loading-spinner::after {
                content: "";
                display: inline-block;
                width: 40px;
                height: 40px;
                border: 4px solid #f3f3f3;
                border-top: 4px solid #3498db;
                border-radius: 50%;
                animation: spin 1s linear infinite;
            }
            </style>
            """, unsafe_allow_html=True)
            
            # Mostrar spinner de carregamento
            loading_placeholder = st.empty()
            loading_placeholder.markdown('<div class="loading-spinner"></div>', unsafe_allow_html=True)
            
            # Verificar se existem colunas de latitude e longitude
            tem_coordenadas = 'LATITUDE' in df_filtrado.columns and 'LONGITUDE' in df_filtrado.columns
            
            if tem_coordenadas:
                # Preparar dados do mapa usando colunas LATITUDE e LONGITUDE diretamente
                colunas_mapa = ['LATITUDE', 'LONGITUDE']
                colunas_popup = ['CODIGO_SNISB', 'SITUACAO_CADASTRO_SNISB', 'SITUACAO_MASSA_DAGUA', 'SITUACAO_COMPARACAO_SIOUT']
                for col in colunas_popup:
                    if col in df_filtrado.columns:
                        colunas_mapa.append(col)
                
                # Adicionar coluna POLIGONO_ANA se existir (para uso posterior)
                if 'POLIGONO_ANA' in df_filtrado.columns:
                    colunas_mapa.append('POLIGONO_ANA')
                
                df_mapa = df_filtrado[colunas_mapa].copy()
                
                # Renomear para lowercase para consistência
                df_mapa = df_mapa.rename(columns={'LATITUDE': 'latitude', 'LONGITUDE': 'longitude'})
                
                # Converter para numérico e remover valores inválidos
                df_mapa['latitude'] = pd.to_numeric(df_mapa['latitude'], errors='coerce')
                df_mapa['longitude'] = pd.to_numeric(df_mapa['longitude'], errors='coerce')
                df_mapa = df_mapa.dropna(subset=['latitude', 'longitude'])
                
                # Validar coordenadas do Brasil (aproximado)
                df_mapa = df_mapa[
                    (df_mapa['latitude'] >= -34) & (df_mapa['latitude'] <= 6) &
                    (df_mapa['longitude'] >= -74) & (df_mapa['longitude'] <= -28)
                ]
                
                if len(df_mapa) > 0:
                    # Calcular centro do mapa
                    center_lat = df_mapa['latitude'].mean()
                    center_lon = df_mapa['longitude'].mean()
                    
                    # Criar mapa Folium com imagem de satélite Esri (como base fixa, sem aparecer no controle)
                    mapa = folium.Map(
                        location=[center_lat, center_lon],
                        zoom_start=7,
                        tiles=None  # Não usar tiles padrão
                    )
                    
                    # Adicionar tiles de satélite como base sem controle
                    folium.TileLayer(
                        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                        attr='Esri World Imagery',
                        name='Satélite Esri',
                        overlay=False,
                        control=False  # Não mostrar no controle de camadas
                    ).add_to(mapa)
                    
                    # Criar grupos de camadas para controle independente (apenas as camadas controláveis)
                    grupo_poligonos = folium.FeatureGroup(name='🗺️ Polígonos ANA', show=True)
                    grupo_pontos = folium.FeatureGroup(name='🔵 Pontos das Barragens', show=True)
                    
                    # Adicionar polígonos ANA ao grupo
                    with st.spinner('Carregando polígonos ANA...'):
                            from shapely import wkt
                            import json
                            
                            # Obter polígonos únicos apenas dos registros filtrados
                            poligonos_unicos = df_mapa[df_mapa['POLIGONO_ANA'].notna()]['POLIGONO_ANA'].unique()
                            
                            # Criar um único FeatureCollection para todos os polígonos (mais eficiente)
                            features = []
                            poligonos_validos = 0
                            poligonos_invalidos = 0
                            
                            for poligono_wkt in poligonos_unicos:
                                try:
                                    # Verificar se o polígono está completo (termina com ))
                                    if not str(poligono_wkt).endswith('))'):
                                        poligonos_invalidos += 1
                                        continue
                                    
                                    # Converter WKT para geometria Shapely
                                    geom = wkt.loads(poligono_wkt)
                                    
                                    # Simplificar geometria agressivamente para melhor performance
                                    geom_simplified = geom.simplify(0.002, preserve_topology=True)
                                    
                                    # Criar feature GeoJSON
                                    feature = {
                                        "type": "Feature",
                                        "geometry": geom_simplified.__geo_interface__,
                                        "properties": {"tipo": "Polígono ANA"}
                                    }
                                    features.append(feature)
                                    poligonos_validos += 1
                                except Exception:
                                    # Ignorar polígonos com erro de parsing
                                    poligonos_invalidos += 1
                                    continue
                            
                            # Adicionar todos os polígonos de uma vez como FeatureCollection
                            if features:
                                feature_collection = {
                                    "type": "FeatureCollection",
                                    "features": features
                                }
                                
                                folium.GeoJson(
                                    feature_collection,
                                    style_function=lambda x: {
                                        'fillColor': '#4A90E2',
                                        'color': '#2E5C8A',
                                        'weight': 1,
                                        'fillOpacity': 0.45,
                                        'interactive': False
                                    }
                                ).add_to(grupo_poligonos)
                            
                    # Adicionar grupo de polígonos ao mapa
                    grupo_poligonos.add_to(mapa)
                    
                    # Adicionar pontos das barragens ao grupo
                    with st.spinner('Carregando pontos das barragens...'):
                            # Processar todos os pontos de uma vez (mais eficiente)
                            for idx, row in df_mapa.iterrows():
                                # Definir cor baseada na situação do cadastro SNISB
                                situacao_cadastro = str(row.get('SITUACAO_CADASTRO_SNISB', '')).lower()
                                situacao_comparacao = str(row.get('SITUACAO_COMPARACAO_SIOUT', '')).lower()
                                
                                # Hierarquia de cores:
                                if 'descartado' in situacao_cadastro:
                                    cor = '#DC143C'
                                elif 'totalmente compatível' in situacao_comparacao:
                                    cor = '#28A745'
                                elif 'compatível parcialmente' in situacao_comparacao:
                                    cor = '#FFC107'
                                elif 'compatível apenas geograficamente' in situacao_comparacao:
                                    cor = '#FF8C00'
                                elif 'incompatível' in situacao_comparacao:
                                    cor = '#8B0000'
                                elif 'selecionado para validação' in situacao_cadastro:
                                    cor = '#007BFF'
                                else:
                                    cor = '#808080'
                                
                                # Criar conteúdo do popup (simplificado)
                                popup_html = f"""<div style='font-family: Arial; font-size: 11px; min-width: 200px;'>
                                    <b>Código:</b> {row.get('CODIGO_SNISB', 'N/A')}<br>
                                    <b>Cadastro SNISB:</b> {row.get('SITUACAO_CADASTRO_SNISB', 'N/A')}<br>
                                    <b>Massa D'água:</b> {row.get('SITUACAO_MASSA_DAGUA', 'N/A')}<br>
                                    <b>Comparação SIOUT:</b> {row.get('SITUACAO_COMPARACAO_SIOUT', 'N/A')}
                                </div>"""
                                
                                folium.CircleMarker(
                                    location=[row['latitude'], row['longitude']],
                                    radius=5,
                                    color='#FFFFFF',
                                    fill=True,
                                    fillColor=cor,
                                    fillOpacity=0.7,
                                    weight=1,
                                    popup=folium.Popup(popup_html, max_width=250, lazy=True)
                                ).add_to(grupo_pontos)
                    
                    # Adicionar grupo de pontos ao mapa
                    grupo_pontos.add_to(mapa)
                    
                    # Adicionar controle de camadas (permite ligar/desligar sem recarregar)
                    folium.LayerControl(position='topright', collapsed=False).add_to(mapa)
                    
                    # Adicionar CSS customizado para deixar o controle de camadas mais transparente
                    custom_css = """
                    <style>
                    .leaflet-control-layers {
                        background-color: rgba(255, 255, 255, 0.85) !important;
                        border: 1px solid grey !important;
                        border-radius: 5px !important;
                    }
                    .leaflet-control-layers-expanded {
                        padding: 6px 8px 6px 6px !important;
                    }
                    </style>
                    """
                    mapa.get_root().html.add_child(folium.Element(custom_css))
                    
                    # Adicionar legenda
                    legenda_html = """
                    <div style="position: fixed; 
                                bottom: 30px; right: 30px; width: 200px; 
                                background-color: rgba(255, 255, 255, 0.9); z-index:9999; 
                                border:1px solid grey; border-radius: 5px;
                                padding: 8px; font-size: 10px;
                                font-family: Arial;">
                        <h4 style="margin: 0 0 6px 0; text-align: center; font-size: 11px;">Legenda</h4>
                        <p style="margin: 3px 0;"><span style="background-color: #28A745; width: 12px; height: 12px; display: inline-block; border-radius: 50%; border: 1px solid white;"></span> Totalmente Compatível</p>
                        <p style="margin: 3px 0;"><span style="background-color: #FFC107; width: 12px; height: 12px; display: inline-block; border-radius: 50%; border: 1px solid white;"></span> Parcialmente Compatível</p>
                        <p style="margin: 3px 0;"><span style="background-color: #FF8C00; width: 12px; height: 12px; display: inline-block; border-radius: 50%; border: 1px solid white;"></span> Compatível Geo</p>
                        <p style="margin: 3px 0;"><span style="background-color: #8B0000; width: 12px; height: 12px; display: inline-block; border-radius: 50%; border: 1px solid white;"></span> Incompatível</p>
                        <p style="margin: 3px 0;"><span style="background-color: #DC143C; width: 12px; height: 12px; display: inline-block; border-radius: 50%; border: 1px solid white;"></span> Descartado</p>
                        <hr style="margin: 6px 0; border: 0; border-top: 1px solid #ccc;">
                        <p style="margin: 3px 0;"><span style="background-color: #4A90E2; width: 12px; height: 12px; display: inline-block; border: 1px solid #2E5C8A;"></span> Polígonos ANA</p>
                    </div>
                    """
                    mapa.get_root().html.add_child(folium.Element(legenda_html))
                    
                    # Remover spinner e exibir mapa
                    loading_placeholder.empty()
                    st_folium(mapa, width=None, height=650, returned_objects=[])
                else:
                    st.info("Nenhuma coordenada válida encontrada nos dados filtrados.")
            else:
                st.info("Colunas LATITUDE e LONGITUDE não encontradas no dataset.")
        else:
            st.warning("Nenhum registro encontrado com os filtros selecionados.")
    
    with tab2:
        st.markdown("<h3 style='text-align: center;'>Ajuda e Glossário</h3>", unsafe_allow_html=True)
        st.markdown("")
        
        # Criar expanders para cada seção
        with st.expander("Critérios de Elegibilidade", expanded=True):
            st.markdown("""
            ### Cadastros Elegíveis para Análise
            
            Os registros considerados válidos para análise devem atender aos seguintes critérios:
            
            **Tipo de Estrutura:**
            - Apenas Barragem
            - Apenas Açude
            
            **Classificação do Cadastro:**
            - Registros com classificação "Cadastro" devem possuir número de autorização/outorga válido
            - Demais classificações diferentes de "Cadastro" são aceitas
            
            **Finalidades de Uso:**
            - São excluídas estruturas destinadas exclusivamente a:
              - Mineração
              - Aproveitamento hidrelétrico
              - Aquicultura/Piscicultura
            - Demais finalidades de uso são consideradas elegíveis
            """)
        
        with st.expander("Colunas do Dataset"):
            st.markdown("""
            ### Descrição das Colunas
            
            **CODIGO_SNISB**: Código único de identificação da barragem no Sistema Nacional de Informações sobre Segurança de Barragens.
            
            **DATA_DO_CADASTRO**: Data em que o registro foi cadastrado no sistema SNISB.
            
            **CODIGO_BARRAGEM_ENTIDADE**: Código da barragem na entidade fiscalizadora.
            
            **CODIGO_SIOUT**: Código da barragem no Sistema de Outorgas (SIOUT-RS).
            
            **AUTORIZACAO_NUM**: Número da autorização/portaria concedida para a barragem no SNISB.
            
            **AUTORIZACAO_SIOUT**: Número da autorização/portaria no Sistema de Outorgas (SIOUT-RS).
            
            **USO_SNISB**: Finalidade de uso da água/barragem registrada no SNISB (Irrigação, Dessedentação Animal, Industrial, Abastecimento Humano, etc).
            
            **USO_SIOUT**: Finalidade de uso da água/barragem registrada no SIOUT-RS.
            
            **EMPREENDEDOR_SNISB**: Nome do responsável/proprietário da barragem conforme cadastro no SNISB.
            
            **EMPREENDEDOR_SIOUT**: Nome do responsável/proprietário da barragem conforme cadastro no SIOUT-RS.
            
            **SITUACAO_CADASTRO_SNISB**: Status do registro após aplicação dos filtros de elegibilidade (Selecionado, Descartado por duplicidade, Descartado por hierarquia).
            
            **SITUACAO_COMPARACAO_SIOUT**: Resultado da comparação entre os dados SNISB e SIOUT (Totalmente compatível, Compatível parcialmente, Compatível apenas geograficamente, Incompatível).
            
            **SITUACAO_MASSA_DAGUA**: Indica se a barragem está localizada dentro de uma massa d'água mapeada pela ANA (Compatível com polígono ANA, Não aplicado).
            
            **GID**: Identificador geográfico único do registro.
            
            **ALTURA_MAX_FUNDACAO**: Altura máxima da barragem medida desde a fundação (em metros).
            
            **ALTURA_MAX_NIVEL_TERRENO**: Altura máxima da barragem medida desde o nível do terreno (em metros).
            
            **CAPACIDADE_TOTAL**: Capacidade total de armazenamento da barragem (em metros cúbicos - m³).
            
            **COROAMENTO**: Largura da crista/topo da barragem (em metros).
            
            **TIPO_DE_MATERIAL**: Material utilizado na construção da barragem (Terra, Concreto, CCR, etc).
            
            **LATITUDE / LONGITUDE**: Coordenadas geográficas da localização da barragem (sistema SIRGAS 2000).
            
            **ID_SIOUT**: Identificador único do registro no Sistema de Outorgas (SIOUT-RS).
            
            **POLIGONO_ANA**: Geometria do polígono da massa d'água da ANA em formato WKT (Well-Known Text) onde a barragem está localizada.
            """)
        
        with st.expander("Situações e Status"):
            st.markdown("""
            ### SITUACAO_CADASTRO_SNISB
            
            - **Selecionado para validação**: Registro passou pelos filtros e está apto para análise.
            - **Descartado por duplicidade**: Registro identificado como duplicado completo (100% igual).
            - **Descartado por hierarquia**: Registro descartado por regras de priorização (data mais recente, código SIOUT, etc).
            
            ### SITUACAO_MASSA_DAGUA
            
            - **Compatível com polígono ANA**: A barragem está localizada dentro de uma massa d'água mapeada pela ANA (Agência Nacional de Águas).
            - **Não aplicado**: Situação não analisada (geralmente para registros descartados).
            
            ### SITUACAO_COMPARACAO_SIOUT
            
            - **Totalmente compatível**: Todos os campos comparados (empreendedor, uso, código, autorização) são idênticos entre SNISB e SIOUT.
            - **Compatível parcialmente**: Alguns campos são compatíveis, mas outros diferem entre SNISB e SIOUT.
            - **Compatível apenas geograficamente**: As coordenadas estão próximas (mesmo polígono ANA), mas os demais dados divergem.
            - **Incompatível**: Não há correspondência entre os registros SNISB e SIOUT.
            - **Não aplicado**: Comparação não realizada (registros descartados anteriormente).
            """)
        
        with st.expander("Código de Cores"):
            st.markdown("""
            ### Legenda de Cores da Tabela
            
            As células coloridas facilitam a identificação rápida dos status:
            
            - **Verde**: Situações positivas (totalmente compatível, selecionado, compatível com polígono)
            - **Amarelo**: Situações intermediárias (parcialmente compatível, apenas geograficamente)
            - **Vermelho**: Situações negativas (incompatível, descartado)
            - **Sem cor**: Não aplicado ou sem informação
            """)
        
        with st.expander("Filtros Disponíveis"):
            st.markdown("""
            ### Tipos de Filtros
            
            **Filtro de Data (Período de Cadastro)**
            - Selecione datas inicial e final usando calendários
            - Filtra barragens cadastradas dentro do período escolhido
            - Útil para análises temporais e acompanhamento de cadastros
            
            **Filtros de Características Físicas**
            - **Situação Cadastro SNISB**: Status do registro (Selecionado, Descartado por duplicidade, etc)
            - **Situação Massa D'água**: Compatibilidade com polígonos ANA
            - **Situação Comparação SIOUT**: Nível de compatibilidade entre SNISB e SIOUT
            - **Código SNISB**: Busca específica por código da barragem (com autocompletar)
            
            **Filtros de Uso e Empreendedor**
            - **Finalidade de Uso (SNISB)**: Tipo de uso da água (Irrigação, Dessedentação Animal, Industrial, Abastecimento Humano, etc)
            - **Tipo de Material**: Material de construção da barragem (Terra, Concreto, CCR, Sem Informação)
            - **Empreendedor**: Proprietário ou responsável pela barragem (com busca)
            
            **Dica**: Combine múltiplos filtros para análises específicas. Todos os filtros funcionam em conjunto.
            """)
        
        with st.expander("Dicas de Uso"):
            st.markdown("""
            ### Como usar o sistema
            
            **1. Filtros de Data**
            - Clique nos campos de data para abrir o calendário
            - Escolha o período desejado (data inicial e final)
            - Os dados são filtrados automaticamente
            
            **2. Filtros por Categoria**
            - Use os dropdowns para selecionar valores específicos
            - O filtro de Código SNISB permite busca com autocompletar
            - Selecione "Todos" para desativar um filtro
            
            **3. Visualização dos Dados**
            - A tabela mostra 50 registros por página
            - Use os botões numerados para navegar entre páginas
            - As cores indicam status (verde=bom, amarelo=intermediário, vermelho=problema)
            
            **4. Mapa Interativo**
            - Localizado no final da página
            - Mostra todas as barragens e polígonos ANA dos dados filtrados
            - Use o controle de camadas (canto superior direito) para exibir/ocultar pontos e polígonos
            - Zoom e navegação disponíveis (arraste, scroll, botões +/-)
            - Clique nos pontos para ver informações detalhadas
            - Imagem de satélite Esri como base do mapa
            
            **5. Download de Dados**
            - Clique no botão "Baixar Dados" (centralizado)
            - Escolha o formato: Excel (.xlsx), CSV (.csv) ou JSON (.json)
            - O arquivo contém apenas os dados filtrados
            
            **6. Filtro por Código SNISB**
            - Digite ou selecione um código específico
            - Sistema autocompleta enquanto você digita
            - Útil para localizar barragens específicas rapidamente
            """)
        
        with st.expander("Perguntas Frequentes"):
            st.markdown("""
            ### FAQ
            
            **P: Por que alguns registros foram descartados?**
            R: Para evitar duplicidade, aplicamos filtros que mantêm apenas o registro mais recente e completo quando há múltiplas entradas para a mesma barragem.
            
            **P: O que significa "compatível apenas geograficamente"?**
            R: Significa que a barragem está na mesma localização (polígono ANA), mas os dados cadastrais (nome, código, etc) não conferem entre SNISB e SIOUT.
            
            **P: Como interpretar registros com "Não aplicado"?**
            R: Esses registros foram descartados em etapas anteriores da análise, portanto não passaram pelas validações posteriores.
            
            **P: Posso confiar nos dados "totalmente compatíveis"?**
            R: Sim, esses registros têm correspondência perfeita entre SNISB e SIOUT em todos os campos analisados.
            
            **P: Como funcionam os filtros de altura e capacidade?**
            R: São faixas pré-definidas que classificam as barragens por porte. Altura em metros e capacidade em metros cúbicos (m³).
            
            **P: O mapa mostra todas as barragens?**
            R: Não, o mapa mostra apenas as barragens que atendem aos filtros aplicados. Se não houver filtros, mostra todas.
            
            **P: Por que o mapa não aparece?**
            R: Pode ser porque os registros filtrados não têm coordenadas válidas de latitude/longitude.
            
            **P: Como uso múltiplos filtros ao mesmo tempo?**
            R: Simplesmente selecione valores em vários filtros. O sistema aplica todos simultaneamente (lógica AND - deve atender todos).
            
            **P: O download inclui dados de todas as páginas?**
            R: Sim! O download exporta TODOS os registros filtrados, não apenas a página atual da tabela.
            
            **P: Posso voltar para o dataset completo depois de filtrar?**
            R: Sim, selecione "Todos" em cada filtro ou recarregue a página (F5).
            """)

else:
    st.error("Não foi possível carregar os dados. Verifique se o arquivo 'RELATORIO_FINAL_SNISB_SIOUT.csv' ou 'RELATORIO_FINAL_SNISB_SIOUT.xlsx' está na pasta correta.")

# Rodapé com logo Zetta
st.markdown("")

# Carregar logo em base64
import base64
logo_path = os.path.join(os.path.dirname(__file__), "image", "app", "LogoZetta.png")
if os.path.exists(logo_path):
    with open(logo_path, "rb") as f:
        img_data = base64.b64encode(f.read()).decode()
    
    # Rodapé centralizado com logo clicável
    st.markdown(
        f"""
        <div style="text-align: center; padding: 10px 0 5px 0;">
            <p style="margin: 0 0 5px 0; color: #666; font-size: 12px;">Desenvolvido por</p>
            <a href="https://agenciazetta.ufla.br/" target="_blank">
                <img src="data:image/png;base64,{img_data}" 
                     style="width: 100px; background: transparent; cursor: pointer;" 
                     alt="Agência Zetta">
            </a>
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    st.markdown("<p style='text-align: center; color: #666; font-size: 12px;'>Desenvolvido por Agência Zetta</p>", unsafe_allow_html=True)
