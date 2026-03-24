# Copyright (C) 2026 Yuri Pontes
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Detecta números de CPF em múltiplos formatos e fornece funcionalidade de mascaramento
preservando a estrutura do documento.
"""

import re
from typing import Optional

class CPFDetector:
    # Detecta e mascara números de CPF nos padrões: 123.456.789-09 ou 12345678909

    formatted_pattern = r'\b\d{3}[.\s\/-]?\d{3}[.\s\/-]?\d{3}[.\s\/-]?\d{2}\b'
    unformatted_pattern = r'\b\d{11}\b'

    def __init__(self):
        self.formatted_regex = re.compile(self.formatted_pattern)
        self.unformatted_regex = re.compile(self.unformatted_pattern)

    def detect(self, text: str) -> list:
        # detecta os números do CPF no texto
        results = []

        # Buscar CPFs formatados
        for match in self.formatted_regex.finditer(text):
            cpf = match.group()
            results.append((cpf, match.start(), match.end(), True))

        for match in self.unformatted_regex.finditer(text):
            if not self._overlaps_formatted(match, results):
                cpf = match.group()
                results.append((cpf, match.start(), match.end(), False))

        return results

    def _overlaps_formatted(self, match, formatted_results):
        # verifica se match sobrepõe resultados já encontrados
        start, end = match.start(), match.end()
        for _, f_start, f_end, _ in formatted_results:
            if not (end <= f_start or start >= f_end):
                return True
        return False

    def mask(self, cpf: str, level: str = 'default') -> str:
        """Mascara CPF preservando formato original.
            Níveis:
            alto:   XXX.XXX.XXX-XX (tudo mascarado)
            padrao: XXX.567.XXX-XX (revela meio)
            baixo:  XXX.XX9.567-01 (revela final)
        """
        digits = ''.join(re.findall(r'\d', cpf))
        is_formatted = bool(re.findall(r'[.\-]', cpf))

        if level == 'high':
            masked = 'X' * 11

        elif level == 'low':
            masked = 'X' * 6 + digits[6:11]
        else:
            # Padrão: revela meio
            masked = 'X' * 3 + digits[3:6] + 'X' * 5

        if is_formatted:
            return f"{masked[:3]}.{masked[3:6]}.{masked[6:9]}-{masked[9:11]}"
            
        return masked
        
def detect_cpf(text: str) -> list:
        # Helper function para detecção rápida
        detector = CPFDetector()
        return detector.detect(text) 

def mask_cpf(cpf: str, level: str = 'default') -> str:
        # Helper function para mascaramento rápido.
        detector = CPFDetector()
        return detector.mask(cpf, level)