# Dashboard SIOUT-RS - Análise de Barragens

Aplicação Streamlit para análise e visualização integrada de dados de barragens do SNISB (Sistema Nacional de Informações sobre Segurança de Barragens) e SIOUT (Sistema de Outorgas de Água do Rio Grande do Sul).

## Sobre o Sistema

Este dashboard realiza o cruzamento de dados entre:

- **SNISB**: Base nacional de barragens gerenciada pela ANA
- **SIOUT-RS**: Sistema estadual de outorgas de recursos hídricos do Rio Grande do Sul

O objetivo é identificar barragens cadastradas nacionalmente que possuem (ou deveriam possuir) autorização estadual de uso de recursos hídricos.

## Como executar

1. Instale as dependências:

```bash
pip install -r requirements.txt
```

2. Execute o aplicativo:

```bash
streamlit run app.py
```

3. O aplicativo abrirá automaticamente no navegador em `http://localhost:8501`

## Estrutura de Arquivos

- `app.py` - Aplicação principal do dashboard
- `adicionar_coluna_point.py` - Script para adicionar geometria POINT ao dataset
- `REGISTROS_SNISB_EM_POLIGONOS_ANA_RS.xlsx` - Base de dados com 4.698 registros
- `requirements.txt` - Dependências do projeto
- `.env` - Credenciais do banco de dados (não versionado)
- `.gitignore` - Arquivos ignorados pelo Git

## Funcionalidades

### Visualização de Dados

- Tabela paginada com 50 registros por página
- Código de cores por status de compatibilidade
- Contador de registros filtrados
- Exportação em múltiplos formatos (Excel, CSV, JSON)

### Filtros Avançados

- **Período de cadastro**: Filtro por data inicial e final
- **Situação Cadastro SNISB**: Seleção múltipla de status
- **Situação Massa D'água**: Compatibilidade com polígonos ANA
- **Situação Comparação SIOUT**: Níveis de compatibilidade
- **Código SNISB**: Busca por múltiplos códigos

### Mapa Interativo

- **Visualização geoespacial** com imagem de satélite Esri
- **Marcadores coloridos** por status de compatibilidade
- **Popups informativos** ao clicar nos pontos
- **Legenda** com hierarquia de cores
- **Zoom e navegação** fluida (sem reload)

### Ajuda e Glossário

- **Critérios de Elegibilidade**: Regras de seleção de cadastros
- **Descrição das Colunas**: Detalhamento de todos os campos
- **Situações e Status**: Significado de cada classificação
- **Código de Cores**: Legenda da tabela
- **FAQ**: Perguntas frequentes

## Tecnologias Utilizadas

- **Streamlit**: Framework para aplicações web
- **Pandas**: Manipulação de dados
- **Folium**: Mapas interativos
- **streamlit-folium**: Integração Folium + Streamlit
- **OpenPyXL**: Leitura de arquivos Excel
- **Python-dotenv**: Gerenciamento de variáveis de ambiente

## Dados

- **Total de registros**: 4.698 barragens
- **Colunas**: 18 campos incluindo geometria POINT
- **Sistema de coordenadas**: SIRGAS 2000 (SRID 4674)
- **Fonte**: Cruzamento SNISB + SIOUT + Polígonos ANA

## Código de Cores

- **Verde**: Totalmente compatível / Selecionado
- **Amarelo**: Compatível parcialmente
- **Laranja**: Compatível apenas geograficamente
- **Vermelho escuro**: Incompatível
- **Vermelho**: Descartado

## Observações

- Validação automática de coordenadas dentro do território brasileiro
- Sistema de paginação com navegação inteligente
- Filtros combinados com lógica AND (todos devem ser atendidos)
- Multiselect com lógica OR dentro de cada filtro
