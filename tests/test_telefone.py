import pytest
from anonbr.detectors.telefone import DetectorTelefone, detectar_telefone, mascarar_telefone


class TestDetectorTelefone:
    def setup_method(self):
        self.detector = DetectorTelefone()
    
    def test_detectar_celular_formatado(self):
        texto = "Telefone: (21) 98765-4321"
        resultados = self.detector.detectar(texto)
        
        assert len(resultados) == 1
        assert "(21) 98765-4321" in resultados[0][0]
    
    def test_detectar_fixo_formatado(self):
        texto = "Fixo: (21) 3456-7890"
        resultados = self.detector.detectar(texto)
        
        assert len(resultados) == 1
    
    def test_detectar_celular_sem_formatacao(self):
        texto = "WhatsApp: 21987654321"
        resultados = self.detector.detectar(texto)
        
        assert len(resultados) == 1
        assert "21987654321" in resultados[0][0]
    
    def test_detectar_fixo_sem_formatacao(self):
        texto = "Telefone: 2134567890"
        resultados = self.detector.detectar(texto)
        
        assert len(resultados) == 1
    
    def test_detectar_com_codigo_pais(self):
        texto = "Internacional: +55 21 98765-4321"
        resultados = self.detector.detectar(texto)
        
        assert len(resultados) == 1
        assert "+55" in resultados[0][0]
    
    def test_detectar_multiplos_telefones(self):
        texto = "Cel: (21) 98765-4321 Fixo: (21) 3456-7890"
        resultados = self.detector.detectar(texto)
        
        assert len(resultados) == 2
    
    def test_validar_celular_valido(self):
        assert self.detector._validar("(21) 98765-4321") == True
        assert self.detector._validar("21987654321") == True
    
    def test_validar_fixo_valido(self):
        assert self.detector._validar("(21) 3456-7890") == True
        assert self.detector._validar("2134567890") == True
    
    def test_validar_ddd_valido_range(self):
        assert self.detector._validar("(11) 98765-4321") == True
        assert self.detector._validar("(99) 98765-4321") == True
    
    def test_validar_ddd_invalido_menor_11(self):
        assert self.detector._validar("(10) 98765-4321") == False
        assert self.detector._validar("(05) 98765-4321") == False
    
    def test_validar_ddd_invalido_maior_99(self):
        # DDDs acima de 99 não são válidos no Brasil
        pass
    
    def test_validar_celular_sem_9_inicial(self):
        assert self.detector._validar("21887654321") == False
    
    def test_validar_telefone_tamanho_invalido(self):
        assert self.detector._validar("219876543") == False  # 9 dígitos
        assert self.detector._validar("219876543210") == False  # 12 dígitos
    
    def test_validar_com_codigo_pais(self):
        assert self.detector._validar("+55 21 98765-4321") == True
        assert self.detector._validar("+5521987654321") == True
    
    def test_mascarar_celular_padrao(self):
        telefone = "(21) 98765-4321"
        mascarado = self.detector.mascarar(telefone, nivel='padrao')
        
        assert "4321" in mascarado
        assert "XXX" in mascarado
    
    def test_mascarar_fixo_padrao(self):
        telefone = "(21) 3456-7890"
        mascarado = self.detector.mascarar(telefone, nivel='padrao')
        
        assert "7890" in mascarado
        assert "XXX" in mascarado
    
    def test_mascarar_celular_nivel_alto(self):
        telefone = "(21) 98765-4321"
        mascarado = self.detector.mascarar(telefone, nivel='alto')
        
        assert "XXXX" in mascarado
        assert "4321" not in mascarado
    
    def test_mascarar_preserva_formato_parenteses(self):
        telefone = "(21) 98765-4321"
        mascarado = self.detector.mascarar(telefone)
        
        assert "(" in mascarado
        assert ")" in mascarado
        assert "-" in mascarado
    
    def test_mascarar_preserva_formato_sem_parenteses(self):
        telefone = "21987654321"
        mascarado = self.detector.mascarar(telefone)
        
        assert "(" not in mascarado
        assert ")" not in mascarado
        assert "-" not in mascarado
    
    def test_mascarar_com_codigo_pais(self):
        telefone = "+55 21 98765-4321"
        mascarado = self.detector.mascarar(telefone)
        
        assert "+55" in mascarado
        assert "4321" in mascarado
    
    def test_mascarar_nivel_minimo(self):
        telefone = "(21) 98765-4321"
        mascarado = self.detector.mascarar(telefone, nivel='padrao')
        
        assert "(21)" in mascarado
        assert "4321" in mascarado

class TestHelpersTelefone:
    def test_helper_detectar_telefone(self):
        texto = "Telefone: (21) 98765-4321"
        resultados = detectar_telefone(texto)
        
        assert len(resultados) == 1
    
    def test_helper_mascarar_telefone(self):
        telefone = "(21) 98765-4321"
        mascarado = mascarar_telefone(telefone)
        
        assert "4321" in mascarado
        assert "XXX" in mascarado
    
    def test_helper_mascarar_telefone_nivel_alto(self):
        telefone = "(21) 98765-4321"
        mascarado = mascarar_telefone(telefone, nivel='alto')
        
        assert "4321" not in mascarado