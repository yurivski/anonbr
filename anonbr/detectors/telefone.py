# Copyright (C) 2026 Yuri Pontes
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Anonimizador de telefone para múltiplos formatos de telefone
incluindo celular e telefone fixo.

Fonte dos padrões regex: config/patterns.yaml  ->  chave 'telefone'
  Os padrões são carregados na ordem em que aparecem no YAML:
    [0] international - +55 (21) 98765-4321
    [1] with_nono_digit_space - (21) 9 8765-4321  (nono dígito separado por espaço)
    [2] with_ddd - (21) 98765-4321
    [3] only_numbers - 21987654321
    [4] short - 99876-5432 ou 9876-5432

  Sistema de redundância: padrões ordenados do mais específico ao mais genérico.
  Isso é necessário porque um número como '+55 (21) 98765-4321' também seria
  capturado pelo padrão [2] sem a etapa de deduplicação por posição.

  Esse 'sistema de redundância' também é uma solução temporária que encontrei para documentos
  antigos digitalizados em PDF. 
"""

import re
from anonbr.pattern_loader import get_compiled


class PhoneDetector:
    """
    Detecta e mascara números de telefone brasileiros em múltiplos formatos.

    Os padrões regex são carregados automaticamente de config/patterns.yaml
    na ordem exata definida no YAML, não há strings de regex hardcoded aqui.

    Atributo criado em __init__:
        regexes - lista de re.Pattern ordenada do padrão mais específico ao mais genérico 
        (ver índices na docstring do módulo acima).
    """

    def __init__(self):
        # Carrega a lista de padrões na ordem do YAML:
        self.regexes = get_compiled('telefone')

    def detect(self, text: str) -> list:
        """
        Busca todos os telefones no texto e retorna uma lista de ocorrências.

        Estratégia em duas etapas:

        Etapa 1 - varredura linear:
            Itera pelos padrões do mais específico ao mais genérico.
            Para cada match, verifica se a posição já foi registrada; se não,
            registra e marca as posições como usadas.

        Etapa 2 - varredura por segmentos (separador '/'):
            Telefones separados por '/' (ex.: '21987654321/21876543210')
            podem ser divididos na borda da barra e não serem capturados
            na etapa 1. Aqui o texto é dividido em partes e cada parte
            é varrida novamente, ajustando os índices pelo offset acumulado.

        Parâmetro:
            text - string de texto onde a busca será realizada.

        Retorna:
            Lista de tuplas (telefone, inicio, fim, indice_padrao):
                telefone - string do número encontrado
                inicio - índice de início no texto original
                fim - índice de fim no texto original
                indice_padrao - índice do padrão em self.regexes que fez o match
        """
        results = []
        # Conjunto de intervalos (inicio, fim) já registrados para evitar sobreposição
        found_positions = set()

        # Etapa 1: varredura linear
        for pattern_index, regex in enumerate(self.regexes):
            for match in regex.finditer(text):
                start, end = match.start(), match.end()

                # Pula se qualquer parte do intervalo já foi capturada
                if any(s <= start < e or s < end <= e for s, e in found_positions):
                    continue

                phone = match.group()
                results.append((phone, start, end, pattern_index))
                found_positions.add((start, end))

        # Etapa 2: varredura por segmentos divididos por '/'
        # Apenas os 3 primeiros padrões são usados aqui (mais específicos)
        phone_patterns = self.regexes[:3]
        parts = text.split('/')
        offset = 0

        for part in parts:
            # Cada padrão é testado dentro do segmento atual
            for regex in phone_patterns:
                for match in regex.finditer(part):
                    # Converte coordenadas do segmento para coordenadas do texto original
                    original_start = offset + match.start()
                    original_end = offset + match.end()

                    # Ignora posições já capturadas na etapa 1 ou em iterações anteriores
                    if any(s <= original_start < e or s < original_end <= e for s, e in found_positions):
                        continue

                    results.append((match.group(), original_start, original_end, 0))
                    found_positions.add((original_start, original_end))

            # Avança o offset: comprimento do segmento + 1 (pelo '/' removido no split)
            offset += len(part) + 1

        return results

    def _validate(self, phone: str) -> bool:
        """
        Valida se um número de telefone atende às regras brasileiras.

        Regras verificadas:
          - 10 dígitos (fixo com DDD) ou 11 dígitos (celular com DDD)
          - DDD deve estar entre 11 e 99
          - Celular (11 dígitos): terceiro dígito deve ser '9'

        Parâmetro:
            phone - string do telefone (pode conter formatação).

        Retorna:
            True se o número é válido, False caso contrário.
        """
        digits = re.sub(r'\D', '', phone)

        # Remove código do país se presente (ex.: +55 ou 55 antes dos 10/11 dígitos)
        if digits.startswith('55'):
            digits = digits[2:]

        if len(digits) not in [10, 11]:
            return False

        # DDD deve estar entre 11 e 99 (não existe DDD 10 ou abaixo)
        ddd = int(digits[:2])
        if ddd < 11 or ddd > 99:
            return False

        # Celular com 11 dígitos: o terceiro dígito obrigatoriamente é '9'
        if len(digits) == 11 and digits[2] != '9':
            return False

        return True

    def mask(self, phone: str, level: str = 'default') -> str:
        """
        Mascara um número de telefone preservando o formato original.

        Anatomia do número (após remover código do país):
            DDD - 2 primeiros dígitos (ex.: 21)
            restante - dígitos do número local (8 ou 9 dígitos)

        Níveis de mascaramento:
            'high' -> +XX (XX) XXXXX-XXXX  (tudo oculto, inclusive DDD)
            'default' -> +55 (21) XXXXX-5678  (revela DDD + últimos 4 dígitos)
            'low' -> +55 (21) XXXX2-3456  (revela DDD + últimos 5 dígitos)

        Parâmetros:
            phone - string do telefone (pode conter formatação: +, (), -, espaços).
            level - nível de mascaramento: 'high', 'default' ou 'low'.

        Retorna:
            Telefone mascarado no mesmo formato de entrada
            (com parênteses se o original tinha, com '+55' se tinha código do país etc.).
        """
        original = phone
        digits = re.sub(r'\D', '', phone)

        # Detecta e remove código do país para processar apenas DDD + número local
        if digits.startswith('55') and len(digits) > 11:
            has_country_code = True
            digits = digits[2:]  # descarta '55', mantém DDD + número
        else:
            has_country_code = False

        ddd = digits[:2] # ex.: '21'
        remainder = digits[2:] # ex.: '987654321'

        if level == 'high':
            # Mascara DDD e todos os dígitos do número
            ddd_masked = 'XX'
            masked = 'X' * len(remainder)

        elif level == 'low':
            # Mantém DDD real, revela os 5 últimos dígitos
            ddd_masked = ddd
            reveal_count = min(5, len(remainder))
            masked = 'X' * (len(remainder) - reveal_count) + remainder[-reveal_count:]

        else:
            # Padrão: mantém DDD real, revela os 4 últimos dígitos
            ddd_masked = ddd
            reveal_count = min(4, len(remainder))
            masked = 'X' * (len(remainder) - reveal_count) + remainder[-reveal_count:]

        # Reconstrói o formato original 
        if '(' in original or '-' in original:
            # Formato com parênteses/hífen: (DDD) NNNNN-NNNN
            if len(remainder) == 9:
                # Celular: 5 dígitos + hífen + 4 dígitos
                formatted = f"({ddd_masked}) {masked[:5]}-{masked[5:]}"
            else:
                # Fixo: 4 dígitos + hífen + 4 dígitos
                formatted = f"({ddd_masked}) {masked[:5]}-{masked[4:]}"

            if has_country_code:
                # Recoloca prefixo internacional
                formatted = f"+{'XX' if level == 'high' else '55'} {formatted}"
            return formatted

        else:
            # Formato sem parênteses/hífen: apenas dígitos concatenados
            prefix = ('XX' if level == 'high' else '55') if has_country_code else ''
            return prefix + ddd_masked + masked


# Funções auxiliares 
def detect_phone(text: str) -> list:
    """
    Atalho funcional para PhoneDetector().detect(text).

    Instancia um detector temporário e retorna as ocorrências de telefone no texto.
    Use quando não precisar reutilizar o detector.
    """
    detector = PhoneDetector()
    return detector.detect(text)


def mask_phone(phone: str, level: str = 'default') -> str:
    """
    Atalho funcional para PhoneDetector().mask(phone, level).

    Instancia um detector temporário e retorna o telefone mascarado.
    Use quando não precisar reutilizar o detector.
    """
    detector = PhoneDetector()
    return detector.mask(phone, level)
