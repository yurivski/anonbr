# Copyright (C) 2026 Yuri Pontes
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

"""
Biblioteca Python para detectar e anonimizar os dados sensíveis (CPF, email, telefone).
"""

__version__ = '1.2.0'
__author__ = 'Yuri Pontes'
__license__ = 'AGPL-3.0'

from anonbr.detectors.cpf import CPFDetector, detect_cpf, mask_cpf
from anonbr.detectors.cnpj import CNPJDetector, detect_cnpj, mask_cnpj
from anonbr.detectors.email import EmailDetector, detect_email, mask_email
from anonbr.detectors.telefone import PhoneDetector, detect_phone, mask_phone
from anonbr.detectors.pdf import PDFDetector, detect_pdf, mask_pdf
from anonbr.anonymizer import Anonymizer

__all__ = [
    # Classe principal
    'Anonymizer',

    # Classes detectores
    'CPFDetector',
    'CNPJDetector',
    'EmailDetector',
    'PhoneDetector',
    'PDFDetector',
    
    # Funções auxiliares - CPF
    'detect_cpf',
    'mask_cpf',

    # Funções auxiliares - CNPJ
    'detect_cnpj',
    'mask_cnpj',

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