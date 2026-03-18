"""
Biblioteca Python para detectar e anonimizar os dados sensíveis (CPF, email, telefone).
"""

__version__ = '1.5.0'
__author__ = 'Yuri Pontes'
__license__ = 'MIT'

from anonbr.detectors.cpf import CPFDetector, detect_cpf, mask_cpf
from anonbr.detectors.email import EmailDetector, detect_email, mask_email
from anonbr.detectors.telefone import PhoneDetector, detect_phone, mask_phone
from anonbr.detectors.pdf import PDFDetector, detect_pdf, mask_pdf
from anonbr.anonymizer import Anonymizer

__all__ = [
    # Classe principal
    'Anonymizer',

    # Classes detectores
    'CPFDetector',
    'EmailDetector',
    'PhoneDetector',
    'PDFDetector',
    
    # Funções auxiliares - CPF
    'detect_cpf',
    'mask_cpf',
    
    # Funções auxiliares - Email
    'detect_email',
    'mask_email',
    
    # Funções auxiliares - Telefone
    'detect_phone',
    'mask_phone',
    
    # Funções auxiliares - PDF
    'detect_pdf',
    'mask_pdf',
]