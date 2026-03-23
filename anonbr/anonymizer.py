# Copyright (C) 2026 Yuri Pontes
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Classe principal de anonimização.
Integra todos os detectores para facilitar uso em DataFrames.
"""

import pandas as pd
import warnings
from anonbr.detectors.cpf import CPFDetector
from anonbr.detectors.cnpj import CNPJDetector
from anonbr.detectors.email import EmailDetector
from anonbr.detectors.telefone import PhoneDetector

class Anonymizer:
    """
    Anonimizador principal que detecta e mascara dados sensíveis em DataFrames.
    Detecta automaticamente CPF, email e telefone em colunas e aplica
    mascaramento preservando formato original.
    """
    def __init__(self, level='default', sample_size=5):
        """
        Inicializa anonimizador com detectores.
        nivel: Nível de mascaramento ('default', 'high', 'low')
        """
        self.level = level
        self.sample_size = sample_size
        self.cpf_detector = CPFDetector()
        self.cnpj_detector = CNPJDetector()
        self.email_detector = EmailDetector()
        self.phone_detector = PhoneDetector()
    
    def _detect_column_type(self, series):
        """
        Detecta tipo de dado sensível na coluna por votação de amostra.
        Usa múltiplos valores e usa votação por maioria.
        """
        samples = (
            series.dropna()
                .astype(str)
                .head(self.sample_size)
                .tolist()
        )

        if not samples:
            return None

        detectors = {
            'cpf':   self.cpf_detector.detect,
            'cnpj':  self.cnpj_detector.detect,
            'email': self.email_detector.detect,
            'phone': self.phone_detector.detect,
        }

        votes = {dtype: 0 for dtype in detectors}

        for sample in samples:
            for dtype, detect_fn in detectors.items():
                if detect_fn(sample):
                    votes[dtype] += 1
                    break  # cada amostra vota em um único tipo

        best_type, best_count = max(votes.items(), key=lambda x: x[1])

        return best_type if best_count > 0 else None
    
    def _mask_value(self, value, data_type):
        # Mascara valor individual baseado no tipo. Retorna o valor mascarado ou original se inválido
        if pd.isna(value):
            return value
        
        value_str = str(value)
        
        try:
            if data_type == 'cpf':
                return self.cpf_detector.mask(value_str, level=self.level)
            elif data_type == 'cnpj':
                return self.cnpj_detector.mask(value_str, level=self.level)
            elif data_type == 'email':
                return self.email_detector.mask(value_str, level=self.level)
            elif data_type == 'phone':
                return self.phone_detector.mask(value_str, level=self.level)
        except Exception as e:
            # Se mascaramento falhar, retorna original
            warnings.warn(
                f"[anonbr] Falha ao mascarar valor do tipo '{data_type}': "
                f"'{value_str}' → {type(e).__name__}: {e}",
                stacklevel=2
            )
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
            'cnpj': [],
            'email': [],
            'phone': []
        }
        
        for column in df.columns:
            data_type = self._detect_column_type(df[column])
            if data_type:
                result[data_type].append(column)
        
        return result