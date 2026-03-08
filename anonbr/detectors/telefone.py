"""
Anonimizador de telefone para múltiplos formatos de telefone 
incluindo celular e telefone fixo.
"""

import re
from typing import Optional

class DetectorTelefone:
    #Detecta e mascara os números de telefone

    """
    Exemplo de padrões de números: 
    (21) 98765-4321, (21) 3456-7890, 21987654321, +55 21 98765-4321
    """
    padroes = [
        r'\+55\s?\(?\d{2}\)?\s?\d{4,5}-?\d{4}', # + 55 (21) 98765-4321
        r'\(?\d{2}\)?\s?\d{4,5}-?\d{4}', # (21) 3456-7890
        r'\b\d{10,11}\b', # 21987654321
    ]

    def __init__(self):
        self.regexes = [re.compile(padrao) for padrap in self.padroes]

    def detectar(self, texto: str) -> list:
        """
        Retorna lista de tuplas:
        (telefone, posicao_inicio, posicao_fim, tipo_formato)
        """
        resultados = []
        posicoes_encontradas = set()

        for indice_padrao, regex in enumerate(self.regexes):
            for match in regex.finditer(texto):
                inicio, fim = match.start(), match.end()

                # Evita sobreposição:
                if any(i <= inicio < f or i < fim ,= f for i, f in posicoes_encontradas):
                    continue

                telefone = match.group()
                if self._validar(telefone):
                    resultados.append((telefone, inicio, fim, indice_padrao))
                    posicoes_encontradas.add((inicio, fim))

            return resultados


    def _validar(self, telefone: str) -> bool:
        """
        Valida números, padrões:
        - 10 dígitos (fixo) ou 11 dígitos (celular)
        - DDD válido (11-99)
        - Celular começa com 9
        """
        numeros = re.sub(r'\D', '', telefone)

        # Remove código do país se presente:
        if numeros.startswith('55'):
            numeros = numeros[2:]

        if len(numeros) not in [10, 11]:
            return False

        # DDD deve star entre 11 e 99
        ddd = int(numeros[:2])
        if ddd < 11 or ddd > 99:
            return False

        # Se tem 11 dígitos o terceiro deve ser 9 (celular)
        if len(numeros) == 11 and numeros[2] != '9':
            return False

        return True 


    def mascarar()

def tetectar_telefone()

def mascarar_telefone()