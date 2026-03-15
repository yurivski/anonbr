"""
Classe principal de anonimização.
Integra todos os detectores para facilitar uso em DataFrames.
"""

import pandas as pd
from anonbr.detectors.cpf import CPFDetector
from anonbr.detectors.email import EmailDetector
from anonbr.detectors.telefone import PhoneDetector

class Anonymizer:
    """
    Anonimizador principal que detecta e mascara dados sensíveis em DataFrames.
    Detecta automaticamente CPF, email e telefone em colunas e aplica
    mascaramento preservando formato original.
    """
    
    def __init__(self, level='default'):
        """
        Inicializa anonimizador com detectores.
        nivel: Nível de mascaramento ('padrao', 'alto', 'baixo')
        """
        self.level = level
        self.cpf_detector = CPFDetector()
        self.email_detector = EmailDetector()
        self.phone_detector = PhoneDetector()
    
    def _detect_column_type(self, series):
        """
        Detecta tipo de dado sensível na coluna.
        Exemplo: 'cpf', 'email', 'telefone' ou None
        """
        # Pegar primeira linha não-nula como amostra
        sample = None
        for value in series:
            if pd.notna(value):
                sample = str(value)
                break
        
        if sample is None:
            return None
        
        # Testar cada detector
        if self.cpf_detector.detect(sample):
            return 'cpf'
        elif self.email_detector.detect(sample):
            return 'email'
        elif self.phone_detector.detect(sample):
            return 'phone'
        
        return None
    
    def _mask_value(self, value, data_type):
        # Mascara valor individual baseado no tipo. Retorna o valor mascarado ou original se inválido
        if pd.isna(value):
            return value
        
        value_str = str(value)
        
        try:
            if data_type == 'cpf':
                return self.cpf_detector.mask(value_str, level=self.level)
            elif data_type == 'email':
                return self.email_detector.mask(value_str, level=self.level)
            elif data_type == 'phone':
                return self.phone_detector.mask(value_str, level=self.level)
        except Exception:
            # Se mascaramento falhar, retorna original
            return value
        
        return value
    
    def anonymize(self, df, columns=None, inplace=False):
        """
        Anonimiza DataFrame detectando e mascarando dados sensíveis.
        colunas: Lista de colunas para anonimizar (None = todas)
        inplace: Se True, modifica DataFrame original
        """
        if not inplace:
            df = df.copy()
        
        columns_to_process = columns if columns else df.columns
        
        for column in columns_to_process:
            if column not in df.columns:
                continue
            
            data_type = self._detect_column_type(df[column])
            
            if data_type:
                df[column] = df[column].apply(
                    lambda x: self._mask_value(x, data_type)
                )
        
        return df
    
    def report(self, df):
        """
        Gera relatório de colunas com dados sensíveis detectados.
        Retorna Dict com informações das colunas detectadas
        """
        result = {
            'cpf': [],
            'email': [],
            'phone': []
        }
        
        for column in df.columns:
            data_type = self._detect_column_type(df[column])
            if data_type:
                result[data_type].append(column)
        
        return result