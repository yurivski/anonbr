# Copyright (C) 2026 Yuri Pontes
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Detector e anonimizador de email.
Detecta endereços de email e mascara preservando informações de domínio
para teste.
"""

import re
from typing import Optional

class EmailDetector:
    # Detecta e anonimiza endereços de email
    pattern = r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b'

    def __init__(self):
        self.regex = re.compile(self.pattern, re.IGNORECASE)

    def detect(self, text: str) -> list:
        # Detecta endereços de email no texto
        results = []
        for match in self.regex.finditer(text):
            email = match.group()

            # Verificar se o email está dentro de uma URL
            block_start = match.start()
            while block_start > 0 and text[block_start -1] not in (' ', '\n', '\t'):
                block_start -= 1
            block_end = match.end()
            while block_end < len(text) and text[block_end] not in (' ', '\n', '\t'):
                block_end -= 1
            block = text[block_start:block_end]
            if '://' in block:
                continue

            results.append((email, match.start(), match.end()))
        return results

    def mask(self, email: str, level: str = 'default') -> str:
        """
        Mascara email preservando estrutura.
        
        Níveis:
            alto:   xxxxxxxxx@xxxxx.xxx (tudo mascarado)
            padrao: jxxxxxxx@gmail.com (revela primeiro caractere do local)
            baixo:  xxxosilva@gmail.com (revela final do local)
        """
        if '@' not in email:
            return email

        local, domain = email.split('@', 1)

        if level == 'high':
            domain_parts = domain.split('.')
            masked_domain = '.'.join('x' * len(part) for part in domain_parts)
            masked_local = 'x' * len(local)
            return f"{masked_local}@{masked_domain}"

        elif level == 'low':
            reveal_count = len(local) // 2
            if reveal_count == 0:
                reveal_count = 1
            masked_local = 'x' * (len(local) - reveal_count) + local[-reveal_count:]
            return f"{masked_local}@{domain}"

        else:
            # Padrão: preserva o primeiro caractere
            masked_local = local[0] + 'x' * (len(local) - 1)
            return f"{masked_local}@{domain}"

def detect_email(text: str) -> list:
    # Função auxiliar para detecção rápida
    detector = EmailDetector()
    return detector.detect(text)

def mask_email(email: str, level: str = 'default') -> str:
    # Função auxiliar para mascaramento rápido
    detector = EmailDetector()
    return detector.mask(email, level)