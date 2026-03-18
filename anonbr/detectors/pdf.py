"""
Detecta e mascara dados sensíveis, por enquanto CPF, email, telefone em arquivos PDF
usando redação pra preservar o layout do documento.
"""

import re
import fitz
from anonbr.detectors.cpf import CPFDetector
from anonbr.detectors.email import EmailDetector
from anonbr.detectors.telefone import PhoneDetector


class PDFDetector:
    """
    Detecta e mascara padrões de CPF, email e telefone em documentos PDF.
    Usa redação do pymupdf pra substituir o padrão detectado por versões mascaradas,
    preservando a estrutura original do documento.
    """

    def __init__(self, level='default'):

        # Níveis: high, default e low
        self.level = level
        self.detect_cpf = CPFDetector()
        self.detect_email = EmailDetector()
        self.detect_phone = PhoneDetector()

    """Reutiliza os regex das classes dos arquivos cpf, email e telefone para usar como base
    pra não ficar definindo os mesmos padrões"""
    # Pega os atributos da classes já definidas e organiza num dicionário.
    @property
    def pattern(self):
        return {
            'cpf_formatted': self.detect_cpf.formatted_regex,
            'cpf_unformatted': self.detect_cpf.unformatted_regex,
            'email': self.detect_email.regex,
            'phone_international': self.detect_phone.regexes[0],
            'phone_ddd': self.detect_phone.regexes[1],
            'phone_digits': self.detect_phone.regexes[2],
        }

    # Função de detecção
    def detect(self, pdf_path: str) -> dict:
        """
        Lê um PDF e detecta todos os padrões definidos.
        Ex.: 
        0: [('cpf', '191.626.860-01', retângulo), ...],
        1: [('email', 'user@test.com', retângulo), ...],
        """
        doc = fitz.open(pdf_path)
        findings = {}

        for page_num in range(len(doc)):
            page = doc[page_num]
            page_findings = []

            # Busca os padrões na página, padrões específicos primeiro para evitar sobreposições
            # Busca CPF formatado antes do não-formatado pra evitar duplicatas
            for match in page.search_for(None, flags=0):
                pass  # placeholder

            # Usa extração de texto mais regex pra detecção mais precisa
            text_dict = page.get_text("dict")

            for block in text_dict["blocks"]:
                if block["type"] != 0:  # Pula blocos, imagens, etc.
                    continue

                for line in block["lines"]:
                    for span in line["spans"]:
                        span_text = span["text"]
                        span_rect = fitz.Rect(span["bbox"])
                        span_font = span["font"]
                        span_size = span["size"]
                        span_color = span["color"]

                        # Verifica cada padrão contra o texto deste span
                        detections = self._detect_in_text(span_text)

                        for data_type, matched_text, start, end in detections:
                            page_findings.append({
                                'type': data_type,
                                'text': matched_text,
                                'rect': span_rect,
                                'font': span_font,
                                'size': span_size,
                                'color': span_color,
                                'span_text': span_text,
                                'start': start,
                                'end': end,
                            })

            if page_findings:
                findings[page_num] = page_findings

        doc.close()
        return findings

    def _detect_in_text(self, text: str) -> list:
        """
        Detecta todos os padrões sensíveis em uma string de texto.
        Trata sobreposições: CPF formatado tem prioridade sobre não-formatado,
        telefone internacional tem prioridade sobre telefone que iniciam com DDD.
        """
        detections = []
        used_positions = set()

        # Ordem: padrões mais específicos primeiro
        pattern_order = [
            ('cpf', 'cpf_formatted'),
            ('email', 'email'),
            ('phone', 'phone_international'),
            ('phone', 'phone_ddd'),
            ('cpf', 'cpf_unformatted'),
            ('phone', 'phone_digits'),
        ]

        for data_type, pattern_name in pattern_order:
            regex = self.pattern[pattern_name]

            for match in regex.finditer(text):
                start, end = match.start(), match.end()

                # Pula se esta posição já foi coberta por um padrão mais específico
                if any(pos in used_positions for pos in range(start, end)):
                    continue

                matched_text = match.group()
                detections.append((data_type, matched_text, start, end))

                # Marca posições como utilizadas
                for pos in range(start, end):
                    used_positions.add(pos)

        return detections

    # Função mascaramento
    def mask(self, pdf_path: str, output_path: str) -> dict:
        doc = fitz.open(pdf_path)
        summary = {'cpf': 0, 'email': 0, 'phone': 0, 'pages_processed': 0}

        for page_num in range(len(doc)):
            page = doc[page_num]
            page_text = page.get_text()
            page_had_redactions = False
    
            # Detecta todos os padrões no texto da página
            detections = self._detect_in_text(page_text)
    
            for data_type, matched_text, start, end in detections:
                # Busca a posição exata do texto na página
                rects = page.search_for(matched_text)
    
                if not rects:
                    continue
                
                # Mascara o valor
                masked = self._mask_value(data_type, matched_text)
    
                for rect in rects:
                    page.add_redact_annot(
                        rect,
                        text=masked,
                        fontname="helv",
                        fontsize=0,  # 0 = ajusta automaticamente ao retângulo
                        align=fitz.TEXT_ALIGN_LEFT,
                        fill=(1, 1, 1),
                        text_color=(0, 0, 0),
                    )
    
                page_had_redactions = True
                summary[data_type] += 1
    
            if page_had_redactions:
                page.apply_redactions()
                summary['pages_processed'] += 1
    
        doc.save(output_path)
        doc.close()
        return summary

    def _build_masked_text(self, span_text: str, detections: list) -> str:
        """ Substitui apenas os dados sensíveis detectados no texto do por versões mascaradas e 
        faz detecções por posição (início) em ordem reversa para substituir do fim"""
        sorted_detections = sorted(detections, key=lambda d: d[2], reverse=True)

        result = span_text

        for data_type, matched_text, start, end in sorted_detections:
            masked = self._mask_value(data_type, matched_text)
            result = result[:start] + masked + result[end:]

        return result

    def _mask_value(self, data_type: str, value: str) -> str:
        """
        Mascara um único valor com base no seu tipo e no nível atual e usa tarjas (█) pra textos redigitos.
        """
        if data_type == 'cpf':
            return self._mask_cpf(value)
        elif data_type == 'email':
            return self._mask_email(value)
        elif data_type == 'phone':
            return self._mask_phone(value)
        return value

    # Mascaramento de CPF
    def _mask_cpf(self, cpf: str) -> str:
        """
        Mascara CPF preservando formato.
            high:    ███.███.███-██
            default: ███.567.███-██ (revela o meio)
            low:     ███.██9.567-01 (revela o final)
        """
        is_formatted = '.' in cpf or '-' in cpf
        digits = re.sub(r'\D', '', cpf)

        if self.level == 'high':
            masked = '█' * 11

        elif self.level == 'low':
            masked = '█' * 6 + digits[6:11]

        else:
            # Padrão: revela o meio, posições 3-5
            masked = '⏹' * 3 + digits[3:6] + '█' * 5

        if is_formatted:
            return f"{masked[:3]}.{masked[3:6]}.{masked[6:9]}-{masked[9:11]}"

        return masked

    # Mascaramento de Email
    def _mask_email(self, email: str) -> str:
        """
        Mascara email preservando estrutura.
            high:    ███████████@███████.███.██
            default: j█████████@empresa.com.br
            low:     █████silva@empresa.com.br
        """
        if '@' not in email:
            return email

        local, domain = email.split('@', 1)

        if self.level == 'high':
            domain_parts = domain.split('.')
            masked_domain = '.'.join('█' * len(part) for part in domain_parts)
            masked_local = '█' * len(local)
            return f"{masked_local}@{masked_domain}"

        elif self.level == 'low':
            reveal_count = len(local) // 2
            if reveal_count == 0:
                reveal_count = 1
            masked_local = '█' * (len(local) - reveal_count) + local[-reveal_count:]
            return f"{masked_local}@{domain}"

        else:
            # Padrão: revela o primeiro caractere
            masked_local = local[0] + '█' * (len(local) - 1)
            return f"{masked_local}@{domain}"

    # Mascaramento de Telefone
    def _mask_phone(self, phone: str) -> str:
        """
        Mascara telefone preservando formato.
            high:    +██ (██) █████-████
            default: +55 (21) █████-5678 (DDD + últimos 4)
            low:     +55 (21) ████2-3456 (DDD + últimos 5)
        """
        original = phone
        digits = re.sub(r'\D', '', phone)

        # Detecta código do país
        if digits.startswith('55') and len(digits) > 11:
            has_country_code = True
            digits = digits[2:]
        else:
            has_country_code = False

        ddd = digits[:2]
        rest = digits[2:]

        if self.level == 'high':
            ddd_masked = '██'
            masked = '█' * len(rest)

        elif self.level == 'low':
            ddd_masked = ddd
            reveal = 5 if len(rest) >= 5 else len(rest)
            masked = '█' * (len(rest) - reveal) + rest[-reveal:]

        else:
            # Padão
            ddd_masked = ddd
            reveal = 4 if len(rest) >= 4 else len(rest)
            masked = '█' * (len(rest) - reveal) + rest[-reveal:]

        # Reconstrói o formato original
        if '(' in original or '-' in original:
            if len(rest) == 9:
                formatted = f"({ddd_masked}) {masked[:5]}-{masked[5:]}"
            else:
                formatted = f"({ddd_masked}) {masked[:4]}-{masked[4:]}"

            if has_country_code:
                country = '██' if self.level == 'high' else '55'
                formatted = f"+{country} {formatted}"
            return formatted
        else:
            prefix = ('██' if self.level == 'high' else '55') if has_country_code else ''
            return prefix + ddd_masked + masked

# Funções auxiliares pra uso rápido
def detect_pdf(pdf_path: str) -> dict:
    """Função auxiliar pra detecção rápida."""
    detector = PDFDetector()
    return detector.detect(pdf_path)


def mask_pdf(pdf_path: str, output_path: str, level: str = 'default') -> dict:
    """Função auxiliar pra mascaramento rápido."""
    detector = PDFDetector(level=level)
    return detector.mask(pdf_path, output_path)