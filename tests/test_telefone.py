import pytest
from anonbr.detectors.telefone import PhoneDetector, detect_phone, mask_phone


class TestPhoneDetector:
    def setup_method(self):
        self.detector = PhoneDetector()
    
    def test_detect_formatted_cellphone(self):
        text = "Telefone: (21) 98765-4321"
        results = self.detector.detect(text)
        
        assert len(results) == 1
        assert "(21) 98765-4321" in results[0][0]
    
    def test_detect_formatted_landline(self):
        text = "Fixo: (21) 3456-7890"
        results = self.detector.detect(text)
        
        assert len(results) == 1
    
    def test_detect_unformatted_cellphone(self):
        text = "WhatsApp: 21987654321"
        results = self.detector.detect(text)
        
        assert len(results) == 1
        assert "21987654321" in results[0][0]
    
    def test_detect_unformatted_landline(self):
        text = "Telefone: 2134567890"
        results = self.detector.detect(text)
        
        assert len(results) == 1
    
    def test_detect_with_country_code(self):
        text = "Internacional: +55 21 98765-4321"
        results = self.detector.detect(text)
        
        assert len(results) == 1
        assert "+55" in results[0][0]
    
    def test_detect_multiple_phones(self):
        text = "Cel: (21) 98765-4321 Fixo: (21) 3456-7890"
        results = self.detector.detect(text)
        
        assert len(results) == 2
    
    def test_mask_cellphone_default(self):
        phone = "(21) 98765-4321"
        masked = self.detector.mask(phone, level='default')
        
        assert "4321" in masked
        assert "XXX" in masked
    
    def test_mask_landline_default(self):
        phone = "(21) 3456-7890"
        masked = self.detector.mask(phone, level='default')
        
        assert "7890" in masked
        assert "XXX" in masked
    
    def test_mask_cellphone_high_level(self):
        phone = "(21) 98765-4321"
        masked = self.detector.mask(phone, level='high')
        
        assert "XXXX" in masked
        assert "4321" not in masked
    
    def test_mask_preserves_parentheses_format(self):
        phone = "(21) 98765-4321"
        masked = self.detector.mask(phone)
        
        assert "(" in masked
        assert ")" in masked
        assert "-" in masked
    
    def test_mask_preserves_no_parentheses_format(self):
        phone = "21987654321"
        masked = self.detector.mask(phone)
        
        assert "(" not in masked
        assert ")" not in masked
        assert "-" not in masked
    
    def test_mask_with_country_code(self):
        phone = "+55 (21) 98765-4321"
        masked = self.detector.mask(phone)
        
        assert "+55" in masked
        assert "4321" in masked
    
    def test_mask_minimum_level(self):
        phone = "(21) 98765-4321"
        masked = self.detector.mask(phone, level='default')
        
        assert "(21)" in masked
        assert "4321" in masked

class TestPhoneHelpers:
    def test_helper_detect_phone(self):
        text = "Telefone: (21) 98765-4321"
        results = detect_phone(text)
        
        assert len(results) == 1
    
    def test_helper_mask_phone(self):
        phone = "(21) 98765-4321"
        masked = mask_phone(phone)
        
        assert "4321" in masked
        assert "XXX" in masked
    
    def test_helper_mask_phone_high_level(self):
        phone = "(21) 98765-4321"
        masked = mask_phone(phone, level='high')
        
        assert "4321" not in masked