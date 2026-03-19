# Copyright (C) 2026 Yuri Pontes
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Detectores de dados pessoais sensíveis.

Módulos disponíveis:
cpf: Detector de CPF (Cadastro de Pessoas Físicas)
email: Detector de endereços de email
telefone: Detector de telefones brasileiros
"""

from anonbr.detectors.cpf import CPFDetector
from anonbr.detectors.email import EmailDetector
from anonbr.detectors.telefone import PhoneDetector

__all__ = [
    'CPFDetector',
    'EmailDetector',
    'PhoneDetector',
]