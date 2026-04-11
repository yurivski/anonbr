# Copyright (C) 2026 Yuri Pontes
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Detecta e censura números de CNPJ em múltiplos formatos preservando a estrutura do documento.

Fonte dos padrões regex: config/patterns.yaml -> chave 'cnpj'
  - formatted:   CNPJ com separadores (ex.: 11.222.333/0001-81)
  - unformatted: CNPJ apenas com dígitos (ex.: 11222333000181)
"""

import re
from anonbr.pattern_loader import get_compiled_by_name

class CNPJDetector:
    """
    Detecta e mascara números de CNPJ em texto livre.

    Os padrões regex são carregados automaticamente de config/patterns.yaml
    no momento da instanciação, não há strings de regex hardcoded aqui.

    Atributos criados em __init__:
        formatted_regex - re.Pattern para CNPJ com separadores (. / -)
        unformatted_regex - re.Pattern para CNPJ apenas numérico (14 dígitos)
    """

    def __init__(self):
        # Carrega os dois padrões do YAML indexados pelo campo 'name'
        compiled = get_compiled_by_name('cnpj')

        # Padrão para CNPJ formatado: 11.222.333/0001-81 e variações
        self.formatted_regex = compiled['formatted']

        # Padrão para CNPJ sem formatação: 11222333000181 (exatamente 14 dígitos)
        self.unformatted_regex = compiled['unformatted']

    def detect(self, text: str) -> list:
        """
        Busca todos os CNPJs no texto e retorna uma lista de ocorrências.

          1. Busca CNPJs formatados primeiro (mais específicos e com prioridade).
          2. Busca CNPJs sem formatação, ignorando posições já capturadas.

        Parâmetro:
            text - string de texto onde a busca será realizada.

        Retorna:
            Lista de tuplas (cnpj, inicio, fim, is_formatted):
                cnpj - string do CNPJ encontrado
                inicio - índice de início no texto
                fim - índice de fim no texto
                is_formatted - True se contém separadores (., /, -)
        """
        results = []

        # CNPJs formatados, maior especificidade, sem sobreposição
        for match in self.formatted_regex.finditer(text):
            if not self._overlaps_formatted(match, results):
                cnpj = match.group()
                results.append((cnpj, match.start(), match.end(), True))

        # CNPJs sem formatação, pula posições já registradas
        for match in self.unformatted_regex.finditer(text):
            if not self._overlaps_formatted(match, results):
                cnpj = match.group()
                results.append((cnpj, match.start(), match.end(), False))

        return results

    def _overlaps_formatted(self, match, formatted_results: list) -> bool:
        """
        Verifica se um match sobrepõe algum resultado já registrado.

        Impede que os 14 dígitos de um CNPJ formatado sejam detectados
        novamente como CNPJ sem formatação.

        Parâmetros:
            match - objeto re.Match do CNPJ sendo avaliado.
            formatted_results - lista de resultados já encontrados.

        Retorna:
            True se há sobreposição (o match deve ser ignorado).
        """
        start, end = match.start(), match.end()
        for _, f_start, f_end, _ in formatted_results:
            if not (end <= f_start or start >= f_end):
                return True
        return False

    def mask(self, cnpj: str, level: str = 'default') -> str:
        """
        Mascara um CNPJ preservando o formato original (formatado ou não).

        Estrutura do CNPJ: RR.EEE.EEE/FFFF-VV  (14 dígitos)
            RR - raiz (2 dígitos) - identifica a empresa-mãe
            EEE - sufixo da raiz (6 dígitos)
            FFFF - filial/estabelecimento (4 dígitos)
            VV - dígitos verificadores (2 dígitos)

        Níveis de mascaramento:
            'high' - XX.XXX.XXX/XXXX-XX (todos os dígitos ocultos)
            'default' - XX.222.333/XXXX-XX (revela a parte central da raiz, dígitos 3–8)
            'low' - XX.XXX.XXX/0001-81 (revela filial + verificadores, dígitos 9–14)

        Parâmetros:
            cnpj - string do CNPJ (formatado ou só dígitos).
            level - nível de mascaramento: 'high', 'default' ou 'low'.

        Retorna:
            CNPJ mascarado no mesmo formato de entrada.
        """
        # Verifica se a entrada tem separadores para preservar o formato na saída
        is_formatted = not bool(re.fullmatch(r'\d{14}', cnpj))

        # Extrai apenas os dígitos para construir o padrão mascarado
        digits = re.sub(r'\D', '', cnpj)

        if level == 'high':
            # Censura todos os 14 dígitos
            masked = 'X' * 14

        elif level == 'low':
            # Revela os últimos 6 dígitos: filial (4) + verificadores (2)
            masked = 'X' * 8 + digits[8:14]

        else:
            # Padrão: revela dígitos 3–8 (parte central da raiz), oculta início e fim
            masked = 'X' * 2 + digits[2:8] + 'X' * 6

        if is_formatted:
            # Reconstrói no formato padrão: XX.EEE.EEE/FFFF-VV
            return f"{masked[:2]}.{masked[2:5]}.{masked[5:8]}/{masked[8:12]}-{masked[12:14]}"

        return masked


# Funções auxiliares 
def detect_cnpj(text: str) -> list:
    """
    Atalho funcional para CNPJDetector().detect(text).

    Instancia um detector temporário e retorna as ocorrências de CNPJ no texto.
    Use quando não precisar reutilizar o detector.
    """
    detector = CNPJDetector()
    return detector.detect(text)


def mask_cnpj(cnpj: str, level: str = 'default') -> str:
    """
    Atalho funcional para CNPJDetector().mask(cnpj, level).

    Instancia um detector temporário e retorna o CNPJ mascarado.
    Use quando não precisar reutilizar o detector.
    """
    detector = CNPJDetector()
    return detector.mask(cnpj, level)
