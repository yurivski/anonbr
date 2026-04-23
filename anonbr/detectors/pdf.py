# Copyright (C) 2026 Yuri Pontes
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Detecta e mascara dados sensíveis em arquivos PDF.

Diferente dos detectores de texto, o PDFDetector opera em dois estágios:

  Estágio 1 - Detecção (pdfplumber):
      Extrai os caracteres individuais do PDF com suas coordenadas (x0, top, x1, bottom).
      Reconstrói o texto linha a linha e aplica os mesmos padrões regex dos detectores.

  Estágio 2 - Mascaramento (pymupdf / fitz):
      Para cada caractere que deve ser ocultado, desenha uma barra preta
      (anotação de redação) sobre o bounding box do caractere no PDF.
      Não altera o texto - apenas o cobre visualmente.

Fonte dos padrões regex: config/patterns.yaml -> via pattern_loader
  Os padrões são acessados diretamente pelo pattern_loader (mesma fonte
  que os detectores CPF, CNPJ, Email e Telefone), garantindo consistência.
"""

import re
import os
import bisect
import fitz
import pdfplumber

from tqdm import tqdm
from anonbr.pattern_loader import get_compiled_by_name


class PDFDetector:
    """
    Detecta e mascara padrões regex em documentos PDF.

    Usa posicionamento em nível de caractere para desenhar barras pretas
    exatamente sobre os caracteres que precisam ser mascarados.

    Atributo:
        level - nível de mascaramento ('default', 'high', 'low').
                 Controla quais dígitos/caracteres são revelados ou ocultados
                 nas funções _*_mask_pattern.
    """

    def __init__(self, level: str = 'default', data_types=None):
        self.level = level
        # None = todos os tipos; lista = filtra os padrões e a detecção
        self.data_types = data_types

    @property
    def patterns(self) -> dict:
        """
        Carrega e retorna os padrões regex compilados do YAML via pattern_loader.

        Esta property é avaliada a cada acesso, mas o pattern_loader usa
        lru_cache internamente, o YAML só é lido uma vez por processo.

        Os padrões de telefone usados aqui são apenas os 3 mais específicos:
          - phone_international - +55 (21) 98765-4321
          - phone_ddd_mobile - (21) 9 8765-4321  (nono dígito separado)
          - phone_ddd_landline - (21) 98765-4321

        Os padrões genéricos (only_numbers, short) não são usados no PDF
        para evitar falsos positivos com números que não são telefones.

        Retorna:
            dict {chave_interna: re.Pattern}
        """
        # Só carrega os padrões dos tipos que estão ativos
        active = self.data_types
        result = {}

        if active is None or 'cpf' in active:
            cpf = get_compiled_by_name('cpf')
            # CPF: formatado tem prioridade sobre não formatado
            result['cpf_formatted']   = cpf['formatted']
            result['cpf_unformatted'] = cpf['unformatted']

        if active is None or 'cnpj' in active:
            cnpj = get_compiled_by_name('cnpj')
            # CNPJ: formatado tem prioridade sobre não formatado
            result['cnpj_formatted']   = cnpj['formatted']
            result['cnpj_unformatted'] = cnpj['unformatted']

        if active is None or 'email' in active:
            email = get_compiled_by_name('email')
            # E-mail: padrão único
            result['email'] = re.compile(email['standard'].pattern, re.IGNORECASE)

        if active is None or 'phone' in active:
            phone = get_compiled_by_name('telefone')
            # Telefone: do mais específico ao mais genérico
            result['phone_international'] = phone['international']
            result['phone_ddd_mobile']    = phone['with_nono_digit_space']
            result['phone_ddd_landline']  = phone['with_ddd']

        return result

    # Extração de texto
    def _extract_text_with_mapping(self, chars: list) -> tuple:
        """
        Reconstrói o texto de uma página a partir da lista de caracteres do pdfplumber
        e cria um mapeamento de índice-no-texto -> índice-no-chars.

        O pdfplumber retorna uma lista de dicts, cada um com:
            {'text': 'A', 'x0': 72.0, 'top': 100.5, 'x1': 77.2, 'bottom': 110.5, ...}

        Esta função:
          1. Detecta quebras de linha comparando a posição vertical ('top') de
             caracteres consecutivos (diferença > 2 pontos = nova linha).
          2. Insere '\n' no texto reconstruído nas quebras de linha.
          3. Para cada caractere (não-newline), registra a correspondência
             texto_idx -> chars_idx no dicionário text_to_char.

        Parâmetro:
            chars - lista de dicts de caracteres retornada por page.chars.

        Retorna:
            (text, text_to_char):
                text - string com o texto completo da página.
                text_to_char - {indice_no_texto: indice_na_lista_chars}
        """
        if not chars:
            return '', {}

        text = ''
        text_to_char = {}   # mapeia posição no texto para índice no chars
        char_idx = 0
        last_top = chars[0]['top']

        for c in chars:
            if abs(c['top'] - last_top) > 2:
                # Nova linha detectada: insere '\n' (não mapeia pra nenhum char)
                text += '\n'
                last_top = c['top']

            # Registra a correspondência antes de adicionar o caractere ao texto
            text_to_char[len(text)] = char_idx
            text += c['text']
            char_idx += 1

        return text, text_to_char

    # Detecção
    def detect(self, pdf_path: str) -> dict:
        """
        Lê um PDF e detecta todos os padrões de dados sensíveis.

        Percorre cada página, extrai o texto e aplica _detect_in_text.

        Parâmetro:
            pdf_path - caminho para o arquivo PDF de entrada.

        Retorna:
            dict {num_pagina: [{'type', 'text', 'start', 'end'}, ...]}
            Apenas páginas com detecções aparecem no resultado.
        """
        findings = {}

        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                chars = page.chars
                if not chars:
                    continue

                # Reconstrói texto da página (sem usar o mapeamento aqui)
                page_text, _ = self._extract_text_with_mapping(chars)
                detections = self._detect_in_text(page_text)

                if detections:
                    findings[page_num] = [
                        {'type': dt, 'text': mt, 'start': s, 'end': e}
                        for dt, mt, s, e in detections
                    ]

        return findings

    def _detect_in_text(self, text: str) -> list:
        """
        Aplica todos os padrões regex a uma string de texto.

        Ordem de prioridade (padrões mais específicos primeiro):
            CPF formatado -> CPF não-formatado 
            CNPJ formatado -> CNPJ não-formatado 
            E-mail 
            Telefone internacional -> Telefone DDD+nono -> Telefone DDD

        A deduplicação por posição impede que o mesmo trecho seja detectado
        mais de uma vez por padrões diferentes.

        Além disso, ao final, realiza uma segunda varredura, dividindo o texto
        por '/' para capturar telefones que aparecem logo após uma barra e
        que os padrões com lookbehind não capturam corretamente. 
        
        Essa é uma solução temporária para identificar os padrões de dados em PDFs 
        com documentos digitalizados que contenham uma lista de dados separados por '/'. 
        Por enquanto, foi a melhor solução que encontrei para evitar essa vulnerabilidade.

        Talvez implementando uma detecção por imagens resolva, mas não estudei isso ainda. Isso
        sacrifica um pouquinho do desempenho, mas nada muito relevante em documentos com cerca
        de 300 páginas contendo aproximadamente 500 dados para censurar. 

        Parâmetro:
            text - string de texto de uma página.

        Retorna:
            Lista de tuplas (tipo, texto_matched, inicio, fim):
                tipo - 'cpf', 'cnpj', 'email' ou 'phone'
                texto - string exata do dado encontrado
                inicio - índice de início no texto
                fim - índice de fim no texto
        """
        detections = []
        # Intervalos já ocupados como lista ordenada de (start, end).
        # Busca e inserção são O(log n), evitando iterar cada posição do match.
        used_intervals: list = []

        # Carrega os padrões ativos uma vez (a property já filtra por data_types)
        active_patterns = self.patterns

        # Ordem de aplicação completa — do mais específico ao mais genérico.
        # Só inclui as entradas cujo padrão existe no dict ativo (filtrado por data_types).
        full_pattern_order = [
            ('cpf',   'cpf_formatted'),
            ('cpf',   'cpf_unformatted'),
            ('cnpj',  'cnpj_formatted'),
            ('cnpj',  'cnpj_unformatted'),
            ('email', 'email'),
            ('phone', 'phone_international'),
            ('phone', 'phone_ddd_mobile'),
            ('phone', 'phone_ddd_landline'),
        ]
        pattern_order = [
            (dt, pn) for dt, pn in full_pattern_order if pn in active_patterns
        ]

        for data_type, pattern_name in pattern_order:
            regex = active_patterns[pattern_name]

            for match in regex.finditer(text):
                start, end = match.start(), match.end()

                # Pula se o intervalo sobrepõe algum já registrado (O(log n))
                idx = bisect.bisect_left(used_intervals, (start,))
                if (idx > 0 and used_intervals[idx - 1][1] > start) or \
                   (idx < len(used_intervals) and used_intervals[idx][0] < end):
                    continue

                detections.append((data_type, match.group(), start, end))
                bisect.insort(used_intervals, (start, end))

        # Segunda varredura: telefones separados por '/'
        # Ex.: '21987654321/21876543210' — a barra pode quebrar o lookbehind (?<!\d)
        # e o segundo número não ser detectado na varredura anterior.
        # Só roda se 'phone' está nos tipos ativos.
        if 'phone_international' in active_patterns:
            phone_patterns = [
                active_patterns['phone_international'],
                active_patterns['phone_ddd_mobile'],
                active_patterns['phone_ddd_landline'],
            ]

            parts = text.split('/')
            offset = 0

            for part in parts:
                for regex in phone_patterns:
                    for match in regex.finditer(part):
                        original_start = offset + match.start()
                        original_end   = offset + match.end()

                        # Pula intervalos já detectados (O(log n))
                        idx = bisect.bisect_left(used_intervals, (original_start,))
                        if (idx > 0 and used_intervals[idx - 1][1] > original_start) or \
                           (idx < len(used_intervals) and used_intervals[idx][0] < original_end):
                            continue

                        detections.append(('phone', match.group(), original_start, original_end))
                        bisect.insort(used_intervals, (original_start, original_end))

                # Avança offset: comprimento da parte + 1 (pelo '/' que foi removido)
                offset += len(part) + 1

        return detections

    # Mascaramento
    def mask(self, pdf_path: str, output_path: str) -> dict:
        """
        Lê um PDF, detecta dados sensíveis e salva uma versão com barras de redação.

        Fluxo interno:
          1. _build_mask_map() - usa pdfplumber para mapear caracteres a cobrir.
          2. fitz.open() - abre o PDF com pymupdf.
          3. Para cada página e cada barra no mapa, adiciona uma anotação de
             redação (add_redact_annot) e a aplica (apply_redactions).
          4. Salva o PDF resultante em output_path.

        Parâmetros:
            pdf_path - caminho do PDF original.
            output_path - caminho onde o PDF censurado será salvo.

        Retorna:
            dict de sumário com contagem de cada tipo detectado e páginas processadas:
            {'cpf': int, 'cnpj': int, 'email': int, 'phone': int, 'pages_processed': int}
        """
        summary = {'cpf': 0, 'cnpj': 0, 'email': 0, 'phone': 0, 'pages_processed': 0}

        # Estágio 1: mapeia os bounding boxes a cobrir (usa pdfplumber)
        mask_map = self._build_mask_map(pdf_path, summary)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        if not mask_map:
            # Nenhum dado sensível -> salva cópia sem alteração
            doc = fitz.open(pdf_path)
            doc.save(output_path)
            doc.close()
            return summary

        # Estágio 2: desenha as barras de redação (usa pymupdf/fitz)
        doc = fitz.open(pdf_path)

        for page_num, bars in tqdm(mask_map.items(), desc="Censurando", unit="pág"):
            page = doc[page_num]

            for bar in bars:
                # Cria o retângulo do bounding box agrupado
                rect = fitz.Rect(bar['x0'], bar['top'], bar['x1'], bar['bottom'])
                # Adiciona anotação de redação: caixa preta com 'X' invisível
                page.add_redact_annot(
                    rect,
                    text='X',
                    fontname="helv",
                    fontsize=1,
                    fill=(0, 0, 0), # preenchimento preto
                    text_color=(1, 1, 1), # texto branco (invisível sobre fundo preto)
                )

            # Efetiva todas as redações da página
            page.apply_redactions()
            summary['pages_processed'] += 1

        doc.save(output_path)
        doc.close()

        return summary

    def _build_mask_map(self, pdf_path: str, summary: dict) -> dict:
        """
        Constrói o mapa de regiões a cobrir em cada página.

        Para cada página:
          1. Extrai chars com _extract_text_with_mapping.
          2. Detecta padrões com _detect_in_text.
          3. Determina quais índices de caractere mascarar com _get_chars_to_mask.
          4. Busca o bounding box de cada caractere na lista chars.
          5. Funde bounding boxes adjacentes na mesma linha em barras únicas
             (reduz o número de anotações e preenche pequenas lacunas entre letras).

        Parâmetros:
            pdf_path - caminho do PDF.
            summary  - dict mutável; contagens por tipo são incrementadas aqui.

        Retorna:
            {num_pagina: [{'x0', 'top', 'x1', 'bottom'}, ...]}
            Cada elemento da lista representa uma barra de redação contínua.
        """
        mask_map = {}

        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in tqdm(enumerate(pdf.pages), total=len(pdf.pages), desc="Detectando", unit="pág"):
                chars = page.chars
                if not chars:
                    continue

                # Reconstrói texto e obtém mapeamento texto_idx -> chars_idx
                page_text, text_to_char = self._extract_text_with_mapping(chars)

                detections = self._detect_in_text(page_text)
                if not detections:
                    continue

                # Determina quais índices (no texto) devem ser cobertos
                chars_to_mask = self._get_chars_to_mask(page_text, detections)

                # Coleta bounding boxes dos chars correspondentes
                rects = []
                for text_idx in sorted(chars_to_mask.keys()):
                    if text_idx in text_to_char:
                        char_idx = text_to_char[text_idx]
                        if char_idx < len(chars):
                            c = chars[char_idx]
                            rects.append((c['x0'], c['top'], c['x1'], c['bottom']))

                # Funde rects adjacentes da mesma linha em barras contínuas
                # Critério de fusão: mesma linha (top) e gap < largura de um caractere
                page_bars = []
                for rect in rects:
                    char_width = rect[2] - rect[0]
                    if (page_bars
                            and abs(rect[1] - page_bars[-1]['top']) < 2
                            and (rect[0] - page_bars[-1]['x1']) < char_width):
                        # Estende a última barra até o fim do caractere atual
                        page_bars[-1]['x1'] = rect[2]
                    else:
                        # Inicia uma nova barra
                        page_bars.append({
                            'x0':    rect[0],
                            'top':   rect[1],
                            'x1':    rect[2],
                            'bottom': rect[3]
                        })

                if page_bars:
                    mask_map[page_num] = page_bars

                # Incrementa o sumário por tipo detectado
                for data_type, _, _, _ in detections:
                    summary[data_type] += 1

        return mask_map

    def _get_chars_to_mask(self, text: str, detections: list) -> dict:
        """
        Determina quais índices de caractere (no texto reconstruído) devem ser cobertos.

        Para cada detecção, obtém o padrão de mascaramento (_get_mask_pattern)
        e itera caractere a caractere: posições marcadas com 'X' no padrão
        são adicionadas ao dicionário de resultado.

        Parâmetros:
            text - texto completo da página.
            detections - lista de tuplas (tipo, texto, inicio, fim).

        Retorna:
            {indice_no_texto: tipo_dado}
            Apenas índices que devem ser cobertos com barra preta.
        """
        chars_to_mask = {}

        for data_type, matched_text, start, end in detections:
            # Obtém o padrão 'X'/'.' de mesmo comprimento que o texto detectado
            mask_pattern = self._get_mask_pattern(data_type, matched_text)

            for i, mask_char in enumerate(mask_pattern):
                char_idx = start + i
                if mask_char == 'X':
                    # Este caractere deve ser coberto com barra preta
                    chars_to_mask[char_idx] = data_type

        return chars_to_mask

    def _get_mask_pattern(self, data_type: str, value: str) -> str:
        """
        Retorna uma string de mesmo comprimento que 'value'.

        Convenção:
            'X' = mascarar este caractere (desenhar barra preta)
            qualquer outro char = manter visível (sem barra)

        Parâmetro:
            data_type - 'cpf', 'cnpj', 'email' ou 'phone'.
            value - string exata do dado detectado.

        Retorna:
            String de padrão com len(value) caracteres.
        """
        if data_type == 'cpf':
            return self._cpf_mask_pattern(value)
        elif data_type == 'cnpj':
            return self._cnpj_mask_pattern(value)
        elif data_type == 'email':
            return self._email_mask_pattern(value)
        elif data_type == 'phone':
            return self._phone_mask_pattern(value)
        # Fallback: mascara tudo
        return 'X' * len(value)

    # Padrões de mascaramento por tipo 
    def _cpf_mask_pattern(self, cpf: str) -> str:
        """
        Gera o padrão 'X'/'.' para um CPF, alinhado com a lógica de CPFDetector.mask.

        Níveis:
            'high' -> XXX.XXX.XXX-XX (todos os dígitos mascarados)
            'default' -> XXX.096.XXX-XX (revela o trecho central, dígitos 4–6)
            'low' -> XXX.XX6.646-08 (revela o final, dígitos 7–11)

        Separadores (., -) nunca são mascarados, permanecem visíveis no PDF.
        """
        digits = ''.join(re.findall(r'\d', cpf))
        is_formatted = bool(re.findall(r'[.\-]', cpf))

        if self.level == 'high':
            digit_pattern = 'X' * 11
        elif self.level == 'low':
            digit_pattern = 'X' * 6 + digits[6:11]
        else:
            # Padrão: revela dígitos 4–6
            digit_pattern = 'X' * 3 + digits[3:6] + 'X' * 5

        if is_formatted:
            # Reconstrói posição a posição, mantendo separadores visíveis
            result = ''
            digit_idx = 0
            for char in cpf:
                if not char.isdigit():
                    result += char # separador: mantém visível
                else:
                    result += digit_pattern[digit_idx]
                    digit_idx += 1
            return result
        else:
            return digit_pattern

    def _cnpj_mask_pattern(self, cnpj: str) -> str:
        """
        Gera o padrão 'X'/'.' para um CNPJ, alinhado com a lógica de CNPJDetector.mask.

        Níveis:
            'high' -> XX.XXX.XXX/XXXX-XX (todos os dígitos mascarados)
            'default' -> XX.222.333/XXXX-XX (revela parte central da raiz, dígitos 3–8)
            'low' -> XX.XXX.XXX/0001-81 (revela filial + verificadores, dígitos 9–14)

        Separadores (., /, -) nunca são mascarados.
        """
        is_formatted = bool(re.findall(r'[.\/-]', cnpj))
        digits = ''.join(re.findall(r'\d', cnpj))

        if self.level == 'high':
            digit_pattern = 'X' * 14
        elif self.level == 'low':
            digit_pattern = 'X' * 8 + digits[8:14]
        else:
            digit_pattern = 'X' * 2 + digits[2:8] + 'X' * 6

        if is_formatted:
            result = ''
            digit_idx = 0
            for char in cnpj:
                if char.isdigit():
                    result += digit_pattern[digit_idx]
                    digit_idx += 1
                else:
                    result += char    # separador: mantém visível
            return result
        else:
            return digit_pattern

    def _email_mask_pattern(self, email: str) -> str:
        """
        Gera o padrão 'X'/'.' para um e-mail, alinhado com EmailDetector.mask.

        Níveis:
            'high' -> XXXX@XXXXXXXXXX (tudo mascarado, incluindo domínio)
            'default' -> jXXXXXXXX@gmail.com (revela 1º char do local)
            'low' -> XXXXsilva@gmail.com (revela metade final do local)

        O '@' e o domínio (exceto no nível 'high') permanecem visíveis.
        """
        if '@' not in email:
            return 'X' * len(email)

        local, domain = email.split('@', 1)

        if self.level == 'high':
            # Mascara local e domínio completamente
            return 'X' * len(local) + '@' + 'X' * len(domain)

        elif self.level == 'low':
            reveal_count = max(len(local) // 2, 1)
            local_pattern = 'X' * (len(local) - reveal_count) + local[-reveal_count:]
            return local_pattern + '@' + domain

        else:
            # Padrão: só o primeiro caractere do local fica visível
            local_pattern = local[0] + 'X' * (len(local) - 1)
            return local_pattern + '@' + domain

    def _phone_mask_pattern(self, phone: str) -> str:
        """
        Gera o padrão 'X'/'.' para um telefone, alinhado com PhoneDetector.mask.

        Níveis:
            'high' -> +XX (XX) XXXXX-XXXX (tudo mascarado)
            'default' -> +55 (21) XXXXX-5678 (revela DDD + últimos 4 dígitos)
            'low' -> +55 (21) XXXX2-3456 (revela DDD + últimos 5 dígitos)

        Caracteres de formatação (+, (, ), -, espaço) sempre permanecem visíveis.
        """
        digits = ''.join(re.findall(r'\d', phone))
        is_formatted = bool(re.findall(r'[()+ \-]', phone))

        # Separa código do país (se presente) de DDD + número local
        if digits.startswith('55') and len(digits) > 11:
            has_country = True
            country_digits = digits[:2] # '55'
            remaining = digits[2:]
        else:
            has_country = False
            country_digits = ''
            remaining = digits

        ddd  = remaining[:2] # ex.: '21'
        rest = remaining[2:] # ex.: '987654321'

        if self.level == 'high':
            # Todos os dígitos viram 'X'
            all_digits_pattern = 'X' * len(digits)

        elif self.level == 'low':
            reveal = min(5, len(rest))
            rest_pattern = 'X' * (len(rest) - reveal) + rest[-reveal:]
            if has_country:
                all_digits_pattern = country_digits + ddd + rest_pattern
            else:
                all_digits_pattern = ddd + rest_pattern

        else:
            reveal = min(4, len(rest))
            rest_pattern = 'X' * (len(rest) - reveal) + rest[-reveal:]
            if has_country:
                all_digits_pattern = country_digits + ddd + rest_pattern
            else:
                all_digits_pattern = ddd + rest_pattern

        # Reconstrói caractere a caractere, substituindo dígitos pelo padrão
        # e mantendo separadores de formatação intactos
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
                result += char # separador: mantém visível

        return result


# Funções auxiliares
def detect_pdf(pdf_path: str) -> dict:
    """
    Atalho funcional para PDFDetector().detect(pdf_path).

    Instancia um detector com nível padrão e retorna o dicionário de detecções.
    """
    detector = PDFDetector()
    return detector.detect(pdf_path)


def mask_pdf(pdf_path: str, output_path: str, level: str = 'default') -> dict:
    """
    Atalho funcional para PDFDetector(level).mask(pdf_path, output_path).

    Instancia um detector com o nível informado e salva o PDF censurado.
    """
    detector = PDFDetector(level=level)
    return detector.mask(pdf_path, output_path)
