"""
Calculadora Corporal - Módulo de lógica de negócio.

Este módulo contém todas as funções de cálculo relacionadas à composição corporal,
incluindo IMC, TMB, gasto calórico e classificações.
"""

from datetime import date, datetime
from typing import Tuple


# Fatores de atividade física para cálculo de gasto calórico diário
FATORES_ATIVIDADE = {
    "Sedentário": 1.2,
    "Levemente ativo": 1.375,
    "Moderadamente ativo": 1.55,
    "Muito ativo": 1.725,
    "Extremamente ativo": 1.9
}

# Classificações de IMC segundo a OMS
CLASSIFICACOES_IMC = [
    (18.5, "Abaixo do peso"),
    (24.9, "Peso normal"),
    (29.9, "Sobrepeso"),
    (34.9, "Obesidade grau I"),
    (39.9, "Obesidade grau II"),
    (float("inf"), "Obesidade grau III")
]

# Gasto calórico por intensidade de treino (kcal por sessão de 1 hora)
GASTO_POR_INTENSIDADE = {
    "Adaptação": 100,
    "Iniciante": 150,
    "Intermediário": 187.5,
    "Avançado": 350
}


def calcular_idade(data_nascimento: str) -> int:
    """
    Calcula a idade atual a partir da data de nascimento.
    
    :param data_nascimento: Data no formato YYYY-MM-DD
    :return: Idade em anos completos
    """
    if not data_nascimento:
        return 0
    
    nascimento = datetime.strptime(data_nascimento, "%Y-%m-%d").date()
    hoje = date.today()
    
    idade = hoje.year - nascimento.year
    
    # Ajusta se ainda não fez aniversário este ano
    if (hoje.month, hoje.day) < (nascimento.month, nascimento.day):
        idade -= 1
    
    return idade


def calcular_imc(peso_kg: float, altura_cm: float) -> float:
    """
    Calcula o Índice de Massa Corporal (IMC).
    
    Fórmula: IMC = peso (kg) / altura² (m)
    
    :param peso_kg: Peso em quilogramas
    :param altura_cm: Altura em centímetros
    :return: Valor do IMC com 2 casas decimais
    """
    if peso_kg <= 0 or altura_cm <= 0:
        return 0.0
    
    altura_metros = altura_cm / 100
    imc = peso_kg / (altura_metros ** 2)
    
    return round(imc, 2)


def classificar_imc(imc: float) -> str:
    """
    Retorna a classificação do IMC segundo a OMS.
    
    :param imc: Valor do IMC calculado
    :return: Classificação textual (ex: "Peso normal", "Sobrepeso")
    """
    if imc <= 0:
        return "Não calculado"
    
    for limite, classificacao in CLASSIFICACOES_IMC:
        if imc <= limite:
            return classificacao
    
    return "Não classificado"


def obter_cor_imc(imc: float) -> str:
    """
    Retorna uma cor indicativa para o IMC (para uso em visualizações).
    
    :param imc: Valor do IMC calculado
    :return: Código de cor em formato hexadecimal
    """
    if imc <= 0:
        return "#808080"  # Cinza
    elif imc < 18.5:
        return "#3498db"  # Azul - Abaixo do peso
    elif imc < 25:
        return "#2ecc71"  # Verde - Normal
    elif imc < 30:
        return "#f39c12"  # Laranja - Sobrepeso
    else:
        return "#e74c3c"  # Vermelho - Obesidade


def calcular_tmb(peso_kg: float, altura_cm: float, idade: int, genero: str) -> float:
    """
    Calcula a Taxa Metabólica Basal usando a fórmula Mifflin-St Jeor.
    
    Esta é a quantidade de calorias que o corpo queima em repouso.
    
    Fórmulas:
    - Masculino: TMB = (10 × peso) + (6.25 × altura) - (5 × idade) + 5
    - Feminino: TMB = (10 × peso) + (6.25 × altura) - (5 × idade) - 161
    
    :param peso_kg: Peso em quilogramas
    :param altura_cm: Altura em centímetros
    :param idade: Idade em anos
    :param genero: "Masculino" ou "Feminino"
    :return: TMB em kcal/dia
    """
    if peso_kg <= 0 or altura_cm <= 0 or idade <= 0:
        return 0.0
    
    tmb_base = (10 * peso_kg) + (6.25 * altura_cm) - (5 * idade)
    
    if genero.lower() == "masculino":
        tmb = tmb_base + 5
    else:
        tmb = tmb_base - 161
    
    return round(tmb, 1)


def calcular_gasto_calorico_diario(tmb: float, nivel_atividade: str) -> float:
    """
    Calcula o gasto calórico diário total (TDEE).
    
    Multiplica a TMB pelo fator de atividade física.
    
    :param tmb: Taxa Metabólica Basal em kcal
    :param nivel_atividade: Nível de atividade física (chave de FATORES_ATIVIDADE)
    :return: Gasto calórico diário em kcal
    """
    if tmb <= 0:
        return 0.0
    
    fator = FATORES_ATIVIDADE.get(nivel_atividade, 1.2)
    gasto = tmb * fator
    
    return round(gasto, 1)


def calcular_metas_caloricas(gasto_diario: float) -> dict:
    """
    Calcula metas calóricas para diferentes objetivos.
    
    :param gasto_diario: Gasto calórico diário total (TDEE)
    :return: Dicionário com metas para déficit, manutenção e superávit
    """
    if gasto_diario <= 0:
        return {
            "deficit_leve": 0,
            "deficit_moderado": 0,
            "manutencao": 0,
            "superavit_leve": 0,
            "superavit_moderado": 0
        }
    
    return {
        "deficit_leve": round(gasto_diario - 250, 0),
        "deficit_moderado": round(gasto_diario - 500, 0),
        "manutencao": round(gasto_diario, 0),
        "superavit_leve": round(gasto_diario + 250, 0),
        "superavit_moderado": round(gasto_diario + 500, 0)
    }


def calcular_gasto_por_treino(intensidade: str) -> float:
    """
    Retorna o gasto calórico estimado por sessão de treino (1 hora).
    
    :param intensidade: Nível de intensidade do treino
    :return: Gasto em kcal por sessão
    """
    return GASTO_POR_INTENSIDADE.get(intensidade, 100)


def calcular_peso_ideal(altura_cm: float, genero: str) -> Tuple[float, float]:
    """
    Calcula a faixa de peso ideal baseado na altura (IMC entre 18.5 e 24.9).
    
    :param altura_cm: Altura em centímetros
    :param genero: "Masculino" ou "Feminino" (não usado, mas preparado para expansão)
    :return: Tupla (peso_minimo, peso_maximo) em kg
    """
    if altura_cm <= 0:
        return (0.0, 0.0)
    
    altura_metros = altura_cm / 100
    
    peso_minimo = 18.5 * (altura_metros ** 2)
    peso_maximo = 24.9 * (altura_metros ** 2)
    
    return (round(peso_minimo, 1), round(peso_maximo, 1))


def listar_niveis_atividade() -> list[str]:
    """
    Retorna lista de níveis de atividade disponíveis.
    
    :return: Lista de strings com os níveis
    """
    return list(FATORES_ATIVIDADE.keys())


def listar_intensidades_treino() -> list[str]:
    """
    Retorna lista de intensidades de treino disponíveis.
    
    :return: Lista de strings com as intensidades
    """
    return list(GASTO_POR_INTENSIDADE.keys())


# =====================================================
# DOBRAS CUTÂNEAS - MÉTODO POLLOCK 7 DOBRAS
# =====================================================

# Classificações de percentual de gordura por gênero
CLASSIFICACOES_GORDURA_MASCULINO = [
    (5.9, "Essencial"),
    (13.9, "Atlético"),
    (17.9, "Fitness"),
    (24.9, "Aceitável"),
    (float("inf"), "Obesidade")
]

CLASSIFICACOES_GORDURA_FEMININO = [
    (13.9, "Essencial"),
    (20.9, "Atlético"),
    (24.9, "Fitness"),
    (31.9, "Aceitável"),
    (float("inf"), "Obesidade")
]


def calcular_soma_7_dobras(dobras: dict) -> float:
    """
    Calcula a soma das 7 dobras cutâneas.
    
    :param dobras: Dicionário com as 7 medidas em mm
    :return: Soma total em mm
    """
    chaves = [
        "peitoral", "axilar_media", "triceps", "subescapular",
        "abdominal", "suprailiaca", "coxa"
    ]
    
    soma = sum(dobras.get(chave, 0) for chave in chaves)
    return soma


def calcular_densidade_corporal_pollock7(
    soma_dobras: float,
    idade: int,
    genero: str
) -> float:
    """
    Calcula a densidade corporal usando as fórmulas de Jackson-Pollock (1978).
    
    Fórmulas:
    - Masculino: DC = 1.112 - (0.00043499 × Σ7) + (0.00000055 × Σ7²) - (0.00028826 × idade)
    - Feminino: DC = 1.097 - (0.00046971 × Σ7) + (0.00000056 × Σ7²) - (0.00012828 × idade)
    
    :param soma_dobras: Soma das 7 dobras em mm
    :param idade: Idade em anos
    :param genero: "Masculino" ou "Feminino"
    :return: Densidade corporal (g/cm³)
    """
    if soma_dobras <= 0 or idade <= 0:
        return 0.0
    
    if genero.lower() == "masculino":
        dc = (1.112 
              - (0.00043499 * soma_dobras) 
              + (0.00000055 * soma_dobras ** 2) 
              - (0.00028826 * idade))
    else:
        dc = (1.097 
              - (0.00046971 * soma_dobras) 
              + (0.00000056 * soma_dobras ** 2) 
              - (0.00012828 * idade))
    
    return round(dc, 5)


def calcular_percentual_gordura(densidade_corporal: float) -> float:
    """
    Calcula o percentual de gordura corporal usando a fórmula de Siri.
    
    Fórmula: %G = [(4.95 / DC) - 4.5] × 100
    
    :param densidade_corporal: Densidade corporal em g/cm³
    :return: Percentual de gordura corporal
    """
    if densidade_corporal <= 0:
        return 0.0
    
    percentual = ((4.95 / densidade_corporal) - 4.5) * 100
    
    # Limita valores extremos
    percentual = max(0, min(percentual, 60))
    
    return round(percentual, 1)


def calcular_gordura_pollock7(dobras: dict, idade: int, genero: str) -> dict:
    """
    Calcula todos os resultados de composição corporal pelo método Pollock 7.
    
    :param dobras: Dicionário com as 7 dobras cutâneas em mm
    :param idade: Idade em anos
    :param genero: "Masculino" ou "Feminino"
    :return: Dicionário com soma, densidade, percentual e classificação
    """
    soma = calcular_soma_7_dobras(dobras)
    densidade = calcular_densidade_corporal_pollock7(soma, idade, genero)
    percentual = calcular_percentual_gordura(densidade)
    classificacao = classificar_percentual_gordura(percentual, genero)
    
    return {
        "soma_dobras": soma,
        "densidade_corporal": densidade,
        "percentual_gordura": percentual,
        "classificacao": classificacao
    }


def classificar_percentual_gordura(percentual: float, genero: str) -> str:
    """
    Classifica o percentual de gordura corporal.
    
    :param percentual: Percentual de gordura
    :param genero: "Masculino" ou "Feminino"
    :return: Classificação textual
    """
    if percentual <= 0:
        return "Não calculado"
    
    classificacoes = (
        CLASSIFICACOES_GORDURA_MASCULINO 
        if genero.lower() == "masculino" 
        else CLASSIFICACOES_GORDURA_FEMININO
    )
    
    for limite, classificacao in classificacoes:
        if percentual <= limite:
            return classificacao
    
    return "Não classificado"


def obter_cor_gordura(percentual: float, genero: str) -> str:
    """
    Retorna uma cor indicativa para o percentual de gordura.
    
    :param percentual: Percentual de gordura
    :param genero: "Masculino" ou "Feminino"
    :return: Código de cor em formato hexadecimal
    """
    if percentual <= 0:
        return "#808080"  # Cinza
    
    classificacao = classificar_percentual_gordura(percentual, genero)
    
    cores = {
        "Essencial": "#e74c3c",   # Vermelho - muito baixo (risco)
        "Atlético": "#2ecc71",     # Verde - excelente
        "Fitness": "#27ae60",      # Verde escuro - bom
        "Aceitável": "#f39c12",    # Laranja - moderado
        "Obesidade": "#c0392b"     # Vermelho escuro - alto
    }
    
    return cores.get(classificacao, "#808080")


def calcular_massas_corporais(peso_kg: float, percentual_gordura: float) -> dict:
    """
    Calcula a massa gorda e massa magra em kg.
    
    :param peso_kg: Peso total em kg
    :param percentual_gordura: Percentual de gordura corporal
    :return: Dicionário com massa_gorda e massa_magra em kg
    """
    if peso_kg <= 0 or percentual_gordura < 0:
        return {"massa_gorda": 0.0, "massa_magra": 0.0}
    
    massa_gorda = peso_kg * (percentual_gordura / 100)
    massa_magra = peso_kg - massa_gorda
    
    return {
        "massa_gorda": round(massa_gorda, 1),
        "massa_magra": round(massa_magra, 1)
    }
