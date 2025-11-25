import streamlit as st
import pandas as pd
import os
import folium
from streamlit_folium import st_folium

# Configuração da página
st.set_page_config(
    page_title="SIOUT-RS - Análise de Dados",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Título principal
st.markdown("<h1 style='text-align: center;'>Sistema de Outorgas de Água - Rio Grande do Sul</h1>", unsafe_allow_html=True)
st.markdown("---")

# Função para carregar os dados com cache
@st.cache_data
def carregar_dados():
    """Carrega o arquivo Excel e retorna um DataFrame"""
    try:
        arquivo_path = os.path.join(os.path.dirname(__file__), "REGISTROS_SNISB_EM_POLIGONOS_ANA_RS.xlsx")
        return pd.read_excel(arquivo_path)
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
        if 'DATA DO CADASTRO' in df.columns:
            df['DATA DO CADASTRO'] = pd.to_datetime(df['DATA DO CADASTRO'], errors='coerce')
            data_min = df['DATA DO CADASTRO'].min()
            data_max = df['DATA DO CADASTRO'].max()
            
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
                opcoes_cadastro = ['Todos'] + sorted(df['SITUACAO_CADASTRO_SNISB'].dropna().unique().tolist())
                filtro_cadastro = st.selectbox(
                    "Situação Cadastro SNISB",
                    opcoes_cadastro,
                    index=0,
                    label_visibility="collapsed"
                )
            else:
                filtro_cadastro = 'Todos'
        
        with col_fis2:
            st.markdown("<p style='text-align: center; margin-bottom: 0;'><small>Situação Massa D'água</small></p>", unsafe_allow_html=True)
            if 'SITUACAO_MASSA_DAGUA' in df.columns:
                opcoes_massa = ['Todos'] + sorted(df['SITUACAO_MASSA_DAGUA'].dropna().unique().tolist())
                filtro_massa = st.selectbox(
                    "Situação Massa D'água",
                    opcoes_massa,
                    index=0,
                    label_visibility="collapsed"
                )
            else:
                filtro_massa = 'Todos'
        
        with col_fis3:
            st.markdown("<p style='text-align: center; margin-bottom: 0;'><small>Situação Comparação SIOUT</small></p>", unsafe_allow_html=True)
            if 'SITUACAO_COMPARACAO_SIOUT' in df.columns:
                opcoes_comparacao = ['Todos'] + sorted(df['SITUACAO_COMPARACAO_SIOUT'].dropna().unique().tolist())
                filtro_comparacao = st.selectbox(
                    "Situação Comparação SIOUT",
                    opcoes_comparacao,
                    index=0,
                    label_visibility="collapsed"
                )
            else:
                filtro_comparacao = 'Todos'
        
        with col_fis4:
            st.markdown("<p style='text-align: center; margin-bottom: 0;'><small>Código SNISB</small></p>", unsafe_allow_html=True)
            if 'CÓDIGO SNISB' in df.columns:
                # Obter lista de códigos únicos
                codigos_unicos = sorted(df['CÓDIGO SNISB'].dropna().astype(str).unique().tolist())
                
                # Campo de busca com autocompletar
                filtro_codigo = st.selectbox(
                    "Código SNISB",
                    ['Todos'] + codigos_unicos,
                    index=0,
                    label_visibility="collapsed",
                    key="filtro_codigo_snisb"
                )
            else:
                filtro_codigo = 'Todos'
        
        # Aplicar os filtros
        df_filtrado = df.copy()
        
        # Verificar se algum filtro está ativo
        filtros_ativos = []
        
        # Filtro de data
        if 'DATA DO CADASTRO' in df.columns:
            data_inicio_dt = pd.to_datetime(data_inicio)
            data_fim_dt = pd.to_datetime(data_fim)
            
            # Verificar se o filtro de data está ativo (diferente do range completo)
            if data_inicio_dt > data_min or data_fim_dt < data_max:
                df_filtrado = df_filtrado[
                    (df_filtrado['DATA DO CADASTRO'] >= data_inicio_dt) & 
                    (df_filtrado['DATA DO CADASTRO'] <= data_fim_dt)
                ]
                filtros_ativos.append('DATA DO CADASTRO')
        
        # Filtro de Código SNISB
        if filtro_codigo != 'Todos':
            if 'CÓDIGO SNISB' in df_filtrado.columns:
                df_filtrado = df_filtrado[df_filtrado['CÓDIGO SNISB'].astype(str) == filtro_codigo]
                filtros_ativos.append('CÓDIGO SNISB')
        
        if filtro_cadastro != 'Todos':
            df_filtrado = df_filtrado[df_filtrado['SITUACAO_CADASTRO_SNISB'] == filtro_cadastro]
            filtros_ativos.append('SITUACAO_CADASTRO_SNISB')
        
        if filtro_massa != 'Todos':
            df_filtrado = df_filtrado[df_filtrado['SITUACAO_MASSA_DAGUA'] == filtro_massa]
            filtros_ativos.append('SITUACAO_MASSA_DAGUA')
        
        if filtro_comparacao != 'Todos':
            df_filtrado = df_filtrado[df_filtrado['SITUACAO_COMPARACAO_SIOUT'] == filtro_comparacao]
            filtros_ativos.append('SITUACAO_COMPARACAO_SIOUT')
        
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
                styled_df = df_pagina.style.applymap(colorir_situacao, subset=colunas_estilo)
                st.dataframe(styled_df, use_container_width=True, height=600, column_config={
                    col: st.column_config.TextColumn(width="medium") for col in df_pagina.columns
                })
            else:
                st.dataframe(df_pagina, use_container_width=True, height=600, column_config={
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
            
            # Verificar se existe coluna PONTO_GEO
            col_ponto = None
            for col in df_filtrado.columns:
                if 'PONTO_GEO' in col.upper():
                    col_ponto = col
                    break
            
            if col_ponto:
                # Preparar dados do mapa extraindo coordenadas de PONTO_GEO
                # Manter todas as colunas necessárias para o popup
                colunas_mapa = [col_ponto]
                colunas_popup = ['CÓDIGO SNISB', 'SITUACAO_CADASTRO_SNISB', 'SITUACAO_MASSA_DAGUA', 'SITUACAO_COMPARACAO_SIOUT']
                for col in colunas_popup:
                    if col in df_filtrado.columns:
                        colunas_mapa.append(col)
                
                df_mapa = df_filtrado[colunas_mapa].copy()
                df_mapa = df_mapa.dropna(subset=[col_ponto])
                
                # Extrair latitude e longitude do formato POINT(lon lat)
                def extrair_coordenadas(ponto_wkt):
                    """Extrai lat/lon de string POINT(longitude latitude)"""
                    try:
                        if pd.isna(ponto_wkt):
                            return None, None
                        # Remove "POINT(" e ")" e separa as coordenadas
                        coords = str(ponto_wkt).replace('POINT(', '').replace(')', '').split()
                        if len(coords) == 2:
                            lon = float(coords[0])
                            lat = float(coords[1])
                            return lat, lon
                        return None, None
                    except:
                        return None, None
                
                # Aplicar extração
                df_mapa[['latitude', 'longitude']] = df_mapa[col_ponto].apply(
                    lambda x: pd.Series(extrair_coordenadas(x))
                )
                
                # Remover valores inválidos
                df_mapa = df_mapa.dropna(subset=['latitude', 'longitude'])
                
                # Converter para numérico
                df_mapa['latitude'] = pd.to_numeric(df_mapa['latitude'], errors='coerce')
                df_mapa['longitude'] = pd.to_numeric(df_mapa['longitude'], errors='coerce')
                df_mapa = df_mapa.dropna(subset=['latitude', 'longitude'])
                
                if len(df_mapa) > 0:
                    # Calcular centro do mapa
                    center_lat = df_mapa['latitude'].mean()
                    center_lon = df_mapa['longitude'].mean()
                    
                    # Criar mapa Folium com imagem de satélite Esri
                    mapa = folium.Map(
                        location=[center_lat, center_lon],
                        zoom_start=7,
                        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                        attr='Esri World Imagery'
                    )
                    
                    # Adicionar legenda
                    legenda_html = """
                    <div style="position: fixed; 
                                bottom: 30px; right: 30px; width: 200px; 
                                background-color: rgba(255, 255, 255, 0.85); z-index:9999; 
                                border:1px solid grey; border-radius: 5px;
                                padding: 8px; font-size: 10px;
                                font-family: Arial;">
                        <h4 style="margin: 0 0 6px 0; text-align: center; font-size: 11px;">Legenda</h4>
                        <p style="margin: 3px 0;"><span style="background-color: #28A745; width: 12px; height: 12px; display: inline-block; border-radius: 50%; border: 1px solid white;"></span> Totalmente Compatível</p>
                        <p style="margin: 3px 0;"><span style="background-color: #FFC107; width: 12px; height: 12px; display: inline-block; border-radius: 50%; border: 1px solid white;"></span> Parcialmente Compatível</p>
                        <p style="margin: 3px 0;"><span style="background-color: #FF8C00; width: 12px; height: 12px; display: inline-block; border-radius: 50%; border: 1px solid white;"></span> Compatível Geo</p>
                        <p style="margin: 3px 0;"><span style="background-color: #8B0000; width: 12px; height: 12px; display: inline-block; border-radius: 50%; border: 1px solid white;"></span> Incompatível</p>
                        <p style="margin: 3px 0;"><span style="background-color: #DC143C; width: 12px; height: 12px; display: inline-block; border-radius: 50%; border: 1px solid white;"></span> Descartado</p>
                    </div>
                    """
                    mapa.get_root().html.add_child(folium.Element(legenda_html))
                    
                    # Adicionar marcadores com popup e cores por situação
                    for idx, row in df_mapa.iterrows():
                        # Definir cor baseada na situação do cadastro SNISB
                        situacao_cadastro = str(row.get('SITUACAO_CADASTRO_SNISB', '')).lower()
                        situacao_comparacao = str(row.get('SITUACAO_COMPARACAO_SIOUT', '')).lower()
                        
                        # Hierarquia de cores:
                        # 1. Descartados (vermelho)
                        # 2. Totalmente compatível (verde)
                        # 3. Parcialmente compatível (amarelo)
                        # 4. Compatível geograficamente (laranja)
                        # 5. Incompatível (vermelho escuro)
                        # 6. Selecionado para validação (azul)
                        
                        if 'descartado' in situacao_cadastro:
                            cor = '#DC143C'  # Vermelho escuro (descartados)
                        elif 'totalmente compatível' in situacao_comparacao:
                            cor = '#28A745'  # Verde (totalmente compatível)
                        elif 'compatível parcialmente' in situacao_comparacao:
                            cor = '#FFC107'  # Amarelo (parcialmente compatível)
                        elif 'compatível apenas geograficamente' in situacao_comparacao:
                            cor = '#FF8C00'  # Laranja (só geografia)
                        elif 'incompatível' in situacao_comparacao:
                            cor = '#8B0000'  # Vermelho muito escuro (incompatível)
                        elif 'selecionado para validação' in situacao_cadastro:
                            cor = '#007BFF'  # Azul (selecionados)
                        else:
                            cor = '#808080'  # Cinza (sem classificação)
                        
                        # Criar conteúdo do popup
                        popup_html = "<div style='font-family: Arial; font-size: 12px;'>"
                        popup_html += f"<b>Código SNISB:</b> {row.get('CÓDIGO SNISB', 'N/A')}<br>"
                        popup_html += f"<b>Situação Cadastro SNISB:</b> {row.get('SITUACAO_CADASTRO_SNISB', 'N/A')}<br>"
                        popup_html += f"<b>Situação Massa D'água:</b> {row.get('SITUACAO_MASSA_DAGUA', 'N/A')}<br>"
                        popup_html += f"<b>Situação Comparação SIOUT:</b> {row.get('SITUACAO_COMPARACAO_SIOUT', 'N/A')}"
                        popup_html += "</div>"
                        
                        folium.CircleMarker(
                            location=[row['latitude'], row['longitude']],
                            radius=6,
                            color='#FFFFFF',
                            fill=True,
                            fillColor=cor,
                            fillOpacity=0.8,
                            weight=1,
                            popup=folium.Popup(popup_html, max_width=300)
                        ).add_to(mapa)
                    
                    # Exibir mapa (returned_objects desabilitado para evitar recarregamento)
                    st_folium(mapa, width=None, height=650, use_container_width=True, returned_objects=[])
                else:
                    st.info("Nenhuma coordenada válida encontrada nos dados filtrados.")
            else:
                st.info("Coluna PONTO_GEO não encontrada no dataset.")
        else:
            st.warning("Nenhum registro encontrado com os filtros selecionados.")
    
    with tab2:
        st.markdown("<h3 style='text-align: center;'>Ajuda e Glossário</h3>", unsafe_allow_html=True)
        st.markdown("")
        
        # Criar expanders para cada seção
        with st.expander("Colunas do Dataset", expanded=True):
            st.markdown("""
            ### Descrição das Colunas
            
            **CÓDIGO SNISB**: Código único de identificação da barragem no Sistema Nacional de Informações sobre Segurança de Barragens.
            
            **COD BARRAGEM NA ENT FISCAL**: Código da barragem na entidade fiscalizadora (formato: AAAA/NNN.NNN).
            
            **AUTORIZAÇÃO Nº**: Número da autorização/portaria concedida (formato: NNN.NNN/AAAA).
            
            **DATA DO CADASTRO**: Data em que o registro foi cadastrado no sistema.
            
            **ALTURA MÁXIMA FUNDAÇÃO**: Altura máxima da barragem medida desde a fundação (em metros).
            
            **ALTURA MÁXIMA NÍVEL TERRENO**: Altura máxima da barragem medida desde o nível do terreno (em metros).
            
            **CAPACIDADE TOTAL**: Capacidade total de armazenamento da barragem (em m³).
            
            **COROAMENTO**: Largura da crista/topo da barragem (em metros).
            
            **TIPO DE MATERIAL**: Material utilizado na construção da barragem (concreto, terra, enrocamento, etc).
            
            **LATITUDE / LONGITUDE**: Coordenadas geográficas da localização da barragem.
            
            **PONTO_GEO**: Geometria espacial da barragem em formato POINT(longitude latitude) - SRID 4674 (SIRGAS 2000).
            
            **ID_PROCESSO_CADASTRO_SIOUT**: Identificador do processo no Sistema de Outorgas (SIOUT).
            
            **CODIGO_PROCESSO_CADASTRO_SIOUT**: Código do processo de cadastro no SIOUT.
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
            
            **Dica**: Combine múltiplos filtros para análises específicas. Todos os filtros funcionam em conjunto.
            """)
        
        with st.expander("Dicas de Uso"):
            st.markdown("""
            ### Como usar o sistema
            x
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
            - Mostra todas as barragens dos dados filtrados
            - Zoom e navegação disponíveis
            
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
    
    # Rodapé
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: gray;'>
        <small>Arquivo: REGISTROS_SNISB_EM_POLIGONOS_ANA_RS.xlsx | Última atualização: Novembro 2025</small>
    </div>
    """, unsafe_allow_html=True)

else:
    st.error("Não foi possível carregar os dados. Verifique se o arquivo 'REGISTROS_SNISB_EM_POLIGONOS_ANA_RS.xlsx' está na pasta correta.")
