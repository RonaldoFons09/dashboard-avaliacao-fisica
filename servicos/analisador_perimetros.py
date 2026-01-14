"""
Analisador de Perímetros - Módulo de lógica de negócio.

Este módulo contém todas as funções de análise relacionadas aos perímetros
corporais, incluindo comparações, simetria e preparação de dados para gráficos.
"""

from typing import Optional


# Nomes amigáveis para exibição dos perímetros
NOMES_PERIMETROS = {
    "braco_direito_relaxado": "Braço Dir. (Relaxado)",
    "braco_direito_contraido": "Braço Dir. (Contraído)",
    "braco_esquerdo_relaxado": "Braço Esq. (Relaxado)",
    "braco_esquerdo_contraido": "Braço Esq. (Contraído)",
    "antebraco_direito": "Antebraço Direito",
    "antebraco_esquerdo": "Antebraço Esquerdo",
    "ombro": "Ombro",
    "torax": "Tórax",
    "cintura": "Cintura",
    "abdomen": "Abdômen",
    "quadril": "Quadril",
    "coxa_superior_direita": "Coxa Sup. Direita",
    "coxa_superior_esquerda": "Coxa Sup. Esquerda",
    "coxa_media_direita": "Coxa Méd. Direita",
    "coxa_media_esquerda": "Coxa Méd. Esquerda",
    "coxa_inferior_direita": "Coxa Inf. Direita",
    "coxa_inferior_esquerda": "Coxa Inf. Esquerda",
    "panturrilha_direita": "Panturrilha Direita",
    "panturrilha_esquerda": "Panturrilha Esquerda"
}

# Pares de medidas para análise de simetria (direito, esquerdo)
PARES_SIMETRIA = [
    ("braco_direito_relaxado", "braco_esquerdo_relaxado"),
    ("braco_direito_contraido", "braco_esquerdo_contraido"),
    ("antebraco_direito", "antebraco_esquerdo"),
    ("coxa_superior_direita", "coxa_superior_esquerda"),
    ("coxa_media_direita", "coxa_media_esquerda"),
    ("coxa_inferior_direita", "coxa_inferior_esquerda"),
    ("panturrilha_direita", "panturrilha_esquerda")
]

# Medidas para o gráfico radar (medidas principais)
MEDIDAS_RADAR = [
    "ombro",
    "torax", 
    "braco_direito_contraido",
    "antebraco_direito",
    "cintura",
    "abdomen",
    "quadril",
    "coxa_superior_direita",
    "coxa_media_direita",
    "panturrilha_direita"
]


def obter_nome_amigavel(chave_perimetro: str) -> str:
    """
    Retorna o nome amigável para exibição do perímetro.
    
    :param chave_perimetro: Chave interna do perímetro
    :return: Nome formatado para exibição
    """
    return NOMES_PERIMETROS.get(chave_perimetro, chave_perimetro)


def calcular_diferenca_simetria(lado_direito: float, lado_esquerdo: float) -> dict:
    """
    Calcula a diferença entre lados direito e esquerdo.
    
    :param lado_direito: Medida do lado direito em cm
    :param lado_esquerdo: Medida do lado esquerdo em cm
    :return: Dicionário com diferença absoluta, percentual e lado dominante
    """
    diferenca_absoluta = abs(lado_direito - lado_esquerdo)
    
    if lado_esquerdo > 0:
        diferenca_percentual = (diferenca_absoluta / lado_esquerdo) * 100
    else:
        diferenca_percentual = 0.0
    
    if lado_direito > lado_esquerdo:
        lado_dominante = "Direito"
    elif lado_esquerdo > lado_direito:
        lado_dominante = "Esquerdo"
    else:
        lado_dominante = "Igual"
    
    return {
        "diferenca_cm": round(diferenca_absoluta, 1),
        "diferenca_percentual": round(diferenca_percentual, 1),
        "lado_dominante": lado_dominante
    }


def analisar_simetria_completa(perimetros: dict) -> list[dict]:
    """
    Analisa a simetria de todos os pares de membros.
    
    :param perimetros: Dicionário com todas as medidas
    :return: Lista de análises de simetria para cada par
    """
    resultados = []
    
    for chave_direita, chave_esquerda in PARES_SIMETRIA:
        valor_direito = perimetros.get(chave_direita, 0)
        valor_esquerdo = perimetros.get(chave_esquerda, 0)
        
        if valor_direito > 0 and valor_esquerdo > 0:
            analise = calcular_diferenca_simetria(valor_direito, valor_esquerdo)
            analise["membro"] = obter_nome_amigavel(chave_direita).split(" ")[0]
            analise["valor_direito"] = valor_direito
            analise["valor_esquerdo"] = valor_esquerdo
            resultados.append(analise)
    
    return resultados


def calcular_variacao_entre_avaliacoes(
    perimetros_anterior: dict, 
    perimetros_atual: dict
) -> dict:
    """
    Calcula a variação de cada medida entre duas avaliações.
    
    :param perimetros_anterior: Perímetros da avaliação mais antiga
    :param perimetros_atual: Perímetros da avaliação mais recente
    :return: Dicionário com variação absoluta e percentual de cada medida
    """
    variacoes = {}
    
    for chave in NOMES_PERIMETROS.keys():
        valor_anterior = perimetros_anterior.get(chave, 0)
        valor_atual = perimetros_atual.get(chave, 0)
        
        if valor_anterior > 0 and valor_atual > 0:
            diferenca = valor_atual - valor_anterior
            percentual = (diferenca / valor_anterior) * 100
            
            variacoes[chave] = {
                "nome": obter_nome_amigavel(chave),
                "anterior": valor_anterior,
                "atual": valor_atual,
                "diferenca_cm": round(diferenca, 1),
                "diferenca_percentual": round(percentual, 1),
                "status": "aumento" if diferenca > 0 else "reducao" if diferenca < 0 else "igual"
            }
    
    return variacoes


def preparar_dados_grafico_radar(perimetros: dict) -> dict:
    """
    Prepara dados para o gráfico radar do Plotly.
    
    :param perimetros: Dicionário com todas as medidas
    :return: Dicionário com 'categorias' e 'valores' para o gráfico
    """
    categorias = []
    valores = []
    
    for chave in MEDIDAS_RADAR:
        nome = obter_nome_amigavel(chave)
        valor = perimetros.get(chave, 0)
        
        categorias.append(nome)
        valores.append(valor)
    
    return {
        "categorias": categorias,
        "valores": valores
    }


def preparar_comparacao_radar(
    perimetros_anterior: dict,
    perimetros_atual: dict
) -> dict:
    """
    Prepara dados para comparação de duas avaliações no gráfico radar.
    
    :param perimetros_anterior: Perímetros da avaliação mais antiga
    :param perimetros_atual: Perímetros da avaliação mais recente
    :return: Dicionário com dados para duas séries no gráfico
    """
    categorias = []
    valores_anterior = []
    valores_atual = []
    
    for chave in MEDIDAS_RADAR:
        nome = obter_nome_amigavel(chave)
        
        categorias.append(nome)
        valores_anterior.append(perimetros_anterior.get(chave, 0))
        valores_atual.append(perimetros_atual.get(chave, 0))
    
    return {
        "categorias": categorias,
        "valores_anterior": valores_anterior,
        "valores_atual": valores_atual
    }


def calcular_soma_perimetros(perimetros: dict, tipo: str = "todos") -> float:
    """
    Calcula a soma de perímetros para análise geral.
    
    :param perimetros: Dicionário com todas as medidas
    :param tipo: "todos", "superior" (braços, ombro, tórax) ou "inferior" (coxas, panturrilha)
    :return: Soma dos perímetros selecionados
    """
    if tipo == "superior":
        chaves = ["ombro", "torax", "braco_direito_contraido", "braco_esquerdo_contraido"]
    elif tipo == "inferior":
        chaves = ["coxa_superior_direita", "coxa_superior_esquerda", 
                  "panturrilha_direita", "panturrilha_esquerda"]
    else:
        chaves = list(NOMES_PERIMETROS.keys())
    
    soma = sum(perimetros.get(chave, 0) for chave in chaves)
    return round(soma, 1)


def calcular_relacao_cintura_quadril(perimetros: dict) -> Optional[float]:
    """
    Calcula a Relação Cintura-Quadril (RCQ).
    
    Indicador de risco cardiovascular:
    - Homens: Alto risco se > 0.90
    - Mulheres: Alto risco se > 0.85
    
    :param perimetros: Dicionário com medidas
    :return: Valor da RCQ ou None se dados insuficientes
    """
    cintura = perimetros.get("cintura", 0)
    quadril = perimetros.get("quadril", 0)
    
    if cintura <= 0 or quadril <= 0:
        return None
    
    return round(cintura / quadril, 2)


def classificar_rcq(rcq: float, genero: str) -> str:
    """
    Classifica a Relação Cintura-Quadril por risco cardiovascular.
    
    :param rcq: Valor da RCQ
    :param genero: "Masculino" ou "Feminino"
    :return: Classificação do risco
    """
    if rcq is None:
        return "Não calculado"
    
    if genero.lower() == "masculino":
        if rcq < 0.90:
            return "Baixo risco"
        elif rcq < 1.0:
            return "Risco moderado"
        else:
            return "Alto risco"
    else:
        if rcq < 0.80:
            return "Baixo risco"
        elif rcq < 0.85:
            return "Risco moderado"
        else:
            return "Alto risco"
