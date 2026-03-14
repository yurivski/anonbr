import pytest
from anonbr.detectors.email import DetectorEmail, detectar_email, mascarar_email

class TesteDetectorEmail:
    def setup_method(self):
        self.detector = DetectorEmail()
    
    def test_detectar_email_simples(self):
        texto = "Contato: joao@email.com"
        resultados = self.detector.detectar(texto)
        
        assert resultados[0][0] == "joao@email.com"

    def test_detectar_email_com_ponto(self):
        texto = "Email: joao.silva@empresa.com.br"
        resultados = self.detector.detectar(texto)
        
        assert len(resultados) == 1
        assert resultados[0][0] == "joao.silva@empresa.com.br"
    
    def test_detectar_email_com_mais(self):
        texto = "Email: usuario+tag@dominio.com"
        resultados = self.detector.detectar(texto)
        
        assert len(resultados) == 1
        assert resultados[0][0] == "usuario+tag@dominio.com"
    
    def test_detectar_email_com_numeros(self):
        texto = "Contato: user123@test456.com"
        resultados = self.detector.detectar(texto)
        
        assert len(resultados) == 1
        assert resultados[0][0] == "user123@test456.com"
    
    def test_detectar_multiplos_emails(self):
        texto = "Contatos: joao@email.com e maria@outro.com.br"
        resultados = self.detector.detectar(texto)
        
        assert len(resultados) == 2
    
    def test_detectar_email_subdominio(self):
        texto = "Email: usuario@sub.dominio.com.br"
        resultados = self.detector.detectar(texto)
        
        assert len(resultados) == 1
    
    def test_mascarar_email_padrao(self):
        email = "joao@email.com"
        mascarado = self.detector.mascarar(email, nivel='padrao')
        
        assert mascarado == "jxxx@email.com"
    
    def test_mascarar_email_padrao_nome_longo(self):
        email = "joaosilva@email.com"
        mascarado = self.detector.mascarar(email, nivel='padrao')
        
        assert mascarado == "jxxxxxxxx@email.com"
        assert mascarado[0] == 'j'
    
    def test_mascarar_email_curto(self):
        email = "ab@email.com"
        mascarado = self.detector.mascarar(email)
        
        assert mascarado == "ax@email.com"
    
    def test_mascarar_email_nivel_alto(self):
        email = "joao@email.com"
        mascarado = self.detector.mascarar(email, nivel='alto')
        
        assert mascarado == "xxxx@xxxxx.xxx"
    
    def test_mascarar_email_dominio(self):
        email = "joao@email.com"
        mascarado = self.detector.mascarar(email, nivel='dominio')
        
        assert mascarado == "jxxx@email.com"
    
    def test_mascarar_email_sem_arroba(self):
        email = "emailinvalido"
        mascarado = self.detector.mascarar(email)
        
        assert mascarado == email

class TestHelpersEmail:
    def test_helper_detectar_email(self):
        texto = "Email: teste@exemplo.com"
        resultados = detectar_email(texto)
        
        assert len(resultados) == 1
        assert "teste@exemplo.com" in resultados[0][0]
    
    def test_helper_mascarar_email(self):
        email = "joao@email.com"
        mascarado = mascarar_email(email)
        
        assert "@email.com" in mascarado
        assert mascarado[0] == 'j'
    
    def test_helper_mascarar_email_nivel_alto(self):
        email = "joao@email.com"
        mascarado = mascarar_email(email, nivel='alto')
        
        assert mascarado == "xxxx@xxxxx.xxx"