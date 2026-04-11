# Copyright (C) 2026 Yuri Pontes
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Detecta números de CPF em múltiplos formatos e fornece funcionalidade de mascaramento
preservando a estrutura do documento.

Fonte dos padrões regex: config/patterns.yaml  -> chave 'cpf'
  - formatted: CPF com separadores (ex.: 375.096.646-08)
  - unformatted: CPF apenas com dígitos (ex.: 37509664608)
"""

import re
from anonbr.pattern_loader import get_compiled_by_name


class CPFDetector:
    """
    Detecta e mascara números de CPF em texto livre.

    Os padrões regex são carregados automaticamente de config/patterns.yaml
    no momento da instanciação, não há strings de regex hardcoded aqui.

    Atributos criados em __init__:
        formatted_regex - re.Pattern para CPF com separadores (. - /)
        unformatted_regex - re.Pattern para CPF apenas numérico (11 dígitos)
    """

    def __init__(self):
        # Carrega os dois padrões do YAML indexados pelo campo 'name'
        compiled = get_compiled_by_name('cpf')

        # Padrão para CPF formatado: 375.096.646-08 / 375/096/646-08 etc.
        self.formatted_regex = compiled['formatted']

        # Padrão para CPF sem formatação: 37509664608 (exatamente 11 dígitos)
        self.unformatted_regex = compiled['unformatted']

    def detect(self, text: str) -> list:
        """
        Busca todos os CPFs no texto e retorna uma lista de ocorrências.

        Estratégia:
          1. Primeiro busca CPFs formatados (mais específicos).
          2. Depois busca CPFs sem formatação, ignorando posições que já
             foram capturadas na etapa anterior (evita sobreposição).

        Parâmetro:
            text - string de texto onde a busca será realizada.

        Retorna:
            Lista de tuplas (cpf, inicio, fim, is_formatted):
                cpf - string do CPF encontrado
                inicio - índice de início no texto
                fim - índice de fim no texto
                is_formatted - True se contém separadores (., -, /)
        """
        results = []

        # CPFs formatados 
        for match in self.formatted_regex.finditer(text):
            cpf = match.group()
            results.append((cpf, match.start(), match.end(), True))

        # CPFs sem formatação, pula posições já ocupadas
        for match in self.unformatted_regex.finditer(text):
            if not self._overlaps_formatted(match, results):
                cpf = match.group()
                results.append((cpf, match.start(), match.end(), False))

        return results

    def _overlaps_formatted(self, match, formatted_results: list) -> bool:
        """
        Verifica se um match não formatado sobrepõe algum resultado já registrado.

        Impede que os 11 dígitos de um CPF formatado (ex.: '37509664608'
        extraídos de '375.096.646-08') sejam detectados novamente como
        CPF sem formatação.

        Parâmetros:
            match - objeto re.Match do CPF sem formatação.
            formatted_results - lista de resultados já encontrados.

        Retorna:
            True se há sobreposição (o match deve ser ignorado).
        """
        start, end = match.start(), match.end()
        for _, f_start, f_end, _ in formatted_results:
            # Sobreposição ocorre quando os intervalos se cruzam
            if not (end <= f_start or start >= f_end):
                return True
        return False

    def mask(self, cpf: str, level: str = 'default') -> str:
        """
        Mascara um CPF preservando o formato original (formatado ou não).

        Níveis de mascaramento:
            'high' -> XXX.XXX.XXX-XX (todos os dígitos ocultos)
            'default'-> XXX.456.XXX-XX (revela o trecho central, dígitos 4–6)
            'low' -> XXX.XX6.789-09 (revela o final, dígitos 7–11)

        Parâmetros:
            cpf - string do CPF (formatado ou só dígitos).
            level - nível de mascaramento: 'high', 'default' ou 'low'.

        Retorna:
            CPF mascarado no mesmo formato de entrada.
        """
        # Extrai apenas os dígitos para aplicar a lógica de mascaramento
        digits = ''.join(re.findall(r'\d', cpf))

        # Detecta se a entrada tem separadores (. ou -) para preservar o formato
        is_formatted = bool(re.findall(r'[.\-]', cpf))

        if level == 'high':
            # Tudo mascarado: nenhum dígito revelado
            masked = 'X' * 11

        elif level == 'low':
            # Revela os 5 últimos dígitos (posições 6–10)
            masked = 'X' * 6 + digits[6:11]

        else:
            # Padrão: revela os 3 dígitos centrais (posições 3–5)
            masked = 'X' * 3 + digits[3:6] + 'X' * 5

        if is_formatted:
            # Reconstrói com separadores: 375.096.XXX-XX
            return f"{masked[:3]}.{masked[3:6]}.{masked[6:9]}-{masked[9:11]}"

        return masked


# Funções auxiliares
def detect_cpf(text: str) -> list:
    """
    Atalho funcional para CPFDetector().detect(text).

    Instancia um detector temporário e retorna as ocorrências de CPF no texto.
    Use quando não precisar reutilizar o detector.
    """
    detector = CPFDetector()
    return detector.detect(text)


def mask_cpf(cpf: str, level: str = 'default') -> str:
    """
    Atalho funcional para CPFDetector().mask(cpf, level).

    Instancia um detector temporário e retorna o CPF mascarado.
    Use quando não precisar reutilizar o detector.
    """
    detector = CPFDetector()
    return detector.mask(cpf, level)
