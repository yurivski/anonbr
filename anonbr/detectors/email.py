"""
Detector e anonimizador de email.
Detecta endereços de email e mascara preservando informações de domínio
para teste.
"""

import re
from typing import Optional

class DetectorEmail:
    # Detecta e anonimiza endereços de email
    padrao = r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b'

    def __init__(self):
        self.regex = re.compile(self.padrao, re.IGNORECASE)

    def detectar(self, texto: str) -> list:
        # Detecta endereços de email no texto
        resultados = []
        for match in self.regex.finditer(texto):
            email = match.group()
            resultados.append((email, match.start(), match.end()))
        return resultados

    def mascarar(self, email: str, nivel: str = 'padrao') -> str:
        """
        Mascara email preservando estrutura.
        
        Níveis:
            alto:   xxxxxxxxx@xxxxx.xxx (tudo mascarado)
            padrao: jxxxxxxx@gmail.com (revela primeiro caractere do local)
            baixo:  xxxosilva@gmail.com (revela final do local)
        """
        if '@' not in email:
            return email

        local, dominio = email.split('@', 1)

        if nivel == 'alto':
            partes_dominio = dominio.split('.')
            dominio_mascarado = '.'.join('x'* len(parte) for parte in partes_dominio)
            local_mascarado = 'x' * len(local)
            return f"{local_mascarado}@{dominio_mascarado}"

        elif nivel == 'baixo':
            qtd_revelar = len(local) // 2
            if qtd_revelar == 0:
                qtd_revelar = 1
            local_mascarado = 'x' * (len(local) - qtd_revelar) + local[-qtd_revelar:]
            return f"{local_mascarado}@{dominio}"

        else:
            # Padrão: preserva o primeiro caractere
            local_mascarado = local[0] + 'x' * (len(local) - 1)
            return f"{local_mascarado}@{dominio}"

def detectar_email(texto: str) -> list:
    # Função auxiliar para detecção rápida
    detector = DetectorEmail()
    return detector.detectar(texto)

def mascarar_email(email: str, nivel: str = 'padrao') -> str:
    # Função auxiliar para mascaramento rápido
    detector = DetectorEmail()
    return detector.mascarar(email, nivel)
