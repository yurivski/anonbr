"""
Detecta números de CPF em múltiplos formatos e fornece funcionalidade de mascaramento
preservando a estrutura do documento.
"""

import re
from typing import Optional

class DetectorCPF:
    # Detecta e mascara números de CPF nos padrões: 123.456.789-09 ou 12345678909

    padrao_formatado = r'\b\d{3}\.\d{3}\.\d{3}-\d{2}\b'
    padrao_nao_formatado = r'\b\d{11}\b'

    def __init__(self):
        self.regex_formatado = re.compile(self.padrao_formatado)
        self.regex_nao_formatado = re.compile(self.padrao_nao_formatado)

    def detectar(self, texto: str) -> list:
        # detecta os números do CPF no texto
        resultados = []

        # Buscar CPFs formatados
        for match in self.regex_formatado.finditer(texto):
            cpf = match.group()
            resultados.append((cpf, match.start(), match.end(), True))

        for match in self.regex_nao_formatado.finditer(texto):
            if not self._sobrepoe_formatado(match, resultados):
                cpf = match.group()
                resultados.append((cpf, match.start(), match.end(), False))

        return resultados

    def _sobrepoe_formatado(self, match, resultados_formatados):
        # verifica se match sobrepõe resultados já encontrados
        inicio, fim = match.start(), match.end()
        for _, f_inicio, f_fim, _ in resultados_formatados:
            if not (fim <= f_inicio or inicio >= f_fim):
                return True
        return False

    def mascarar(self, cpf: str, nivel: str = 'padrao') -> str:
        """Mascara CPF preservando formato original.
            Níveis:
            alto:   XXX.XXX.XXX-XX (tudo mascarado)
            padrao: XXX.567.XXX-XX (revela meio)
            baixo:  XXX.XX9.567-01 (revela final)
        """
        esta_formatado = '.' in cpf or '-' in cpf
        numeros = re.sub(r'\D', '', cpf)

        if nivel == 'alto':
            mascarado = 'X' * 11

        elif nivel == 'baixo':
            mascarado = 'X' * 6 + numeros[6:11]
        else:
            # Padrão: revela meio
            mascarado = 'X' * 3 + numeros[3:6] + 'X' * 5

        if esta_formatado:
            return f"{mascarado[:3]}.{mascarado[3:6]}.{mascarado[6:9]}-{mascarado[9:11]}"
            
        return mascarado
        
def detectar_cpf(texto: str) -> list:
        # Helper function para detecção rápida
        detector = DetectorCPF()
        return detector.detectar(texto) 

def mascarar_cpf(cpf: str, nivel: str = 'padrao') -> str:
        # Helper function para mascaramento rápido.
        detector = DetectorCPF()
        return detector.mascarar(cpf, nivel)