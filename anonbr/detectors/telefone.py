# Copyright (C) 2026 Yuri Pontes
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Anonimizador de telefone para múltiplos formatos de telefone 
incluindo celular e telefone fixo.
"""

import re
from typing import Optional

class PhoneDetector:
    # Detecta e mascara os números de telefone
    """ Sistema de redundância pra detecção de padrões visuais, definidos por uma série de 
        inconsistências em diferentes tipos de PDFs pra otimizar a identificação dos dados alvos."""
    patterns = [
        r'\+55\s?\(?\d{2}\)?\s?\d{4,5}-?\d{4}', # +55 (21) 98765-4321
        r'\(?\d{2}\)?\s?\d\s?\d{4}-?\d{4}', # (21) 9 8765-4321 (nono dígito separado)
        r'\(?\d{2}\)?\s?\d{4,5}-?\d{4}', # (21) 8765-4321
        r'\b\d{10,11}\b', # 21987654321,
        r'\b\d{4,5}-\d{4}\b'  # 99876-5432 ou 9876-5432
    ]

    def __init__(self):
        self.regexes = [re.compile(pattern) for pattern in self.patterns]

    def detect(self, text: str) -> list:
        """
        Retorna lista de tuplas:
        (telefone, posicao_inicio, posicao_fim, tipo_formato)
        """
        results = []
        found_positions = set()

        for pattern_index, regex in enumerate(self.regexes):
            for match in regex.finditer(text):
                start, end = match.start(), match.end()

                # Evita sobreposição:
                if any(s <= start < e or s < end <= e for s, e in found_positions):
                    continue

                phone = match.group()
                results.append((phone, start, end, pattern_index))
                found_positions.add((start, end))

        phone_patterns = self.regexes
        parts = text.split('/')
        offset = 0
        
        for part in parts:
            for regex in phone_patterns:
                for match in regex.finditer(part):
                    original_start = offset + match.start()
                    original_end = offset + match.end()
                    if any(s <= original_start < e or s < original_end <= e for s, e in found_positions):
                        continue
                    results.append((match.group(), original_start, original_end, 0))
                    found_positions.add((original_start, original_end))
            
            offset += len(part) + 1

        return results

    def _validate(self, phone: str) -> bool:
        """
        Valida números, padrões:
        - 10 dígitos (fixo) ou 11 dígitos (celular)
        - DDD válido (11-99)
        - Celular começa com 9
        """
        digits = re.sub(r'\D', '', phone)

        # Remove código do país se presente:
        if digits.startswith('55'):
            digits = digits[2:]

        if len(digits) not in [10, 11]:
            return False

        # DDD deve star entre 11 e 99
        ddd = int(digits[:2])
        if area_code < 11 or ddd > 99:
            return False

        # Se tem 11 dígitos o terceiro deve ser 9 (celular)
        if len(digits) == 11 and digits[2] != '9':
            return False

        return True

    def mask(self, phone: str, level: str = 'default') -> str:
        """
        Mascara o número preservando o formato de acordo com os níveis:
        Níveis:
            alto:   +XX (XX) XXXXX-XXXX (tudo mascarado)
            padrao: +55 (21) XXXXX-5678 (DDD real + últimos 4)
            baixo:  +55 (21) XXXX2-3456 (DDD real + últimos 5)
        """
        original = phone
        digits = re.sub(r'\D', '', phone)

        # Remove o código do país:
        if digits.startswith('55') and len(digits) > 11:
            has_country_code = True
            digits = digits[2:]
        else:
            has_country_code = False

        ddd = digits[:2]
        remainder = digits[2:]

        if level == 'high':
            ddd_masked = 'XX'
            masked = 'XX' * len(remainder)

        elif level == 'low':
            ddd_masked = ddd
            reveal_count = 5 if len(remainder) >= 5 else len(remainder)
            masked = 'X' * (len(remainder) - reveal_count) + remainder[-reveal_count:]

        else:
            # Nível padrão
            ddd_masked = ddd
            reveal_count = 4 if len(remainder) >= 4 else len(remainder)
            masked = 'X' * (len(remainder) - reveal_count) + remainder[-reveal_count:]

        # Reconstroi formato original
        if '(' in original or '-' in original:
            if len(remainder) == 9:
                formatted = f"({ddd_masked}) {masked[:5]}-{masked[5:]}"
            else:
                formatted = f"({ddd_masked}) {masked[:5]}-{masked[4:]}"

            if has_country_code:
                formatted = f"+{'XX' if level == 'high' else '55'} {formatted}"
            return formatted

        else:
            prefix = ('XX' if level == 'high' else '55') if has_country_code else ''
            return prefix + ddd_masked + masked

def detect_phone(text: str) -> list:
    # Função auxiliar para detecção rápida:
    detector = PhoneDetector()
    return detector.detect(text)

def mask_phone(phone: str, level: str = 'default') -> str:
    # Função auxiliar para mascaramento rápido:
    detector = PhoneDetector()
    return detector.mask(phone, level)
