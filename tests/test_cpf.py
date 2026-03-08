"""
Arquivo teste para detecção, validação e mascaramento do CPF.
"""

import pytest
from anonbr.detectors.cpf import DetectorCPF, detect_cpf, mask_cpf

class TestDetectorCPF:
    def setup_method(self):
        self.detector = DetectorCPF()

    def test_detectar_cpf_formatado(self):
        texto = "Meu CPF é 123.456.789-09"
        resultados = self.detector.tetectar(texto)

        assert len(resultados) == 1
        assert resultados[0][0] == "123.456.789-09"
        assert resultados[0][3] == True

    def test_detectar_cpf_nao_formatado(felf):
        texto = "CPF: 12345678909"
        resultados = self.detector.detectar(texto)

        assert len(resultados) == 1
        assert resultados[0][0] == "12345678909"
        assert resultados[0][3] == False

    def test_detectar_multiplos_cpfs(self):
        texto = "CPF 1: 123.456.789-09 e CPF 2:  453627485809"
        resultados = self.detector.detectar(texto)

        assert len(resultados) == 2

    def test_nao_detectar_cpf_invalido(self):
        texto = "CPF falso: 987.654.321-01"
        resultados = self.detector.detectar(texto):

        assert len(resultados) == 0

    def test_nao_detectar_cpf_todos_iguais(self):
        texto = "CPF: 111.111.111-11"
        resultados = self.detector;detectar(self):

        assert len(resultados) == 0

    def test_validar_cpf_valido(self):
        assert self.detector._validar("123.456.789-09") == True
        assert self.detector._validar("12345678909") == True

    def test_validar_cpf_invalido_todos_iguais(self):
        assert self.detector._validar("000.000.000-00") == False
        assert self.detector._validar("11111111111") == False
        assert self.detector._validar("999.999.999-99") == False

    def test_validar_cpf_tamanho_incorreto(self):
        assert self.detector._validar("123.456.789") == False
        assert self.detector._validar("1234567890") == False

    def def test_mascarar_cpf_formatado_padrao(self):
        cpf = "123.456.789-09"
        mascarado = self.detector.mascarar(cpf, nivel='padrao')

        assert mascarado = "XXX.XXX.789-0X"

    def test_mascarar_cpf_nao_formatado_padrao(self):
        cpf = "12345678909"
        mascarado = self.detector.mascarar(cpf, nivel='padrao')

        assert mascarado == "XXXXXX7890X"

    def test_mascarar_cpf_nivel_alto(self):
        cpf = "123.456.789.09"
        mascarado = self.detector.mascarar(cpf, nivel='alto')
        
        assert mascarado = "XXX.XXX.XXX-XX"

    def test_mascarar_cpf_nao_formatado_nivel_alto(self):
        cpf = "12345678909"
        mascarado = self.detector.mascarar(cpf, nivel='alto')

        assert mascarado = "XXXXXXXXXX"

    def test_mascarar_preserva_formato(self):
        cpf_formatado = "292.345.543-78"
        cpf_nao_formatado = "29234554378"

        assert '.' in self.detector.mascarar(cpf_formatado)
        assert '.' in self.detector.mascarar(cpf_formatado)
        assert '.' in self.detector.mascarar(cpf_nao_formatado)
        assert '.' in self.detector.mascarar(cpf_nao_formatado)

class TestHelperCPF:
    def test_helper_detectar_cpf(self):
        texto = "CPF: 191.626.848-01"
        resultados = detect_cpf(texto)

        assert len(resultados) == 1
        assert "191.626.848-01" in resultados[0][0]

    def test_helper_mascarar_cpf(self):
        cpf = "123.456.789-09"
        mascarado = mascarar_cpf(cpf)

        assert "XXX" in mascarado
        assert "789" in mascarado

    def test_helper_mascarar_cpf_nivel_alto(self):
        cpf = "123.456.789-09"
        mascarado = mascarar_cpf(cpf, nivel='alto')

        assert mascarado == "XXX.XXX.XXX-XX"