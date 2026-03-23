# Copyright (C) 2026 Yuri Pontes
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Detectores de dados pessoais sensíveis.

Módulos disponíveis:
cpf: Detector de CPF (Cadastro de Pessoas Físicas)
email: Detector de endereços de email
telefone: Detector de telefones brasileiros
pdf: Faz a mesma coisa, mas em documentos PDF sem quebrar a estrutura
"""

from anonbr.detectors.cpf import CPFDetector
from anonbr.detectors.cnpj import CNPJDetector
from anonbr.detectors.email import EmailDetector
from anonbr.detectors.telefone import PhoneDetector
from anonbr.detectors.pdf import PDFDetector

__all__ = [
    'CPFDetector',
    'CNPJDetector',
    'EmailDetector',
    'PhoneDetector',
    'PDFDetector',
]