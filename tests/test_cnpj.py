"""
Testes de detecção e mascaramento de CNPJ.

A partir da refatoração para YAML, os padrões regex não estão mais hardcoded
em cnpj.py, eles são carregados de config/patterns.yaml via pattern_loader.

O comportamento externo (o que detect() e mask() retornam) não muda;
apenas a origem dos padrões mudou. Os testes abaixo continuam válidos
e garantem que a nova fonte de padrões produz os mesmos resultados.

Para testar o carregamento do YAML em si, veja tests/test_pattern_loader.py.
"""

import pytest
from anonbr.detectors.cnpj import CNPJDetector, detect_cnpj, mask_cnpj

class TestCNPJDetector:
    def setup_method(self):
        self.detector = CNPJDetector()

    def test_detect_formatted_cnpj(self):
        text = "CNPJ: 11.222.333/0001-81"
        results = self.detector.detect(text)

        assert len(results) == 1
        assert results[0][0] == "11.222.333/0001-81"
        assert results[0][3] == True

    def test_detect_multiple_cnpjs(self):
        text = "CNPJ 1: 11.222.333/0001-81 e CNPJ 2: 11222333000181"
        results = self.detector.detect(text)

        assert len(results) == 2

    def test_mask_formatted_cnpj_default(self):
        cnpj = "11.222.333/0001-81"
        masked = self.detector.mask(cnpj, level='default')

        assert masked == "XX.222.333/XXXX-XX"

    def test_mask_unformatted_cnpj_default(self):
        cnpj = "11222333000181"
        masked = self.detector.mask(cnpj, level='default')

        assert masked == "XX222333XXXXXX"

    def test_mask_formatted_cnpj_high(self):
        cnpj = "11.222.333/0001-81"
        masked = self.detector.mask(cnpj, level='high')

        assert masked == "XX.XXX.XXX/XXXX-XX"

    def test_mask_unformatted_cnpj_high(self):
        cnpj = "11222333000181"
        masked = self.detector.mask(cnpj, level='high')

        assert masked == "XXXXXXXXXXXXXX"

    def test_mask_formatted_cnpj_low(self):
        cnpj = "11.222.333/0001-81"
        masked = self.detector.mask(cnpj, level='low')

        assert masked == "XX.XXX.XXX/0001-81"

    def test_mask_unformatted_cnpj_low(self):
        cnpj = "11222333000181"
        masked = self.detector.mask(cnpj, level='low')

        assert masked == "XXXXXXXX000181"

    def test_mask_preserves_format(self):
        formatted_cnpj = "11.222.333/0001-81"
        unformatted_cnpj = "11222333000181"

        assert '.' in self.detector.mask(formatted_cnpj)
        assert '/' in self.detector.mask(formatted_cnpj)
        assert '-' in self.detector.mask(formatted_cnpj)
        assert '.' not in self.detector.mask(unformatted_cnpj)
        assert '/' not in self.detector.mask(unformatted_cnpj)
        assert '-' not in self.detector.mask(unformatted_cnpj)


    def test_no_detect_sequence_longer_than_cnpj(self):
        text = "Código: 112223330001810000"
        results = self.detector.detect(text)
        assert len(results) == 0

    def test_no_detect_unformatted_sequence_longer_than_cnpj(self):
        text = "ID: 112223330001819999"
        results = self.detector.detect(text)
        assert len(results) == 0


class TestCNPJHelper:
    def test_helper_detect_cnpj(self):
        text = "CNPJ: 11.222.333/0001-81"
        results = detect_cnpj(text)

        assert len(results) == 1
        assert "11.222.333/0001-81" in results[0][0]

    def test_helper_mask_cnpj(self):
        cnpj = "11.222.333/0001-81"
        masked = mask_cnpj(cnpj)

        assert "XX" in masked

    def test_helper_mask_cnpj_high_level(self):
        cnpj = "11.222.333/0001-81"
        masked = mask_cnpj(cnpj, level='high')

        assert masked == "XX.XXX.XXX/XXXX-XX"

    def test_helper_no_detect_sequence_longer_than_cnpj(self):
        text = "Código: 112223330001810000"
        results = detect_cnpj(text)
        assert len(results) == 0

    def test_helper_no_detect_unformatted_sequence_longer_than_cnpj(self):
        text = "ID: 112223330001819999"
        results = detect_cnpj(text)
        assert len(results) == 0
