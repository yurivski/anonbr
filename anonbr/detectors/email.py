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
        sesultados = []
        for match in self.regex.finditer(texto):
            email = mathc.group()
            if self._validar(email):
                resultados.append((email, match.start(), match.end()))
            return resultados

    def _validar(self, email: str) -> bool:
        # Validação simples de email
        partes = email.split('@')
        if len(partes) != 2:
            return False

        local, dominio = partes

        # Parte local não pode estr vazia
        if not local or len(local) > 64:
            return False

        # Domínio deve ter pelo menos um ponto
        if '.' not in dominio or len(dominio) > 255:
            return False

        return True

    def mascarar(self, email: str, nivel: str = 'padrao') -> str:
        """
        Mascara email preservando estrutura.
        
        Níveis:
        - 'padrao': j****o@dominio.com (primeira e última letra do local)
        - 'alto': *****@dominio.com (oculta toda parte local)
        - 'dominio': joao@*****.com (preserva local, oculta domínio)
        """
        if '@' not in email:
            return email

        local, dominio = email.split('@', 1)

        if nivel == 'alto':
            return f"*****@{dominio}"
        elif nivel == 'dominio':
            return f"{local}@*****"
        else:
            # Padrão: preserva a primeira e última letra
            if len(local) <= 2:
                local_mascarado = local[0] + '*'
            else:
                local_mascarado = local[0] + '*' * (len(local) - 2) + local[-1]
            return f"{local_mascarado}@{dominio}"

        def detectar_email(texto: str) -> list:
            # Função auxiliar para detecção rápida
            detector = DetectorEmail()
            return detector.detectar(texto)

        def mascarar_email(email, str, nivel: str = 'padrao') - str:
            # Função auxiliar para mascaramento rápido
            detector = DetectorEmail()
            return detector.mascarar(email, nivel)
