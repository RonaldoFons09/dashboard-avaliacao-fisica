"""
Gerenciador de Clientes - Módulo de persistência de dados.

Este módulo é responsável por todas as operações de CRUD (Create, Read, Update, Delete)
relacionadas aos clientes no sistema de avaliação física.

Usa Google Sheets como banco de dados quando disponível, com fallback para JSON local.
"""

import json
import uuid
from pathlib import Path
from typing import Optional

# Tenta importar o gerenciador de Sheets
try:
    from dados.gerenciador_sheets import obter_aba_clientes, verificar_conexao
    SHEETS_DISPONIVEL = True
except ImportError:
    SHEETS_DISPONIVEL = False


CAMINHO_ARQUIVO_CLIENTES = Path(__file__).parent / "clientes.json"


def _usar_sheets() -> bool:
    """Verifica se deve usar Google Sheets ou JSON local."""
    if not SHEETS_DISPONIVEL:
        return False
    try:
        return verificar_conexao()
    except Exception:
        return False


# ============ FUNÇÕES PARA JSON LOCAL ============

def _carregar_dados_json() -> list[dict]:
    """Carrega os dados do arquivo JSON."""
    if not CAMINHO_ARQUIVO_CLIENTES.exists():
        return []
    
    with open(CAMINHO_ARQUIVO_CLIENTES, "r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


def _salvar_dados_json(clientes: list[dict]) -> None:
    """Salva a lista de clientes no arquivo JSON."""
    with open(CAMINHO_ARQUIVO_CLIENTES, "w", encoding="utf-8") as arquivo:
        json.dump(clientes, arquivo, ensure_ascii=False, indent=2)


# ============ FUNÇÕES PARA GOOGLE SHEETS ============

def _carregar_dados_sheets() -> list[dict]:
    """Carrega todos os clientes do Google Sheets."""
    try:
        aba = obter_aba_clientes()
        if not aba:
            return []
        
        registros = aba.get_all_records()
        
        # Converte para o formato esperado
        clientes = []
        for registro in registros:
            if registro.get("id"):
                cliente = {
                    "id": str(registro.get("id", "")),
                    "nome": str(registro.get("nome", "")),
                    "genero": str(registro.get("genero", "")),
                    "data_nascimento": str(registro.get("data_nascimento", "")),
                    "biotipo": str(registro.get("biotipo", "")),
                    "avaliacoes": []  # Avaliações são carregadas separadamente
                }
                clientes.append(cliente)
        
        return clientes
    except Exception as e:
        print(f"Erro ao carregar do Sheets: {e}")
        return []


def _adicionar_cliente_sheets(cliente: dict) -> bool:
    """Adiciona um cliente no Google Sheets."""
    try:
        aba = obter_aba_clientes()
        if not aba:
            return False
        
        linha = [
            cliente.get("id", ""),
            cliente.get("nome", ""),
            cliente.get("genero", ""),
            cliente.get("data_nascimento", ""),
            cliente.get("biotipo", "")
        ]
        
        aba.append_row(linha)
        return True
    except Exception as e:
        print(f"Erro ao adicionar no Sheets: {e}")
        return False


def _excluir_cliente_sheets(cliente_id: str) -> bool:
    """Remove um cliente do Google Sheets."""
    try:
        aba = obter_aba_clientes()
        if not aba:
            return False
        
        # Encontra a linha do cliente
        celula = aba.find(cliente_id)
        if celula:
            aba.delete_rows(celula.row)
            return True
        return False
    except Exception as e:
        print(f"Erro ao excluir no Sheets: {e}")
        return False


# ============ FUNÇÕES PÚBLICAS ============

def carregar_todos_clientes() -> list[dict]:
    """
    Carrega todos os clientes cadastrados.
    
    :return: Lista de clientes com todos os seus dados
    """
    if _usar_sheets():
        return _carregar_dados_sheets()
    return _carregar_dados_json()


def buscar_cliente_por_id(cliente_id: str) -> Optional[dict]:
    """
    Busca um cliente específico pelo seu ID único.
    
    :param cliente_id: ID único do cliente (UUID)
    :return: Dicionário com dados do cliente ou None se não encontrado
    """
    clientes = carregar_todos_clientes()
    
    for cliente in clientes:
        if cliente.get("id") == cliente_id:
            return cliente
    
    return None


def buscar_cliente_por_nome(nome: str) -> Optional[dict]:
    """
    Busca um cliente pelo nome exato.
    
    :param nome: Nome completo do cliente
    :return: Dicionário com dados do cliente ou None se não encontrado
    """
    clientes = carregar_todos_clientes()
    
    for cliente in clientes:
        if cliente.get("nome") == nome:
            return cliente
    
    return None


def listar_nomes_clientes() -> list[str]:
    """
    Retorna lista com os nomes de todos os clientes.
    
    :return: Lista de nomes dos clientes ordenada alfabeticamente
    """
    clientes = carregar_todos_clientes()
    nomes = [cliente.get("nome", "") for cliente in clientes]
    return sorted(nomes)


def criar_novo_cliente(
    nome: str,
    genero: str,
    data_nascimento: str,
    biotipo: str
) -> dict:
    """
    Cria um novo cliente com ID único.
    
    :param nome: Nome completo do cliente
    :param genero: Masculino ou Feminino
    :param data_nascimento: Data no formato YYYY-MM-DD
    :param biotipo: Ectomorfo, Mesomorfo ou Endomorfo
    :return: Dicionário do cliente criado com ID gerado
    """
    novo_cliente = {
        "id": str(uuid.uuid4()),
        "nome": nome,
        "genero": genero,
        "data_nascimento": data_nascimento,
        "biotipo": biotipo,
        "avaliacoes": []
    }
    
    if _usar_sheets():
        _adicionar_cliente_sheets(novo_cliente)
    else:
        clientes = _carregar_dados_json()
        clientes.append(novo_cliente)
        _salvar_dados_json(clientes)
    
    return novo_cliente


def atualizar_cliente(cliente_id: str, dados_atualizados: dict) -> bool:
    """
    Atualiza os dados de um cliente existente.
    
    :param cliente_id: ID único do cliente
    :param dados_atualizados: Dicionário com os campos a atualizar
    :return: True se atualizado com sucesso, False se cliente não encontrado
    """
    if _usar_sheets():
        # Para Sheets, precisaria implementar update de linha
        # Por simplicidade, mantemos JSON para updates
        pass
    
    clientes = _carregar_dados_json()
    
    for indice, cliente in enumerate(clientes):
        if cliente.get("id") == cliente_id:
            clientes[indice].update(dados_atualizados)
            clientes[indice]["id"] = cliente_id
            _salvar_dados_json(clientes)
            return True
    
    return False


def excluir_cliente(cliente_id: str) -> bool:
    """
    Remove um cliente do sistema.
    
    :param cliente_id: ID único do cliente
    :return: True se excluído com sucesso, False se não encontrado
    """
    if _usar_sheets():
        return _excluir_cliente_sheets(cliente_id)
    
    clientes = _carregar_dados_json()
    quantidade_original = len(clientes)
    
    clientes = [c for c in clientes if c.get("id") != cliente_id]
    
    if len(clientes) < quantidade_original:
        _salvar_dados_json(clientes)
        return True
    
    return False


def contar_clientes() -> int:
    """
    Retorna a quantidade total de clientes cadastrados.
    
    :return: Número de clientes
    """
    clientes = carregar_todos_clientes()
    return len(clientes)
