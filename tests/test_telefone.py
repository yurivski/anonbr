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

    def test_detect_phone_separated_by_slash(self):
        text = "Telefones: 21987654321/21876543210"
        results = self.detector.detect(text)
        assert len(results) == 2

    def test_detect_phone_formatted_separated_by_slash(self):
        text = "Fone: (21) 98765-4321/(21) 87654-3210"
        results = self.detector.detect(text)
        assert len(results) == 2

    def test_detect_phone_with_slash_and_spaces(self):
        text = "Tel: 21987654321 / 21876543210"
        results = self.detector.detect(text)

        assert len(results) == 2

    def test_detect_phone_separated_by_pipe(self):
        text = "Telefones: 21987654321|21876543210"
        results = self.detector.detect(text)

        assert len(results) == 2

    def test_detect_phone_separated_by_pipe_and_spaces(self):
        text = "Telefones: 21987654321 | 21876543210"
        results = self.detector.detect(text)

        assert len(results) == 2

    def test_detect_ninth_digit_separated(self):
        text = "Celular: (21) 9 9876-5432"
        results = self.detector.detect(text)

        assert len(results) == 1
        assert results[0][0] == "(21) 9 9876-5432"

    def test_no_detect_sequence_longer_than_phone(self):
        text = "Código: 219876543210000"
        results = self.detector.detect(text)
        assert len(results) == 0

    def test_no_detect_unformatted_phone_adjacent_to_digits(self):
        text = "ID: 121987654321"
        results = self.detector.detect(text)
        assert len(results) == 0


class TestPhoneHelpers:

    def test_helper_detect_phone_separated_by_pipe(self):
        text = "Fones: 21987654321|21876543210"
        results = detect_phone(text)
        assert len(results) == 2

    def test_detect_phone_separated_by_pipe_and_spaces(self):
        text = "Telefones: 21987654321 | 21876543210"
        results = detect_phone(text)
        
        assert len(results) == 2

    def test_helper_detect_ninth_digit_separated(self):
        text = "Cel: (21) 9 9876-5432"
        results = detect_phone(text)
        
        assert len(results) == 1

    def test_helper_detect_phone_separated_by_slash(self):
        text = "Fones: 21987654321/21876543210"
        results = detect_phone(text)
        
        assert len(results) == 2

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

    def test_helper_no_detect_sequence_longer_than_phone(self):
        text = "Código: 219876543210000"
        results = detect_phone(text)
        assert len(results) == 0

    def test_helper_no_detect_unformatted_phone_adjacent_to_digits(self):
        text = "ID: 121987654321"
        results = detect_phone(text)
        assert len(results) == 0