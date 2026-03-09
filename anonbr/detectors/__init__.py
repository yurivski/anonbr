"""
Detectores de dados pessoais sensíveis.

Módulos disponíveis:
cpf: Detector de CPF (Cadastro de Pessoas Físicas)
email: Detector de endereços de email
telefone: Detector de telefones brasileiros
"""

from anonbr.detectors.cpf import DetectorCPF
from anonbr.detectors.email import DetectorEmail
from anonbr.detectors.telefone import DetectorTelefone

__all__ = [
    'DetectorCPF',
    'DetectorEmail',
    'DetectorTelefone',
]