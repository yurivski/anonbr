"""
Detecta e mascara dados sensíveis (CPF, email, telefone) em arquivos PDF.
"""

import re
import os
import fitz  # pymupdf
import pdfplumber

from anonbr.detectors.cpf import CPFDetector
from anonbr.detectors.email import EmailDetector
from anonbr.detectors.telefone import PhoneDetector


class PDFDetector:
    """
    Detecta e mascara padrões de CPF, email e telefone em documentos PDF.
    Usa posicionamento em nível de caractere pra desenhar barras pretas
    apenas sobre os caracteres exatos que precisam ser mascarados.
    """

    def __init__(self, level='default'):
        self.level = level
        self.detect_cpf = CPFDetector()
        self.detect_email = EmailDetector()
        self.detect_phone = PhoneDetector()

    @property
    def patterns(self):
        # Importa padrões regex dos detectores existentes
        return {
            'cpf_formatted': self.detect_cpf.formatted_regex,
            'cpf_unformatted': self.detect_cpf.unformatted_regex,
            'email': self.detect_email.regex,
            'phone_international': self.detect_phone.regexes[0],
            'phone_ddd': self.detect_phone.regexes[1],
            'phone_digits': self.detect_phone.regexes[2],
        }

    def _extract_text_with_mapping(self, chars):
        """Reconstrói texto com quebras de linha e mapeia índice do texto pro índice do chars."""
        if not chars:
            return '', {}
        
        text = ''
        text_to_char = {}  # {índice_no_texto: índice_no_chars}
        char_idx = 0
        last_top = chars[0]['top']
        
        for c in chars:
            if abs(c['top'] - last_top) > 2:
                text += '\n'
                # \n não mapeia pra nenhum char
                last_top = c['top']
            text_to_char[len(text)] = char_idx
            text += c['text']
            char_idx += 1
        
        return text, text_to_char

    # Detecção
    def detect(self, pdf_path: str) -> dict:
        """
        Lê um PDF e detecta todos os padrões de dados sensíveis e retorna dict 
        com as ocorrências por página.
        """
        findings = {}

        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                chars = page.chars
                if not chars:
                    continue

                # Construir texto a partir dos caracteres com quebras de linha
                page_text = self._extract_text_with_newlines(chars)

                detections = self._detect_in_text(page_text)

                if detections:
                    findings[page_num] = [
                        {'type': dt, 'text': mt, 'start': s, 'end': e}
                        for dt, mt, s, e in detections
                    ]

        return findings

    def _detect_in_text(self, text: str) -> list:
        """
        Detecta todos os padrões sensíveis em uma string de texto.
        Padrões mais específicos têm prioridade sobre os genéricos.
        """
        detections = []
        used_positions = set()

        pattern_order = [
            ('cpf', 'cpf_formatted'),
            ('cpf', 'cpf_unformatted'),
            ('email', 'email'),
            ('phone', 'phone_international'),
            ('phone', 'phone_ddd'),
            ('phone', 'phone_digits'),
        ]

        for data_type, pattern_name in pattern_order:
            regex = self.patterns[pattern_name]

            for match in regex.finditer(text):
                start, end = match.start(), match.end()

                if any(pos in used_positions for pos in range(start, end)):
                    continue

                detections.append((data_type, match.group(), start, end))

                for pos in range(start, end):
                    used_positions.add(pos)

        return detections

    # Mascaramento
    def mask(self, pdf_path: str, output_path: str) -> dict:
        """
        Lê um PDF, detecta dados sensíveis, desenha barras pretas sobre os caracteres 
        que devem ser mascarados e salva o resultado.
        """
        summary = {'cpf': 0, 'email': 0, 'phone': 0, 'pages_processed': 0}

        # pdfplumber detecta caracteres e constrói mapa de mascaramento
        mask_map = self._build_mask_map(pdf_path, summary)

        if not mask_map:
            doc = fitz.open(pdf_path)
            doc.save(output_path)
            doc.close()
            return summary

        # pymupdf desenha barras pretas sobre os caracteres mascarados
        doc = fitz.open(pdf_path)

        for page_num, bars in mask_map.items():
            page = doc[page_num]

            # Apaga o texto original permanentemente
            for bar in bars:
                rect = fitz.Rect(bar['x0'], bar['top'], bar['x1'], bar['bottom'])
                page.add_redact_annot(
                    rect,
                    text='X',
                    fontname="helv",
                    fontsize=1,
                    fill=(1, 1, 1),
                    text_color=(1, 1, 1),  # Texto branco (invisível)
                )

            page.apply_redactions()

            # Desenha tarjas pretas por cima
            for bar in bars:
                rect = fitz.Rect(bar['x0'], bar['top'], bar['x1'], bar['bottom'])
                page.draw_rect(rect, color=(0, 0, 0), fill=(0, 0, 0))

            summary['pages_processed'] += 1

        doc.save(output_path)
        doc.close()

        return summary

    def _build_mask_map(self, pdf_path: str, summary: dict) -> dict:
        """
        Constrói um mapa de quais caracteres cobrir com barras pretas.
        Retorna {num_pagina: [{'x0', 'top', 'x1', 'bottom'}, ...]}
        """
        mask_map = {}

        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                chars = page.chars
                if not chars:
                    continue

                # Construir texto a partir dos caracteres com quebras de linha
                page_text, text_to_char = self._extract_text_with_mapping(chars)

                # Detectar padrões
                detections = self._detect_in_text(page_text)
                if not detections:
                    continue

                # Determinar quais índices de caractere mascarar
                chars_to_mask = self._get_chars_to_mask(page_text, detections)

                # Construir posições das barras a partir das bounding boxes dos caracteres
                page_bars = []
                for text_idx in sorted(chars_to_mask.keys()):
                    if text_idx in text_to_char:
                        char_idx = text_to_char[text_idx]
                        if char_idx < len(chars):
                            c = chars[char_idx]
                            page_bars.append({
                                'x0': c['x0'],
                                'top': c['top'],
                                'x1': c['x1'],
                                'bottom': c['bottom'],
                            })

                if page_bars:
                    mask_map[page_num] = page_bars

                # Contar detecções
                for data_type, _, _, _ in detections:
                    summary[data_type] += 1

        return mask_map

    def _get_chars_to_mask(self, text: str, detections: list) -> dict:
        """
        Determina quais índices de caractere devem ser mascarados e retorna 
        {indice_caractere: tipo_dado} pra caracteres a cobrir com barras.
        """
        chars_to_mask = {}

        for data_type, matched_text, start, end in detections:
            mask_pattern = self._get_mask_pattern(data_type, matched_text)

            for i, mask_char in enumerate(mask_pattern):
                char_idx = start + i
                if mask_char == 'X':
                    chars_to_mask[char_idx] = data_type

        return chars_to_mask

    def _get_mask_pattern(self, data_type: str, value: str) -> str:
        """
        Retorna uma string de padrão com o mesmo comprimento do valor.
        'X' = mascarar este caractere (desenhar barra preta).
        Qualquer outro caractere = manter visível (sem barra).
        """
        if data_type == 'cpf':
            return self._cpf_mask_pattern(value)
        elif data_type == 'email':
            return self._email_mask_pattern(value)
        elif data_type == 'phone':
            return self._phone_mask_pattern(value)
        return 'X' * len(value)

    # Padrão de mascaramento de CPF
    def _cpf_mask_pattern(self, cpf: str) -> str:
        """
        high:    XXX.XXX.XXX-XX (todos os dígitos mascarados)
        default: XXX.096.XXX-XX (meio revelado)
        low:     XXX.XX6.646-08 (final revelado)
        """
        is_formatted = '.' in cpf or '-' in cpf
        digits = re.sub(r'\D', '', cpf)

        if self.level == 'high':
            digit_pattern = 'X' * 11
        elif self.level == 'low':
            digit_pattern = 'X' * 6 + digits[6:11]
        else:
            digit_pattern = 'X' * 3 + digits[3:6] + 'X' * 5

        if is_formatted:
            result = ''
            digit_idx = 0
            for char in cpf:
                if char in '.-':
                    result += char  # Separadores permanecem visíveis
                else:
                    result += digit_pattern[digit_idx]
                    digit_idx += 1
            return result
        else:
            return digit_pattern

    # Padrão de mascaramento de Email
    def _email_mask_pattern(self, email: str) -> str:
        """
        high:    XXXX@XXXXXXXXXX (tudo mascarado)
        default: jXXXXXXXX@empresa.com.br (primeiro caractere revelado)
        low:     XXXXXsilva@empresa.com.br (final do local revelado)
        """
        if '@' not in email:
            return 'X' * len(email)

        local, domain = email.split('@', 1)

        if self.level == 'high':
            return 'X' * len(local) + '@' + 'X' * len(domain)

        elif self.level == 'low':
            reveal_count = len(local) // 2
            if reveal_count == 0:
                reveal_count = 1
            local_pattern = 'X' * (len(local) - reveal_count) + local[-reveal_count:]
            return local_pattern + '@' + domain

        else:
            local_pattern = local[0] + 'X' * (len(local) - 1)
            return local_pattern + '@' + domain

    # Padrão de mascaramento de Telefone
    def _phone_mask_pattern(self, phone: str) -> str:
        """
        high:    +XX (XX) XXXXX-XXXX (tudo mascarado)
        default: +55 (21) XXXXX-5678 (DDD + últimos 4 revelados)
        low:     +55 (21) XXXX2-3456 (DDD + últimos 5 revelados)
        """
        digits = re.sub(r'\D', '', phone)

        if digits.startswith('55') and len(digits) > 11:
            has_country = True
            country_digits = digits[:2]
            remaining = digits[2:]
        else:
            has_country = False
            country_digits = ''
            remaining = digits

        ddd = remaining[:2]
        rest = remaining[2:]

        if self.level == 'high':
            all_digits_pattern = 'X' * len(digits)
        elif self.level == 'low':
            reveal = 5 if len(rest) >= 5 else len(rest)
            rest_pattern = 'X' * (len(rest) - reveal) + rest[-reveal:]
            if has_country:
                all_digits_pattern = country_digits + ddd + rest_pattern
            else:
                all_digits_pattern = ddd + rest_pattern
        else:
            reveal = 4 if len(rest) >= 4 else len(rest)
            rest_pattern = 'X' * (len(rest) - reveal) + rest[-reveal:]
            if has_country:
                all_digits_pattern = country_digits + ddd + rest_pattern
            else:
                all_digits_pattern = ddd + rest_pattern

        # Mapear de volta para o formato original
        result = ''
        digit_idx = 0
        for char in phone:
            if char.isdigit():
                if digit_idx < len(all_digits_pattern):
                    result += all_digits_pattern[digit_idx]
                    digit_idx += 1
                else:
                    result += char
            else:
                result += char  # Manter caracteres de formatação visíveis

        return result


# Funções auxiliares
def detect_pdf(pdf_path: str) -> dict:
    # Função auxiliar para detecção rápida.
    detector = PDFDetector()
    return detector.detect(pdf_path)


def mask_pdf(pdf_path: str, output_path: str, level: str = 'default') -> dict:
    # Função auxiliar para mascaramento rápido.
    detector = PDFDetector(level=level)
    return detector.mask(pdf_path, output_path)