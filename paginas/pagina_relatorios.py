"""
Página Relatórios - Exportação de dados em PDF e Excel.

Esta página permite gerar e baixar relatórios das avaliações
em formatos PDF e Excel.
"""

import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime
from dados.gerenciador_clientes import buscar_cliente_por_id
from dados.gerenciador_avaliacoes import (
    obter_historico_avaliacoes,
    obter_ultima_avaliacao,
    listar_datas_avaliacoes,
    obter_avaliacao_por_data
)
from servicos.calculadora_corporal import (
    calcular_imc,
    classificar_imc,
    calcular_tmb,
    calcular_gasto_calorico_diario,
    calcular_idade
)
from servicos.analisador_perimetros import NOMES_PERIMETROS


def gerar_dataframe_avaliacao(cliente: dict, avaliacao: dict) -> pd.DataFrame:
    """
    Gera um DataFrame com os dados da avaliação para exportação.
    
    :param cliente: Dicionário com dados do cliente
    :param avaliacao: Dicionário com dados da avaliação
    :return: DataFrame formatado
    """
    peso = avaliacao.get("peso_kg", 0)
    altura = avaliacao.get("altura_cm", 0)
    genero = cliente.get("genero", "Masculino")
    data_nascimento = cliente.get("data_nascimento", "")
    idade = calcular_idade(data_nascimento) if data_nascimento else 25
    nivel = avaliacao.get("nivel_atividade", "Sedentário")
    
    imc = calcular_imc(peso, altura)
    classificacao = classificar_imc(imc)
    tmb = calcular_tmb(peso, altura, idade, genero)
    gasto = calcular_gasto_calorico_diario(tmb, nivel)
    
    # Dados gerais
    dados_gerais = {
        "Campo": ["Nome", "Gênero", "Idade", "Data Avaliação", "Peso (kg)", 
                  "Altura (cm)", "IMC", "Classificação IMC", "TMB (kcal)", 
                  "Gasto Diário (kcal)", "Nível Atividade"],
        "Valor": [cliente.get("nome", ""), genero, idade, avaliacao.get("data", ""),
                  peso, altura, imc, classificacao, round(tmb), round(gasto), nivel]
    }
    
    df_geral = pd.DataFrame(dados_gerais)
    
    return df_geral


def gerar_dataframe_perimetros(avaliacao: dict) -> pd.DataFrame:
    """
    Gera um DataFrame com os perímetros da avaliação.
    
    :param avaliacao: Dicionário com dados da avaliação
    :return: DataFrame formatado
    """
    perimetros = avaliacao.get("perimetros", {})
    
    dados = []
    for chave, nome in NOMES_PERIMETROS.items():
        valor = perimetros.get(chave, 0)
        dados.append({
            "Região": nome,
            "Medida (cm)": valor
        })
    
    return pd.DataFrame(dados)


def gerar_excel_completo(cliente: dict, avaliacoes: list[dict]) -> BytesIO:
    """
    Gera um arquivo Excel com todas as avaliações do cliente.
    
    :param cliente: Dicionário com dados do cliente
    :param avaliacoes: Lista de avaliações
    :return: Buffer com o arquivo Excel
    """
    buffer = BytesIO()
    
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        # Aba: Dados do Cliente
        dados_cliente = pd.DataFrame({
            "Campo": ["Nome", "Gênero", "Data Nascimento", "Biotipo"],
            "Valor": [
                cliente.get("nome", ""),
                cliente.get("genero", ""),
                cliente.get("data_nascimento", ""),
                cliente.get("biotipo", "")
            ]
        })
        dados_cliente.to_excel(writer, sheet_name="Cliente", index=False)
        
        # Aba: Histórico de Avaliações
        historico_dados = []
        for avaliacao in avaliacoes:
            peso = avaliacao.get("peso_kg", 0)
            altura = avaliacao.get("altura_cm", 0)
            imc = calcular_imc(peso, altura)
            
            historico_dados.append({
                "Data": avaliacao.get("data", ""),
                "Peso (kg)": peso,
                "Altura (cm)": altura,
                "IMC": imc,
                "Nível Atividade": avaliacao.get("nivel_atividade", "")
            })
        
        df_historico = pd.DataFrame(historico_dados)
        df_historico.to_excel(writer, sheet_name="Histórico", index=False)
        
        # Aba: Perímetros (última avaliação)
        if avaliacoes:
            ultima = avaliacoes[-1]
            df_perimetros = gerar_dataframe_perimetros(ultima)
            df_perimetros.to_excel(writer, sheet_name="Perímetros", index=False)
        
        # Aba: Evolução de Peso
        evolucao = []
        for i, avaliacao in enumerate(avaliacoes):
            peso_atual = avaliacao.get("peso_kg", 0)
            variacao = 0
            if i > 0:
                peso_anterior = avaliacoes[i-1].get("peso_kg", 0)
                variacao = peso_atual - peso_anterior
            
            evolucao.append({
                "Data": avaliacao.get("data", ""),
                "Peso (kg)": peso_atual,
                "Variação (kg)": variacao
            })
        
        df_evolucao = pd.DataFrame(evolucao)
        df_evolucao.to_excel(writer, sheet_name="Evolução", index=False)
    
    buffer.seek(0)
    return buffer


def renderizar_pagina_relatorios() -> None:
    """
    Renderiza a página de relatórios e exportação.
    """
    st.title("📄 Relatórios")
    
    # Verifica se há cliente selecionado
    if "cliente_selecionado_id" not in st.session_state or not st.session_state.cliente_selecionado_id:
        st.warning("⚠️ Selecione um cliente na barra lateral.")
        return
    
    cliente_id = st.session_state.cliente_selecionado_id
    cliente = buscar_cliente_por_id(cliente_id)
    
    if not cliente:
        st.error("Cliente não encontrado.")
        return
    
    nome_cliente = cliente.get("nome", "Cliente")
    st.info(f"📋 Relatórios de: **{nome_cliente}**")
    
    historico = obter_historico_avaliacoes(cliente_id)
    
    if not historico:
        st.warning("Este cliente não possui avaliações para gerar relatório.")
        return
    
    # Opções de exportação
    st.markdown("### 📊 Exportar para Excel")
    st.markdown("O arquivo Excel contém todas as avaliações, perímetros e evolução do cliente.")
    
    excel_buffer = gerar_excel_completo(cliente, historico)
    nome_arquivo = f"avaliacao_{nome_cliente.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.xlsx"
    
    st.download_button(
        label="📥 Baixar Excel Completo",
        data=excel_buffer,
        file_name=nome_arquivo,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )
    
    st.divider()
    
    # Preview dos dados
    st.markdown("### 👁️ Preview dos Dados")
    
    aba_geral, aba_perimetros, aba_evolucao = st.tabs([
        "📋 Dados Gerais",
        "📐 Perímetros",
        "📈 Evolução"
    ])
    
    ultima = historico[-1]
    
    with aba_geral:
        df_geral = gerar_dataframe_avaliacao(cliente, ultima)
        st.dataframe(df_geral, use_container_width=True, hide_index=True)
    
    with aba_perimetros:
        df_perimetros = gerar_dataframe_perimetros(ultima)
        st.dataframe(df_perimetros, use_container_width=True, hide_index=True)
    
    with aba_evolucao:
        evolucao_dados = []
        for avaliacao in historico:
            peso = avaliacao.get("peso_kg", 0)
            altura = avaliacao.get("altura_cm", 0)
            
            evolucao_dados.append({
                "Data": avaliacao.get("data", ""),
                "Peso (kg)": peso,
                "Altura (cm)": altura,
                "IMC": calcular_imc(peso, altura)
            })
        
        df_evolucao = pd.DataFrame(evolucao_dados)
        st.dataframe(df_evolucao, use_container_width=True, hide_index=True)
