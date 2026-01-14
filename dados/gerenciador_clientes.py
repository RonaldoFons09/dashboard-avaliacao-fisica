"""
Gerenciador de Clientes - Módulo de persistência de dados.

Este módulo é responsável por todas as operações de CRUD (Create, Read, Update, Delete)
relacionadas aos clientes no sistema de avaliação física.
"""

import json
import uuid
from pathlib import Path
from typing import Optional


CAMINHO_ARQUIVO_CLIENTES = Path(__file__).parent / "clientes.json"


def _carregar_dados_json() -> list[dict]:
    """
    Carrega os dados do arquivo JSON.
    
    :return: Lista de clientes ou lista vazia se arquivo não existir
    """
    if not CAMINHO_ARQUIVO_CLIENTES.exists():
        return []
    
    with open(CAMINHO_ARQUIVO_CLIENTES, "r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


def _salvar_dados_json(clientes: list[dict]) -> None:
    """
    Salva a lista de clientes no arquivo JSON.
    
    :param clientes: Lista de dicionários com dados dos clientes
    """
    with open(CAMINHO_ARQUIVO_CLIENTES, "w", encoding="utf-8") as arquivo:
        json.dump(clientes, arquivo, ensure_ascii=False, indent=2)


def carregar_todos_clientes() -> list[dict]:
    """
    Carrega todos os clientes cadastrados.
    
    :return: Lista de clientes com todos os seus dados
    """
    return _carregar_dados_json()


def buscar_cliente_por_id(cliente_id: str) -> Optional[dict]:
    """
    Busca um cliente específico pelo seu ID único.
    
    :param cliente_id: ID único do cliente (UUID)
    :return: Dicionário com dados do cliente ou None se não encontrado
    """
    clientes = _carregar_dados_json()
    
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
    clientes = _carregar_dados_json()
    
    for cliente in clientes:
        if cliente.get("nome") == nome:
            return cliente
    
    return None


def listar_nomes_clientes() -> list[str]:
    """
    Retorna lista com os nomes de todos os clientes.
    
    Útil para preencher selectboxes e dropdowns.
    
    :return: Lista de nomes dos clientes ordenada alfabeticamente
    """
    clientes = _carregar_dados_json()
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
    clientes = _carregar_dados_json()
    
    for indice, cliente in enumerate(clientes):
        if cliente.get("id") == cliente_id:
            # Mantém o ID e avaliacoes, atualiza o resto
            clientes[indice].update(dados_atualizados)
            clientes[indice]["id"] = cliente_id  # Garante que ID não mude
            _salvar_dados_json(clientes)
            return True
    
    return False


def excluir_cliente(cliente_id: str) -> bool:
    """
    Remove um cliente do sistema.
    
    :param cliente_id: ID único do cliente
    :return: True se excluído com sucesso, False se não encontrado
    """
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
    clientes = _carregar_dados_json()
    return len(clientes)
