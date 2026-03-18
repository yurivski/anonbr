import os
import fitz
import pytest
from anonbr.detectors.pdf import PDFDetector, detect_pdf, mask_pdf

# Criar PDFs de teste
@pytest.fixture
def sample_pdf(tmp_path):
    """Cria um PDF simples com CPF, email e telefone."""
    pdf_path = tmp_path / "sample.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "CPF: 375.096.646-08")
    page.insert_text((50, 80), "Email: teste@email.com")
    page.insert_text((50, 110), "Tel: (21) 98765-4321")
    doc.save(str(pdf_path))
    doc.close()
    return str(pdf_path)


@pytest.fixture
def pdf_multiple_data(tmp_path):
    """Cria um PDF com vários dados sensíveis na mesma linha."""
    pdf_path = tmp_path / "multiple.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "Dados: 375.096.646-08,teste@email.com,(21) 98765-4321")
    doc.save(str(pdf_path))
    doc.close()
    return str(pdf_path)


@pytest.fixture
def pdf_no_sensitive_data(tmp_path):
    """Cria um PDF sem dados sensíveis."""
    pdf_path = tmp_path / "clean.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "Este documento não contém dados sensíveis.")
    page.insert_text((50, 80), "Apenas texto comum pra teste.")
    doc.save(str(pdf_path))
    doc.close()
    return str(pdf_path)


@pytest.fixture
def pdf_multiple_pages(tmp_path):
    """Cria um PDF com dados sensíveis em múltiplas pág."""
    pdf_path = tmp_path / "multipage.pdf"
    doc = fitz.open()

    page1 = doc.new_page()
    page1.insert_text((50, 50), "CPF: 375.096.646-08")

    page2 = doc.new_page()
    page2.insert_text((50, 50), "Email: contato@empresa.com.br")

    page3 = doc.new_page()
    page3.insert_text((50, 50), "Tel: +55 21 98765-4321")

    doc.save(str(pdf_path))
    doc.close()
    return str(pdf_path)


@pytest.fixture
def pdf_unformatted_cpf(tmp_path):
    """Cria um PDF com CPF sem formatação."""
    pdf_path = tmp_path / "unformatted.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "CPF: 37509664608")
    doc.save(str(pdf_path))
    doc.close()
    return str(pdf_path)

# Testes de detecção
class TestPDFDetection:

    def test_detect_cpf(self, sample_pdf):
        detector = PDFDetector()
        findings = detector.detect(sample_pdf)

        assert 0 in findings
        types_found = [f['type'] for f in findings[0]]
        assert 'cpf' in types_found

    def test_detect_email(self, sample_pdf):
        detector = PDFDetector()
        findings = detector.detect(sample_pdf)

        assert 0 in findings
        types_found = [f['type'] for f in findings[0]]
        assert 'email' in types_found

    def test_detect_phone(self, sample_pdf):
        detector = PDFDetector()
        findings = detector.detect(sample_pdf)

        assert 0 in findings
        types_found = [f['type'] for f in findings[0]]
        assert 'phone' in types_found

    def test_detect_no_sensitive_data(self, pdf_no_sensitive_data):
        detector = PDFDetector()
        findings = detector.detect(pdf_no_sensitive_data)

        assert len(findings) == 0

    def test_detect_multiple_on_same_line(self, pdf_multiple_data):
        detector = PDFDetector()
        findings = detector.detect(pdf_multiple_data)

        assert 0 in findings
        types_found = [f['type'] for f in findings[0]]
        assert 'cpf' in types_found
        assert 'email' in types_found
        assert 'phone' in types_found

    def test_detect_multiple_pages(self, pdf_multiple_pages):
        detector = PDFDetector()
        findings = detector.detect(pdf_multiple_pages)

        assert 0 in findings  # CPF na pág. 1
        assert 1 in findings  # Email na pág. 2
        assert 2 in findings  # Telefone na pág. 3

    def test_detect_unformatted_cpf(self, pdf_unformatted_cpf):
        detector = PDFDetector()
        findings = detector.detect(pdf_unformatted_cpf)

        assert 0 in findings
        types_found = [f['type'] for f in findings[0]]
        assert 'cpf' in types_found

# Testes de padõres de mascaramento
class TestPDFMaskPatterns:

    def test_cpf_pattern_high(self):
        detector = PDFDetector(level='high')
        pattern = detector._cpf_mask_pattern('375.096.646-08')
        assert pattern == 'XXX.XXX.XXX-XX'

    def test_cpf_pattern_default(self):
        detector = PDFDetector(level='default')
        pattern = detector._cpf_mask_pattern('375.096.646-08')
        assert pattern == 'XXX.096.XXX-XX'

    def test_cpf_pattern_low(self):
        detector = PDFDetector(level='low')
        pattern = detector._cpf_mask_pattern('375.096.646-08')
        assert pattern == 'XXX.XXX.646-08'

    def test_cpf_pattern_unformatted_high(self):
        detector = PDFDetector(level='high')
        pattern = detector._cpf_mask_pattern('37509664608')
        assert pattern == 'XXXXXXXXXXX'

    def test_cpf_pattern_unformatted_default(self):
        detector = PDFDetector(level='default')
        pattern = detector._cpf_mask_pattern('37509664608')
        assert pattern == 'XXX096XXXXX'

    def test_email_pattern_high(self):
        detector = PDFDetector(level='high')
        pattern = detector._email_mask_pattern('teste@email.com')
        assert pattern == 'XXXXX@XXXXXXXXX'

    def test_email_pattern_default(self):
        detector = PDFDetector(level='default')
        pattern = detector._email_mask_pattern('teste@email.com')
        assert pattern == 'tXXXX@email.com'

    def test_email_pattern_low(self):
        detector = PDFDetector(level='low')
        pattern = detector._email_mask_pattern('teste@email.com')
        assert pattern == 'XXXte@email.com'

    def test_phone_pattern_high(self):
        detector = PDFDetector(level='high')
        pattern = detector._phone_mask_pattern('(21) 98765-4321')
        assert pattern == '(XX) XXXXX-XXXX'

    def test_phone_pattern_default(self):
        detector = PDFDetector(level='default')
        pattern = detector._phone_mask_pattern('(21) 98765-4321')
        assert pattern == '(21) XXXXX-4321'

    def test_phone_pattern_low(self):
        detector = PDFDetector(level='low')
        pattern = detector._phone_mask_pattern('(21) 98765-4321')
        assert pattern == '(21) XXXX5-4321'


# Testes de saída do mascaramento
class TestPDFMaskOutput:

    def test_mask_creates_output_file(self, sample_pdf, tmp_path):
        output_path = str(tmp_path / "output.pdf")
        detector = PDFDetector(level='default')
        summary = detector.mask(sample_pdf, output_path)

        assert os.path.exists(output_path)

    def test_mask_returns_summary(self, sample_pdf, tmp_path):
        output_path = str(tmp_path / "output.pdf")
        detector = PDFDetector(level='default')
        summary = detector.mask(sample_pdf, output_path)

        assert 'cpf' in summary
        assert 'email' in summary
        assert 'phone' in summary
        assert 'pages_processed' in summary
        assert summary['pages_processed'] >= 1

    def test_mask_no_sensitive_data_copies_file(self, pdf_no_sensitive_data, tmp_path):
        output_path = str(tmp_path / "output.pdf")
        detector = PDFDetector(level='default')
        summary = detector.mask(pdf_no_sensitive_data, output_path)

        assert os.path.exists(output_path)
        assert summary['pages_processed'] == 0

    def test_mask_output_is_valid_pdf(self, sample_pdf, tmp_path):
        output_path = str(tmp_path / "output.pdf")
        detector = PDFDetector(level='default')
        detector.mask(sample_pdf, output_path)

        # Verifica se a saída é um PDF válido que pode ser aberto
        doc = fitz.open(output_path)
        assert len(doc) >= 1
        doc.close()

    def test_mask_removes_original_text(self, sample_pdf, tmp_path):
        """Verifica se a redação remove o texto sensível original."""
        output_path = str(tmp_path / "output.pdf")
        detector = PDFDetector(level='high')
        detector.mask(sample_pdf, output_path)

        # Extrair texto do PDF mascarado
        doc = fitz.open(output_path)
        page = doc[0]
        text = page.get_text()
        doc.close()

        # O CPF original NÃO deve estar no texto extraído
        assert '375.096.646-08' not in text
        assert 'teste@email.com' not in text
        assert '98765-4321' not in text

    def test_mask_multiple_pages(self, pdf_multiple_pages, tmp_path):
        output_path = str(tmp_path / "output.pdf")
        detector = PDFDetector(level='default')
        summary = detector.mask(pdf_multiple_pages, output_path)

        assert summary['pages_processed'] >= 2

    def test_mask_high_level(self, sample_pdf, tmp_path):
        output_path = str(tmp_path / "output.pdf")
        detector = PDFDetector(level='high')
        summary = detector.mask(sample_pdf, output_path)

        assert os.path.exists(output_path)

    def test_mask_low_level(self, sample_pdf, tmp_path):
        output_path = str(tmp_path / "output.pdf")
        detector = PDFDetector(level='low')
        summary = detector.mask(sample_pdf, output_path)

        assert os.path.exists(output_path)


# Testes das funções auxiliares
class TestPDFHelpers:

    def test_helper_detect_pdf(self, sample_pdf):
        findings = detect_pdf(sample_pdf)
        assert 0 in findings

    def test_helper_mask_pdf(self, sample_pdf, tmp_path):
        output_path = str(tmp_path / "output.pdf")
        summary = mask_pdf(sample_pdf, output_path, level='default')

        assert os.path.exists(output_path)
        assert summary['pages_processed'] >= 1