"""
Classe principal de anonimização.
Integra todos os detectores para facilitar uso em DataFrames.
"""

import pandas as pd
from anonbr.detectors.cpf import DetectorCPF
from anonbr.detectors.email import DetectorEmail
from anonbr.detectors.telefone import DetectorTelefone

class Anonymizer:
    """
    Anonimizador principal que detecta e mascara dados sensíveis em DataFrames.
    Detecta automaticamente CPF, email e telefone em colunas e aplica
    mascaramento preservando formato original.
    """
    
    def __init__(self, nivel='padrao'):
        """
        Inicializa anonimizador com detectores.
        nivel: Nível de mascaramento ('padrao', 'alto', 'minimo')
        """
        self.nivel = nivel
        self.detector_cpf = DetectorCPF()
        self.detector_email = DetectorEmail()
        self.detector_telefone = DetectorTelefone()
    
    def _detectar_tipo_coluna(self, serie):
        """
        Detecta tipo de dado sensível na coluna.
        Exemplo: 'cpf', 'email', 'telefone' ou None
        """
        # Pegar primeira linha não-nula como amostra
        amostra = None
        for valor in serie:
            if pd.notna(valor):
                amostra = str(valor)
                break
        
        if amostra is None:
            return None
        
        # Testar cada detector
        if self.detector_cpf.detectar(amostra):
            return 'cpf'
        elif self.detector_email.detectar(amostra):
            return 'email'
        elif self.detector_telefone.detectar(amostra):
            return 'telefone'
        
        return None
    
    def _mascarar_valor(self, valor, tipo):
        # Mascara valor individual baseado no tipo. Returna o valor mascarado ou original se inválido
        if pd.isna(valor):
            return valor
        
        valor_str = str(valor)
        
        try:
            if tipo == 'cpf':
                return self.detector_cpf.mascarar(valor_str, nivel=self.nivel)
            elif tipo == 'email':
                return self.detector_email.mascarar(valor_str, nivel=self.nivel)
            elif tipo == 'telefone':
                return self.detector_telefone.mascarar(valor_str, nivel=self.nivel)
        except Exception:
            # Se mascaramento falhar, retorna original
            return valor
        
        return valor
    
    def anonimizar(self, df, colunas=None, inplace=False):
        """
        Anonimiza DataFrame detectando e mascarando dados sensíveis.
        Args:
            df: DataFrame pandas
            colunas: Lista de colunas para anonimizar (None = todas)
            inplace: Se True, modifica DataFrame original
        """
        if not inplace:
            df = df.copy()
        
        colunas_processar = colunas if colunas else df.columns
        
        for coluna in colunas_processar:
            if coluna not in df.columns:
                continue
            
            tipo = self._detectar_tipo_coluna(df[coluna])
            
            if tipo:
                df[coluna] = df[coluna].apply(
                    lambda x: self._mascarar_valor(x, tipo)
                )
        
        return df
    
    def relatorio(self, df):
        """
        Gera relatório de colunas com dados sensíveis detectados.
        Returna Dict com informações das colunas detectadas
        """
        resultado = {
            'cpf': [],
            'email': [],
            'telefone': []
        }
        
        for coluna in df.columns:
            tipo = self._detectar_tipo_coluna(df[coluna])
            if tipo:
                resultado[tipo].append(coluna)
        
        return resultado