"""
Testes de detecção e mascaramento de e-mail.

A partir da refatoração para YAML, o padrão regex não está mais hardcoded
em email.py, é carregado de config/patterns.yaml via pattern_loader.

O comportamento externo (o que detect() e mask() retornam) não muda;
apenas a origem do padrão mudou. Os testes abaixo continuam válidos
e garantem que a nova fonte de padrões produz os mesmos resultados.

Para testar o carregamento do YAML em si, veja tests/test_pattern_loader.py.
"""

import pytest
from anonbr.detectors.email import EmailDetector, detect_email, mask_email

class TestEmailDetector:
    def setup_method(self):
        self.detector = EmailDetector()
    
    def test_detect_simple_email(self):
        text = "Contato: joao@email.com"
        results = self.detector.detect(text)
        
        assert results[0][0] == "joao@email.com"

    def test_detect_email_with_dot(self):
        text = "Email: joao.silva@empresa.com.br"
        results = self.detector.detect(text)
        
        assert len(results) == 1
        assert results[0][0] == "joao.silva@empresa.com.br"
    
    def test_detect_email_with_plus(self):
        text = "Email: usuario+tag@dominio.com"
        results = self.detector.detect(text)
        
        assert len(results) == 1
        assert results[0][0] == "usuario+tag@dominio.com"
    
    def test_detect_email_with_numbers(self):
        text = "Contato: user123@test456.com"
        results = self.detector.detect(text)
        
        assert len(results) == 1
        assert results[0][0] == "user123@test456.com"
    
    def test_detect_multiple_emails(self):
        text = "Contatos: joao@email.com e maria@outro.com.br"
        results = self.detector.detect(text)
        
        assert len(results) == 2
    
    def test_detect_subdomain_email(self):
        text = "Email: usuario@sub.dominio.com.br"
        results = self.detector.detect(text)
        
        assert len(results) == 1
    
    def test_mask_email_default(self):
        email = "joao@email.com"
        masked = self.detector.mask(email, level='default')
        
        assert masked == "jxxx@email.com"
    
    def test_mask_email_default_long_name(self):
        email = "joaosilva@email.com"
        masked = self.detector.mask(email, level='default')
        
        assert masked == "jxxxxxxxx@email.com"
        assert masked[0] == 'j'
    
    def test_mask_short_email(self):
        email = "ab@email.com"
        masked = self.detector.mask(email)
        
        assert masked == "ax@email.com"
    
    def test_mask_email_high_level(self):
        email = "joao@email.com"
        masked = self.detector.mask(email, level='high')
        
        assert masked == "xxxx@xxxxx.xxx"

    def test_detect_email_not_in_url(self):
        text = "Contato: usuario@empresa.com"
        results = self.detector.detect(text)
        assert len(results) == 1

    def test_detect_email_with_slash_no_protocol(self):
        text = "Lista: email1@empresa.com/email2@empresa.com"
        results = self.detector.detect(text)
        assert len(results) == 2
    
    def test_mask_email_without_at(self):
        email = "emailinvalido"
        masked = self.detector.mask(email)
        
        assert masked == email

class TestEmailHelpers:

    def test_helper_detect_email(self):
        text = "Email: teste@exemplo.com"
        results = detect_email(text)
        
        assert len(results) == 1
        assert "teste@exemplo.com" in results[0][0]
    
    def test_helper_mask_email(self):
        email = "joao@email.com"
        masked = mask_email(email)
        
        assert "@email.com" in masked
        assert masked[0] == 'j'
    
    def test_helper_mask_email_high_level(self):
        email = "joao@email.com"
        masked = mask_email(email, level='high')
        
        assert masked == "xxxx@xxxxx.xxx"