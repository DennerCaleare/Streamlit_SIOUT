# 🌊 Ferramenta de Comparação de Registros - SNISB vs SIOUT-RS

Aplicação web desenvolvida em Streamlit para análise e visualização integrada de dados de barragens do SNISB (Sistema Nacional de Informações sobre Segurança de Barragens) e SIOUT-RS (Sistema de Outorgas de Água do Rio Grande do Sul).

## 📋 Sobre o Sistema

Este dashboard realiza o cruzamento e comparação de dados entre:

- **SNISB**: Base nacional de barragens gerenciada pela ANA (Agência Nacional de Águas)
- **SIOUT-RS**: Sistema estadual de outorgas de recursos hídricos do Rio Grande do Sul
- **Polígonos ANA**: Massas d'água mapeadas pela ANA

O objetivo é identificar barragens cadastradas no SNISB que possuem (ou deveriam possuir) autorização estadual de uso de recursos hídricos, analisando compatibilidade geográfica e cadastral.

## 🚀 Como Executar

### Localmente

1. Clone o repositório:
```bash
git clone https://github.com/DennerCaleare/Streamlit_SIOUT.git
cd Streamlit_SIOUT
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Execute o aplicativo:
```bash
streamlit run app.py
```

4. O aplicativo abrirá automaticamente no navegador em `http://localhost:8501`

### Deploy na Nuvem

O aplicativo está disponível online através do Streamlit Cloud.

## 📁 Estrutura de Arquivos

```
Streamlit_SIOUT/
├── app.py                              # Aplicação principal
├── RELATORIO_FINAL_SNISB_SIOUT.csv     # Dataset principal (preferencial)
├── RELATORIO_FINAL_SNISB_SIOUT.xlsx    # Dataset alternativo (fallback)
├── requirements.txt                     # Dependências Python
├── image/
│   └── app/
│       ├── Logo.png                    # Favicon da aplicação
│       └── LogoZetta.png               # Logo da Agência Zetta
└── README.md                           # Este arquivo
```

## ✨ Funcionalidades

### 📊 Visualização de Dados

- **Tabela paginada** com 50 registros por página e navegação inteligente
- **Código de cores** automático por status de compatibilidade
- **Contador dinâmico** de registros filtrados vs. total
- **Exportação em múltiplos formatos**: Excel (.xlsx), CSV (.csv), JSON (.json)
- **Formatação responsiva** que se adapta ao tamanho da tela

### 🔍 Filtros Avançados

**Filtros de Data:**
- **Período de cadastro**: Seleção de data inicial e final com calendário

**Filtros de Características Físicas:**
- **Situação Cadastro SNISB**: Status do registro (Selecionado, Descartado)
- **Situação Massa D'água**: Compatibilidade com polígonos ANA
- **Situação Comparação SIOUT**: Níveis de compatibilidade entre sistemas
- **Código SNISB**: Busca específica com autocompletar

**Filtros de Uso e Empreendedor:**
- **Finalidade de Uso (SNISB)**: Irrigação, Dessedentação Animal, Industrial, etc.
- **Tipo de Material**: Terra, Concreto, CCR
- **Empreendedor**: Busca por proprietário/responsável

*Todos os filtros funcionam em conjunto (lógica AND)*

### 🗺️ Mapa Interativo

- **Visualização geoespacial** com imagem de satélite Esri em alta resolução
- **Controle de camadas** interativo sem recarregamento da página:
  - 🗺️ Polígonos ANA (massas d'água)
  - 🔵 Pontos das Barragens
- **Marcadores coloridos** por hierarquia de status:
  - 🟢 Verde: Totalmente compatível
  - 🟡 Amarelo: Parcialmente compatível
  - 🟠 Laranja: Compatível geograficamente
  - 🔴 Vermelho: Incompatível/Descartado
  - 🔵 Azul: Selecionado para validação
- **Popups informativos** ao clicar nos pontos com dados detalhados
- **Polígonos ANA** com 45% de opacidade e otimização de geometria
- **Legenda fixa** no canto inferior direito
- **Spinner de carregamento** durante processamento
- **Zoom e navegação** fluida preservando posição

### 📖 Ajuda e Glossário Completo

- **Critérios de Elegibilidade**: Regras de seleção e validação de cadastros
- **Descrição das Colunas**: Detalhamento completo de todas as 23 colunas
- **Situações e Status**: Significado de cada classificação (SNISB, Massa D'água, Comparação SIOUT)
- **Código de Cores**: Legenda completa da tabela
- **Filtros Disponíveis**: Explicação de cada tipo de filtro
- **Dicas de Uso**: Guia passo a passo de como usar o sistema
- **FAQ**: Perguntas frequentes com respostas detalhadas

## 🛠️ Tecnologias Utilizadas

- **Streamlit 1.32+**: Framework para aplicações web em Python
- **Pandas 2.0+**: Manipulação e análise de dados
- **Folium 0.14+**: Mapas interativos com Leaflet.js
- **streamlit-folium 0.15+**: Integração Folium + Streamlit
- **Shapely 2.0+**: Manipulação de geometrias espaciais
- **Geopandas 0.14+**: Análise de dados geoespaciais
- **OpenPyXL**: Leitura de arquivos Excel
- **Python 3.11+**: Linguagem de programação

## 📊 Dados

- **Total de registros**: 10.129 barragens
- **Registros com polígonos ANA**: 9.642 (95,2%)
- **Polígonos ANA únicos**: ~4.214 massas d'água
- **Colunas**: 23 campos incluindo:
  - Dados cadastrais (códigos, datas, autorizações)
  - Dados técnicos (altura, capacidade, material)
  - Dados espaciais (latitude, longitude, polígonos WKT)
  - Dados de comparação (situações e compatibilidades)
- **Sistema de coordenadas**: SIRGAS 2000 (EPSG:4674)
- **Formato preferencial**: CSV (sem limite de caracteres)
- **Formato alternativo**: Excel (polígonos complexos podem ser truncados)

## 🎨 Hierarquia de Cores

| Cor | Status | Significado |
|-----|--------|-------------|
| 🟢 Verde | Totalmente Compatível | Todos os campos conferem entre SNISB e SIOUT |
| 🟡 Amarelo | Parcialmente Compatível | Alguns campos diferem |
| 🟠 Laranja | Compatível Geograficamente | Mesma localização, dados divergentes |
| 🔴 Vermelho Escuro | Incompatível | Sem correspondência entre sistemas |
| 🔴 Vermelho | Descartado | Eliminado por duplicidade ou hierarquia |
| 🔵 Azul | Selecionado | Aprovado para validação |

## 💡 Observações Técnicas

- ✅ Validação automática de coordenadas dentro do território brasileiro
- ✅ Sistema de paginação inteligente com reticências
- ✅ Filtros combinados com lógica AND (todos devem ser atendidos)
- ✅ Multiselect com lógica OR dentro de cada filtro
- ✅ Cache de dados para performance otimizada
- ✅ Detecção e tratamento de polígonos truncados pelo Excel (32.767 caracteres)
- ✅ Geometrias simplificadas automaticamente para melhor renderização
- ✅ Controle de camadas do mapa sem recarregamento (JavaScript puro)

## 🏢 Desenvolvido por

**Agência Zetta - UFLA**

[https://agenciazetta.ufla.br/](https://agenciazetta.ufla.br/)

Agência de inovação, empreendedorismo e transferência de tecnologia da Universidade Federal de Lavras.

## 📝 Licença

Este projeto foi desenvolvido para uso institucional e análise de dados públicos de recursos hídricos.
