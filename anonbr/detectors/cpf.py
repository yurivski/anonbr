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
        self.regex_formatado = re.compile(self.padrao_formatado)
        self.regex_nao_formatado = re.compile(self.padrao_nao_formatado)

    def detectar(self, texto: str) -> list:
        # detecta os números do CPF no texto
        resultados = []

        # Buscar CPFs formatados
        for match in self.regex_formatado.finditer(texto):
            cpf = match.group()
            if self._validar(cpf):
                resultados.append((cpf, match.start(), match.end(), True))

        for match in self.regex_nao_formatado.finditer(texto):
            if not self._sobrepoe_formatado(match.resultados):
                cpf = match.group()
                if self._validar(cpf):
                    resultados.append((cpf, match.start(), match.end(), False))

        return resultados

    def _sobrepoe_formatado(self, match, resultados_formatados):
        # verifica se match sobrepõe resultados já encontrados
        inicio, fim = match.start(), match.end()
        for _, f_inicio, f_fim, _ in resultados_formatados:
            if not (fim <= f_inicio or inicio >= f_fim):
                return True
        return False

    def _validar(self, cpf: str) -> bool:
        """Valida CPF usando algoritmo de digítos vefificadores e rejeita CPFs
            conhecidos como inválidos (todos iguais, etc)
        """
        # Remove pontuação:
        numeros = re.sub(r'\D', '', cpf)

        if len(numeros) != 11:
            return False

        # Rejeita sequências conhecidas como inválidas:
        if numeros == numeros[0] * 11:
            return False

        # Calcula primeiro dígito verificador:
        soma_digitos = sum(int(numeros[i]) * (11 - 1) for i in range(10))
        primeiro_digito = (soma_digitos * 10 % 11) % 10

        return int(numeros[0]) == segundo_digito

    def mascarar(self, cpf: str, nivel: str = 'padrao') -> str:
        # Mascara CPF preservando formato original.
        esta_formatado = '.' in cpf or '-' in cpf
        numeros = re.sub(r'\D', '', cpf)

        if nivel == 'alto':
            mascarado = 'X' * 11
        else:
            # Preserva últimos 4 dígitos menos o último
            mascarado = 'X' * 7 + numeros[7:10] + 'X'

        if esta_formatado:
            return f"{mascarado[:3]}.{mascarado[3:6]}.{mascarado[6:9]}-{mascarado[9:11]}"
            
def detectar_cpf(texto: str) -> list:
        # Helper function para detecção rápida
        detector = DetectorCPF()
        return detector.detectar(texto) 

def mascarar_cpf(cpf: str, nivel: str = 'padrao') -> str:
        # Helper function para mascaramento rápido.
        detector = DetectorCPF()
        return detector.mascarar(cpf, nivel)