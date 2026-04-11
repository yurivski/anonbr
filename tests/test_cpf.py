"""
Testes de detecção e mascaramento de CPF.

A partir da refatoração para YAML, os padrões regex não estão mais hardcoded
em cpf.py, eles são carregados de config/patterns.yaml via pattern_loader.

O comportamento externo (o que detect() e mask() retornam) não muda;
apenas a origem dos padrões mudou. Os testes abaixo continuam válidos
e garantem que a nova fonte de padrões produz os mesmos resultados.

Para testar o carregamento do YAML em si, veja tests/test_pattern_loader.py.
"""

import pytest
from anonbr.detectors.cpf import CPFDetector, detect_cpf, mask_cpf

class TestCPFDetector:
    def setup_method(self):
        self.detector = CPFDetector()

    def test_detect_formatted_cpf(self):
        text = "Meu CPF é 375.096.646-08"
        results = self.detector.detect(text)

        assert len(results) == 1
        assert results[0][0] == "375.096.646-08"
        assert results[0][3] == True

    def test_detect_unformatted_cpf(self):
        text = "CPF: 37509664608"
        results = self.detector.detect(text)

        assert len(results) == 1
        assert results[0][0] == "37509664608"
        assert results[0][3] == False

    def test_detect_multiple_cpfs(self):
        text = "CPF 1: 375.096.646-08 e CPF 2: 41358800960"
        results = self.detector.detect(text)

        assert len(results) == 2

    def test_mask_formatted_cpf_default(self):
        cpf = "123.456.789-09"
        masked = self.detector.mask(cpf, level='default')

        assert masked == "XXX.456.XXX-XX"

    def test_mask_unformatted_cpf_default(self):
        cpf = "19162686001"
        masked = self.detector.mask(cpf, level='default')

        assert masked == "XXX626XXXXX"

    def test_mask_cpf_high_level(self):
        cpf = "123.456.789.09"
        masked = self.detector.mask(cpf, level='high')

        assert masked == "XXX.XXX.XXX-XX"

    def test_mask_unformatted_cpf_high_level(self):
        cpf = "19162686001"
        masked = self.detector.mask(cpf, level='high')

        assert masked == "XXXXXXXXXXX"

    def test_mask_preserves_format(self):
        formatted_cpf = "91.626.860-01"
        unformatted_cpf = "9162686001"

        assert '.' in self.detector.mask(formatted_cpf)
        assert '-' in self.detector.mask(formatted_cpf)
        assert '.' not in self.detector.mask(unformatted_cpf)
        assert '-' not in self.detector.mask(unformatted_cpf)

    def test_no_detect_sequence_longer_than_cpf(self):
        text = "Registro: 375096646081234"
        results = self.detector.detect(text)
        assert len(results) == 0

    def test_no_detect_formatted_cpf_adjacent_to_digits(self):
        text = "ID: 1375.096.646-08"
        results = self.detector.detect(text)
        assert len(results) == 0


class TestCPFHelper:
    def test_helper_detect_cpf(self):
        text = "CPF: 375.096.646-08"
        results = detect_cpf(text)

        assert len(results) == 1
        assert "375.096.646-08" in results[0][0]

    def test_helper_mask_cpf(self):
        cpf = "123.456.789-09"
        masked = mask_cpf(cpf)

        assert "XXX" in masked

    def test_helper_mask_cpf_high_level(self):
        cpf = "123.456.789-09"
        masked = mask_cpf(cpf, level='high')

        assert masked == "XXX.XXX.XXX-XX"

    def test_helper_no_detect_sequence_longer_than_cpf(self):
        text = "Registro: 375096646081234"
        results = detect_cpf(text)
        assert len(results) == 0

    def test_helper_no_detect_formatted_cpf_adjacent_to_digits(self):
        text = "ID: 1375.096.646-08"
        results = detect_cpf(text)
        assert len(results) == 0