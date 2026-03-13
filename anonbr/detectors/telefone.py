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
        self.regexes = [re.compile(padrao) for padrao in self.padroes]

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
                if any(i <= inicio < f or i < fim <= f for i, f in posicoes_encontradas):
                    continue

                telefone = match.group()
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


    def mascarar(self, telefone: str, nivel: str = 'padrao') -> str:
        """
        Mascara o número preservando o formato de acordo com os níveis:
        Níveis:
            alto:   +XX (XX) XXXXX-XXXX (tudo mascarado)
            padrao: +55 (21) XXXXX-5678 (DDD real + últimos 4)
            baixo:  +55 (21) XXXX2-3456 (DDD real + últimos 5)
        """
        original = telefone
        numeros = re.sub(r'\D', '', telefone)

        # Remove o código do país:
        if numeros.startswith('55') and len(numeros) > 11:
            tem_codigo_pais = True
            numeros = numeros[2:]
        else:
            tem_codigo_pais = False

        ddd = numeros[:2]
        resto = numeros[2:]

        if nivel == 'alto':
            ddd_mascarado = 'XX'
            mascarado = 'XX' * len(resto)

        elif nivel == 'baixo':
            ddd_mascarado = ddd
            qtd_revelar = 5 if len(resto) >= 5 else len(resto)
            mascarado = 'X' * (len(resto) - qtd_revelar) + resto[-qtd_revelar:]
        
        else:
            # Nível padrão
            ddd_mascarado = ddd 
            qtd_revelar = 4 if len(resto) >= 4 else len(resto)
            mascarado = 'X' * (len(resto) - qtd_revelar) + resto[-qtd_revelar:]
        
        # Reconstroi formato original
        if '(' in original or '-' in original:
            if len(resto) == 9:
                formatado = f"({ddd_mascarado}) {mascarado[:5]}-{mascarado[5:]}"
            else:
                formatado = f"({ddd_mascarado}) {mascarado[:5]}-{mascarado[4:]}"
            
            if tem_codigo_pais:
                formatado = f"+{'XX' if nivel == 'alto' else '55'} {formatado}"
            return formatado

        else:
            prefixo = ('XX' if nivel == 'alto' else '55') if tem_codigo_pais else ''
            return prefixo + ddd_mascarado + mascarado
            
def detectar_telefone(texto: str) -> list:
    # Função auxiliar para detecção rápida:
    detector = DetectorTelefone()
    return detector.detectar(texto)

def mascarar_telefone(telefone: str, nivel: str = 'padrao') -> str:
    # Função auxiliar para mascaramento rápido:
    detector = DetectorTelefone()
    return detector.mascarar(telefone, nivel)
