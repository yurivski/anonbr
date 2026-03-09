"""
Biblioteca Python para detectar e anonimizar os dados sensíveis (CPF, email, telefone).

Exemplo de uso:
    >>> from anonbr import Anonymizer
    >>> import pandas as pd
    >>> 
    >>> df = pd.read_csv('dados.csv')
    >>> anonimizador = Anonymizer()
    >>> df_anonimizado = anonimizador.anonimizar(df)

Para mais informações: https://github.com/yurivski/anonbr
"""

__version__ = '1.0'
__author__ = 'Yuri Pontes'
__license__ = 'MIT'

from anonbr.detectors.cpf import DetectorCPF, detectar_cpf, mascarar_cpf
from anonbr.detectors.email import DetectorEmail, detectar_email, mascarar_email
from anonbr.detectors.telefone import DetectorTelefone, detectar_telefone, mascarar_telefone
from anonbr.anonymizer import Anonymizer

__all__ = [
    # Classe principal
    'Anonymizer',

    # Classes detectores
    'DetectorCPF',
    'DetectorEmail',
    'DetectorTelefone',
    
    # Funções auxiliares - CPF
    'detectar_cpf',
    'mascarar_cpf',
    
    # Funções auxiliares - Email
    'detectar_email',
    'mascarar_email',
    
    # Funções auxiliares - Telefone
    'detectar_telefone',
    'mascarar_telefone',
]