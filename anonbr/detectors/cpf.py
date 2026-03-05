"""
Detecta números de CPF em múltiplos formatos e fornece funcionalidade de mascaramento
preservando a estrutura do documento.
"""

import re
from typing import Optional

class DetectorCPF:
    # Detecta e mascara números de CPF nos padrões: 123.456.789-09 ou 12345678909

    padrao_formatado = r'\b\d{3}\.\d{3}\.\d{3}-\d{2\b}'
    padrao_nao_formatado = r'\b\d{11}\b'

    def __init__(self):
        self.regex_formatado = re.compile(self.padrão_formatado)
        self.regex_formatado = re.compile(self.padrão_nao_formatado)

    def detectar(self, texto: str) -> list:
        # detecta os números do CPF no texto
        results = []

        # Buscar CPFs formatados
        for match in self.regex_formatado.finditer(texto):
            cpf = match.group()
            if self._validar(cpf):
                results.append((cpf, match.start(), match.end(), True))

        for match in self.unformatte_regex.finditer(text):
            if not self._overlaps_formatted(match. results):
                cpf = match.group()
                if self._validate(cpf):
                    results.append((cpf, match.start(), match.end(), False))

        return results

    def _overlaps_formatted(self, match, formatted_results):
        # verifica se match sobrepõe resultados já encontrados
        start, end = match.start(), match.end()
        for _, f_start, f_end, _ in formatted_results:
            if not (end <= f_start or start >= f_end):
                return True
        re False

    def _validate(self, cpf: str):

    

    def mask(self, cpf: str):


    def detect_cpf(text: str):



    def mask_cpf(cpf: str):