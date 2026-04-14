"""
Testes para o módulo anonbr/pattern_loader.py.

Verifica que:
  1. O arquivo config/patterns.yaml é carregado corretamente.
  2. As chaves esperadas existem no YAML.
  3. get_compiled() retorna listas de re.Pattern na ordem do YAML.
  4. get_compiled_by_name() retorna os nomes corretos como chaves.
  5. Os padrões compilados realmente detectam os textos esperados.
  6. O cache (lru_cache) funciona, um segundo call não relê o arquivo.
"""

import re
import pytest

from anonbr.pattern_loader import (
    load_raw,
    get_patterns,
    get_compiled,
    get_compiled_by_name,
    PATTERNS_FILE,
)


# Testes estruturais do YAML
class TestLoadRaw:
    def test_arquivo_yaml_existe(self):
        """O arquivo config/patterns.yaml deve existir no caminho calculado."""
        assert PATTERNS_FILE.exists(), f"Arquivo não encontrado: {PATTERNS_FILE}"

    def test_chaves_esperadas_presentes(self):
        """O YAML deve conter exatamente as chaves dos detectores do projeto."""
        raw = load_raw()
        for chave in ('cpf', 'cnpj', 'email', 'telefone'):
            assert chave in raw, f"Chave '{chave}' ausente no YAML"

    def test_cada_chave_tem_patterns(self):
        """Cada detector deve ter a lista 'patterns' com ao menos um item."""
        raw = load_raw()
        for chave in ('cpf', 'cnpj', 'email', 'telefone'):
            patterns = raw[chave].get('patterns', [])
            assert len(patterns) >= 1, f"'{chave}' não tem padrões definidos"

    def test_cada_padrao_tem_campos_obrigatorios(self):
        """Cada padrão deve ter os campos 'name' e 'regex'."""
        raw = load_raw()
        for chave, bloco in raw.items():
            for p in bloco.get('patterns', []):
                assert 'name' in p, f"[{chave}] padrão sem 'name': {p}"
                assert 'regex' in p, f"[{chave}] padrão sem 'regex': {p}"

    def test_cache_retorna_mesmo_objeto(self):
        """load_raw() deve retornar o mesmo objeto em chamadas consecutivas (lru_cache)."""
        primeiro = load_raw()
        segundo  = load_raw()
        assert primeiro is segundo, "load_raw deveria retornar objeto cacheado"


# Testes de get_patterns
class TestGetPatterns:
    def test_cpf_tem_dois_padroes(self):
        """CPF deve ter exatamente os padrões 'formatted' e 'unformatted'."""
        patterns = get_patterns('cpf')
        nomes = [p['name'] for p in patterns]
        assert 'formatted' in nomes
        assert 'unformatted' in nomes

    def test_cnpj_tem_dois_padroes(self):
        patterns = get_patterns('cnpj')
        nomes = [p['name'] for p in patterns]
        assert 'formatted' in nomes
        assert 'unformatted' in nomes

    def test_email_tem_padrao_standard(self):
        patterns = get_patterns('email')
        nomes = [p['name'] for p in patterns]
        assert 'standard' in nomes

    def test_telefone_tem_cinco_padroes(self):
        """Telefone deve ter os 5 padrões definidos no YAML."""
        patterns = get_patterns('telefone')
        nomes = [p['name'] for p in patterns]
        assert 'international' in nomes
        assert 'with_nono_digit_space' in nomes
        assert 'with_ddd' in nomes
        assert 'only_numbers' in nomes
        assert 'short' in nomes


# Testes de get_compiled
class TestGetCompiled:
    def test_retorna_lista_de_patterns(self):
        """get_compiled deve retornar uma lista de re.Pattern."""
        compiled = get_compiled('cpf')
        assert isinstance(compiled, list)
        for item in compiled:
            assert isinstance(item, type(re.compile('')))

    def test_cpf_dois_itens(self):
        assert len(get_compiled('cpf')) == 2

    def test_cnpj_dois_itens(self):
        assert len(get_compiled('cnpj')) == 2

    def test_email_um_item(self):
        assert len(get_compiled('email')) == 1

    def test_telefone_cinco_itens(self):
        """A lista de telefone deve ter 5 padrões na ordem do YAML."""
        assert len(get_compiled('telefone')) == 5

    def test_ordem_telefone_internacional_primeiro(self):
        """
        O primeiro padrão de telefone deve capturar números internacionais (+55).
        Garante que a ordem do YAML é preservada, padrão mais específico primeiro.
        """
        regexes = get_compiled('telefone')
        # índice 0 = international
        assert regexes[0].search('+55 (21) 98765-4321') is not None


# Testes de get_compiled_by_name
class TestGetCompiledByName:
    def test_retorna_dict(self):
        result = get_compiled_by_name('cpf')
        assert isinstance(result, dict)

    def test_cpf_chaves_corretas(self):
        result = get_compiled_by_name('cpf')
        assert 'formatted' in result
        assert 'unformatted' in result

    def test_cnpj_chaves_corretas(self):
        result = get_compiled_by_name('cnpj')
        assert 'formatted' in result
        assert 'unformatted' in result

    def test_email_chave_standard(self):
        result = get_compiled_by_name('email')
        assert 'standard' in result

    def test_telefone_chaves_corretas(self):
        result = get_compiled_by_name('telefone')
        assert 'international' in result
        assert 'with_nono_digit_space' in result
        assert 'with_ddd' in result
        assert 'only_numbers' in result
        assert 'short' in result


# Testes funcionais: os padrões detectam corretamente 
class TestPatternsFuncionais:
    """
    Verifica que os padrões carregados do YAML produzem os mesmos resultados
    que os padrões hardcoded anteriores. Qualquer alteração no YAML que quebre
    esses testes indica uma regressão.
    """

    def test_cpf_formatted_detecta(self):
        regex = get_compiled_by_name('cpf')['formatted']
        assert regex.search('375.096.646-08') is not None

    def test_cpf_formatted_nao_detecta_sem_separador(self):
        # Padrão formatado não deve detectar apenas dígitos
        regex = get_compiled_by_name('cpf')['formatted']
        # '37509664608' não tem separadores — não deve ser detectado por este padrão
        assert regex.fullmatch('37509664608') is None

    def test_cpf_unformatted_detecta(self):
        regex = get_compiled_by_name('cpf')['unformatted']
        assert regex.search('37509664608') is not None

    def test_cpf_unformatted_nao_detecta_sequencia_maior(self):
        # Lookbehind/lookahead deve rejeitar sequências maiores que 11 dígitos
        regex = get_compiled_by_name('cpf')['unformatted']
        assert regex.search('375096646081234') is None

    def test_cnpj_formatted_detecta(self):
        regex = get_compiled_by_name('cnpj')['formatted']
        assert regex.search('11.222.333/0001-81') is not None

    def test_cnpj_unformatted_detecta(self):
        regex = get_compiled_by_name('cnpj')['unformatted']
        assert regex.search('11222333000181') is not None

    def test_cnpj_unformatted_nao_detecta_sequencia_maior(self):
        regex = get_compiled_by_name('cnpj')['unformatted']
        assert regex.search('112223330001810000') is None

    def test_email_standard_detecta(self):
        regex = get_compiled_by_name('email')['standard']
        assert regex.search('usuario@empresa.com.br') is not None

    def test_email_standard_detecta_case_insensitive(self):
        # EmailDetector usa re.IGNORECASE, mas o padrão bruto aqui não tem flag —
        # apenas verificamos que o padrão puro captura o e-mail em minúsculas
        regex = re.compile(
            get_compiled_by_name('email')['standard'].pattern,
            re.IGNORECASE
        )
        assert regex.search('USUARIO@EMPRESA.COM') is not None

    def test_telefone_international_detecta(self):
        regex = get_compiled_by_name('telefone')['international']
        assert regex.search('+55 (21) 98765-4321') is not None

    def test_telefone_with_ddd_detecta(self):
        regex = get_compiled_by_name('telefone')['with_ddd']
        assert regex.search('(21) 98765-4321') is not None

    def test_telefone_only_numbers_detecta(self):
        regex = get_compiled_by_name('telefone')['only_numbers']
        assert regex.search('21987654321') is not None

    def test_telefone_only_numbers_nao_detecta_sequencia_maior(self):
        regex = get_compiled_by_name('telefone')['only_numbers']
        assert regex.search('219876543210000') is None
