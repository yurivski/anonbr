"""
Testes de detecção e mascaramento de CNPJ.

Os padrões regex não estão mais hardcoded em cnpj.py, 
eles são carregados de config/patterns.yaml via pattern_loader.

O comportamento externo (o que detect() e mask() retornam) não muda;
apenas a origem dos padrões mudou. Os testes abaixo continuam válidos
e garantem que a nova fonte de padrões produz os mesmos resultados.

Para testar o carregamento do YAML em si, veja tests/test_pattern_loader.py.
"""

import pytest
import yaml
from pathlib import Path
from anonbr.detectors.cnpj import CNPJDetector
from anonbr.detectors.cnpj import detect_cnpj
from anonbr.detectors.cnpj import mask_cnpj

# Carrega patterns.yaml uma vez
PATTERNS = yaml.safe_load(
    Path("config/patterns.yaml").read_text(encoding="utf-8")
)

# Extrai os dados do detector específico
DETECTOR_CONFIG = PATTERNS["cnpj"]

# Fixtures
@pytest.fixture
def detector():
    """Cria uma instância do detector."""
    return CNPJDetector()

# Testes de detecção parametrizados pelo YAML
# Extrai test_cases de cada padrão pra usar no parametrize
def _build_detect_cases():
    """Monta lista de (input, expected, description) a partir do YAML."""
    cases = []
    for pattern in DETECTOR_CONFIG.get("patterns", []):
        pattern_name = pattern.get("name", "unknown")
        for tc in pattern.get("test_cases", []):
            cases.append(
                pytest.param(
                    tc["input"],
                    tc["expected"],
                    id=f"{pattern_name}_{tc.get('description', 'case')}"
                )
            )
    return cases


@pytest.mark.parametrize("text_input, expected", _build_detect_cases())
def test_detect(detector, text_input, expected):
    """Testa detecção usando os casos definidos no YAML."""
    results = detector.detect(text_input)
    found_texts = [r[0] for r in results]
    assert found_texts == expected


# Testes de mascaramento parametrizados pelo YAML
def _build_mask_cases():
    """Monta lista de (value, level, expected) a partir do YAML."""
    cases = []
    for mc in DETECTOR_CONFIG.get("mask_cases", []):
        cases.append(
            pytest.param(
                mc["input"],
                mc["level"],
                mc["expected"],
                id=f"{mc['level']}_{mc.get('description', 'case')}"
            )
        )
    return cases


@pytest.mark.parametrize("value, level, expected", _build_mask_cases())
def test_mask(detector, value, level, expected):
    """Testa mascaramento usando os casos definidos no YAML."""
    result = detector.mask(value, level=level)
    assert result == expected


# Testes de helpers
def test_helper_detect():
    """Testa a função helper de detecção."""
    # Usa o primeiro test_case do primeiro padrão como teste básico
    first_case = DETECTOR_CONFIG["patterns"][0]["test_cases"][0]
    results = detect_cnpj(first_case["input"])
    found_texts = [r[0] for r in results]
    assert found_texts == first_case["expected"]


def test_helper_mask():
    """Testa a função helper de mascaramento."""
    first_case = DETECTOR_CONFIG["mask_cases"][0]
    result = mask_cnpj(first_case["input"], level=first_case["level"])
    assert result == first_case["expected"]
