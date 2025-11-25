"""
Script para adicionar coluna POINT ao arquivo Excel existente
Busca dados do banco PostgreSQL e cria coluna ponto_geo no Excel
"""

import pandas as pd
import os
from consulta_banco import buscar_barragens_com_geometria

def adicionar_coluna_point_no_excel():
    """
    Busca dados do banco e adiciona coluna ponto_geo no arquivo Excel
    """
    # Buscar dados do banco com coluna POINT
    print("🔄 Buscando dados do banco PostgreSQL...")
    df_banco = buscar_barragens_com_geometria()
    
    if df_banco is None:
        print("❌ Erro ao buscar dados do banco")
        return
    
    print(f"✅ {len(df_banco)} registros obtidos do banco")
    
    # Carregar arquivo Excel existente
    arquivo_excel = "REGISTROS_SNISB_EM_POLIGONOS_ANA_RS.xlsx"
    
    if not os.path.exists(arquivo_excel):
        print(f"❌ Arquivo {arquivo_excel} não encontrado!")
        return
    
    print(f"📂 Carregando {arquivo_excel}...")
    df_excel = pd.read_excel(arquivo_excel)
    print(f"✅ {len(df_excel)} registros no Excel")
    
    # Criar coluna ponto_geo formatada como texto WKT
    if 'LATITUDE' in df_excel.columns and 'LONGITUDE' in df_excel.columns:
        df_excel['PONTO_GEO'] = df_excel.apply(
            lambda row: f"POINT({row['LONGITUDE']} {row['LATITUDE']})" 
            if pd.notna(row['LATITUDE']) and pd.notna(row['LONGITUDE']) 
            else None,
            axis=1
        )
        print("✅ Coluna PONTO_GEO criada com formato WKT")
    else:
        print("⚠️ Colunas LATITUDE/LONGITUDE não encontradas no Excel")
        return
    
    # Salvar arquivo atualizado
    print(f"💾 Salvando arquivo atualizado...")
    df_excel.to_excel(arquivo_excel, index=False, engine='openpyxl')
    print(f"✅ Arquivo {arquivo_excel} atualizado com coluna PONTO_GEO")
    print(f"📊 Total de colunas: {len(df_excel.columns)}")
    print(f"📋 Novas colunas: {df_excel.columns.tolist()}")


if __name__ == "__main__":
    adicionar_coluna_point_no_excel()
