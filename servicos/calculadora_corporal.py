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
