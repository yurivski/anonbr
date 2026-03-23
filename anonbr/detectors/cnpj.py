# Copyright (C) 2026 Yuri Pontes
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Detecta e censura números de CNPJ em múltiplos formatos preservando a estrutura do documento.
"""
import re
from typing import Optional

class CNPJDetector:
    # Sistema de redundância de padrões regex
    formatted_pattern = [
        r'\b\d{2}\.\d{3}\.\d{3}\/\d{4}-\d{2}\b', # 12.345.678/0001-90
        r'\b\d{2}\.?\d{3}\.?\d{3}\/?\d{4}-?\d{2}\b', # 12345678/0001-90, 12.345.678/000190
        r'\b\d{2}[\s\.]*\d{3}[\s\.]*\d{3}[\s\/]*\d{4}[\s\-]*\d{2}\b', # 12 345 678 0001 90, 12 . 345 . 678 / 0001 - 90
        ] 
    unformatted_pattern = r'\b\d{14}\b' # 12345678000190

    def __init__(self):
        self.formatted_regex = re.compile('|'.join(self.formatted_pattern))
        self.unformatted_regex = re.compile(self.unformatted_pattern)

    # Detecta os padrões
    def detect(self, text: str) -> list:
        results = []

        for match in self.formatted_regex.finditer(text):
            if not self._overlaps_formatted(match, results):
                cnpj = match.group()
                results.append((cnpj, match.start(), match.end(), True))

        for match in self.unformatted_regex.finditer(text):
            if not self._overlaps_formatted(match, results):
                cnpj = match.group()
                results.append((cnpj, match.start(), match.end(), False))

        return results

    # verifica se match sobrepõe resultados já encontrados
    def _overlaps_formatted(self, match, formatted_results):
        start, end = match.start(), match.end()
        for _, f_start, f_end, _ in formatted_results:
            if not (end <= f_start or start >= f_end):
                return True
        return False

    # Aplica os níveis de censura
    def mask(self, cnpj: str, level: str = 'default') -> str:
        is_formatted = not bool(re.fullmatch(r'\d{14}', cnpj))
        digits = re.sub(r'\D', '', cnpj)
        # Nível 'high' censura todos os dígitos (14)
        if level == 'high':
            masked = 'X' * 14
        elif level == 'low':
            # Revela filial e dígitos verificadores (últimos 6)
            masked = 'X' * 8 + digits[8:14]
        else:
            # Padrão: revela os dígitos das posições 2–7, oculta prefixo e sufixo
            masked = 'X' * 2 + digits[2:8] + 'X' * 6
        if is_formatted:
            return f"{masked[:2]}.{masked[2:5]}.{masked[5:8]}/{masked[8:12]}-{masked[12:14]}"

        return masked
        
def detect_cnpj(text: str) -> list:
    # Helper function para detecção rápida
    detector = CNPJDetector()
    return detector.detect(text) 

def mask_cnpj(cnpj: str, level: str = 'default') -> str:
    # Helper function para mascaramento rápido.
    detector = CNPJDetector()
    return detector.mask(cnpj, level)