# Copyright (C) 2026 Yuri Pontes
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Detector e anonimizador de e-mail.

Detecta endereços de e-mail e mascara preservando informações de domínio
conforme o nível solicitado.

Fonte dos padrões regex: config/patterns.yaml -> chave 'email'
  - standard: padrão RFC-compatível para e-mails clássicos
"""

import re
from anonbr.pattern_loader import get_compiled_by_name


class EmailDetector:
    """
    Detecta e mascara endereços de e-mail em texto livre.

    O padrão regex é carregado automaticamente de config/patterns.yaml
    no momento da instanciação - não há string de regex hardcoded aqui.

    Atributo criado em __init__:
        regex - re.Pattern compilado com flag IGNORECASE para e-mails.
    """

    def __init__(self):
        # Carrega o padrão 'standard' do YAML e compila com IGNORECASE
        # para capturar e-mails em qualquer combinação de maiúsculas/minúsculas
        compiled = get_compiled_by_name('email')
        self.regex = re.compile(
            compiled['standard'].pattern,  # reutiliza a string já extraída do YAML
            re.IGNORECASE
        )

    def detect(self, text: str) -> list:
        """
        Busca todos os e-mails no texto e retorna uma lista de ocorrências.

        Parâmetro:
            text - string de texto onde a busca será realizada.

        Retorna:
            Lista de tuplas (email, inicio, fim):
                email - string do e-mail encontrado
                inicio - índice de início no texto
                fim - índice de fim no texto
        """
        results = []
        # Itera sobre todos os matches sem sobreposição (finditer garante isso)
        for match in self.regex.finditer(text):
            email = match.group()
            results.append((email, match.start(), match.end()))
        return results

    def mask(self, email: str, level: str = 'default') -> str:
        """
        Mascara um e-mail preservando a estrutura local@dominio.

        Anatomia do e-mail:
            local - parte antes do '@' (ex.: 'joaosilva')
            domínio - parte após o '@' (ex.: 'empresa.com.br')

        Níveis de mascaramento:
            'high' - xxxx@xxxxx.xxx (tudo oculto, incluindo domínio)
            'default' - jxxxxxxx@gmail.com (revela 1º caractere do local + domínio)
            'low' - xxxosilva@gmail.com (revela a metade final do local + domínio)

        Parâmetros:
            email - string do e-mail a mascarar.
            level - nível de mascaramento: 'high', 'default' ou 'low'.

        Retorna:
            E-mail mascarado. Se não contiver '@', retorna a string original.
        """
        if '@' not in email:
            # Sem '@' não é possível separar local de domínio, retorna intacto
            return email

        # Divide e-mail em parte local e domínio
        local, domain = email.split('@', 1)

        if level == 'high':
            # Mascara tanto o local quanto cada parte do domínio individualmente
            domain_parts = domain.split('.')
            masked_domain = '.'.join('x' * len(part) for part in domain_parts)
            masked_local = 'x' * len(local)
            return f"{masked_local}@{masked_domain}"

        elif level == 'low':
            # Revela a metade final do local (mínimo 1 caractere)
            reveal_count = max(len(local) // 2, 1)
            masked_local = 'x' * (len(local) - reveal_count) + local[-reveal_count:]
            return f"{masked_local}@{domain}"

        else:
            # Padrão: preserva apenas o primeiro caractere do local
            masked_local = local[0] + 'x' * (len(local) - 1)
            return f"{masked_local}@{domain}"


# Funções auxiliares
def detect_email(text: str) -> list:
    """
    Atalho funcional para EmailDetector().detect(text).

    Instancia um detector temporário e retorna as ocorrências de e-mail no texto.
    Use quando não precisar reutilizar o detector.
    """
    detector = EmailDetector()
    return detector.detect(text)


def mask_email(email: str, level: str = 'default') -> str:
    """
    Atalho funcional para EmailDetector().mask(email, level).

    Instancia um detector temporário e retorna o e-mail mascarado.
    Use quando não precisar reutilizar o detector.
    """
    detector = EmailDetector()
    return detector.mask(email, level)
