import pytest
from anonbr.detectors.email import DetectorEmail, detectar, mascarar

class TesteDetectorEmail:
    def setup_method(self):
        self.detector = DetectorEmail()
    
    def test_detectar_email_simples(self):
        texto = "Contato: joao@email.com"
        resultados = self.detector[0][0] == "joao@email.com"

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
    
    def test_validar_email_valido(self):
        assert self.detector._validar("usuario@dominio.com") == True
        assert self.detector._validar("user.name@example.co.uk") == True
    
    def test_validar_email_sem_arroba(self):
        assert self.detector._validar("usuariodominio.com") == False
    
    def test_validar_email_sem_ponto_dominio(self):
        assert self.detector._validar("usuario@dominio") == False
    
    def test_validar_email_local_vazio(self):
        assert self.detector._validar("@dominio.com") == False
    
    def test_validar_email_dominio_vazio(self):
        assert self.detector._validar("usuario@") == False
    
    def test_validar_email_local_muito_longo(self):
        local_longo = "a" * 65
        email = f"{local_longo}@dominio.com"
        assert self.detector._validar(email) == False
    
    def test_validar_email_dominio_muito_longo(self):
        dominio_longo = "a" * 250 + ".com"
        email = f"usuario@{dominio_longo}"
        assert self.detector._validar(email) == False
    
    def test_mascarar_email_padrao(self):
        email = "joao@email.com"
        mascarado = self.detector.mascarar(email, nivel='padrao')
        
        assert mascarado == "j**o@email.com"
    
    def test_mascarar_email_padrao_nome_longo(self):
        email = "joaosilva@email.com"
        mascarado = self.detector.mascarar(email, nivel='padrao')
        
        assert mascarado == "j*******a@email.com"
        assert mascarado[0] == 'j'
        assert mascarado[-10] == 'a'
    
    def test_mascarar_email_curto(self):
        email = "ab@email.com"
        mascarado = self.detector.mascarar(email)
        
        assert mascarado == "a*@email.com"
    
    def test_mascarar_email_nivel_alto(self):
        email = "joao@email.com"
        mascarado = self.detector.mascarar(email, nivel='alto')
        
        assert mascarado == "*****@email.com"
    
    def test_mascarar_email_dominio(self):
        email = "joao@email.com"
        mascarado = self.detector.mascarar(email, nivel='dominio')
        
        assert mascarado == "joao@*****"
    
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
        
        assert mascarado == "*****@email.com"