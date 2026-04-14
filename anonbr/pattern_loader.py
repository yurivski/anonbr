# Copyright (C) 2026 Yuri Pontes
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Carregador central de padrões regex definidos em config/patterns.yaml.

Este módulo é o único ponto de acesso ao arquivo de padrões. Todos os
detectores importam daqui, nunca duplicam a string de regex no próprio código.

Fluxo de leitura:
    patterns.yaml -> load_raw() -> get_compiled() / get_compiled_by_name()
                                          │
                                          └──► cada Detector.__init__()
"""

import re
import yaml

from functools import lru_cache
from pathlib import Path

# Caminho absoluto até o YAML, calculado em relação a este arquivo:
PATTERNS_FILE: Path = Path(__file__).parent.parent / 'config' / 'patterns.yaml'

# Carregamento bruto 

@lru_cache(maxsize=1)
def load_raw() -> dict:
    """
    Lê o arquivo patterns.yaml e retorna o dicionário bruto.

    O resultado é cacheado em memória pelo lru_cache, o arquivo é aberto
    uma única vez por processo. Para forçar um recarregamento (ex.: testes),
    chame load_raw.cache_clear() antes.

    Retorna:
        dict com a estrutura completa do YAML:
        {
            'cpf': {'description': ..., 'priority': ..., 'patterns': [...]},
            'cnpj': {...},
            'email': {...},
            'telefone': {...},
        }

    Lança:
        FileNotFoundError - se config/patterns.yaml não existir.
        yaml.YAMLError   - se o arquivo estiver mal formatado.
    """
    with open(PATTERNS_FILE, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


# API pública
def get_patterns(key: str) -> list:
    """
    Retorna a lista de dicts de padrões brutos para um detector.

    Cada elemento da lista tem a forma:
        {
            'name': str - identificador único do padrão (ex.: 'formatted'),
            'regex': str - string regex,
            'description': str - descrição legível,
            'is_formatted': bool - (CPF/CNPJ) indica se tem separadores, [opcional]
            'test_cases': list - casos de teste documentados, [opcional]
        }

    Parâmetro:
        key - chave do YAML: 'cpf', 'cnpj', 'email' ou 'telefone'.
    """
    return load_raw()[key]['patterns']


def get_compiled(key: str) -> list:
    """
    Retorna uma lista de regexes já compilados, na mesma ordem em que
    aparecem no YAML.

    Uso típico - PhoneDetector precisa de uma lista ordenada:
        self.regexes = get_compiled('telefone')

    Parâmetro:
        key - chave do YAML: 'cpf', 'cnpj', 'email' ou 'telefone'.

    Retorna:
        [re.Pattern, re.Pattern, ...]
    """
    return [
        re.compile(p['regex'])
        for p in get_patterns(key)
    ]


def get_compiled_by_name(key: str) -> dict:
    """
    Retorna um dicionário {nome: regex_compilado} para um detector.

    Uso típico - CPFDetector precisa acessar padrões por nome:
        compiled = get_compiled_by_name('cpf')
        self.formatted_regex = compiled['formatted']
        self.unformatted_regex = compiled['unformatted']

    Parâmetro:
        key - chave do YAML: 'cpf', 'cnpj', 'email' ou 'telefone'.

    Retorna:
        {'nome_padrao': re.Pattern, ...}
    """
    return {
        p['name']: re.compile(p['regex'])
        for p in get_patterns(key)
    }
