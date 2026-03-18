# Como contribuir para o Anonbr

O Anonbr tem como objetivo transformar dados sensíveis de formato padrão brasileiro para que documentos (atualmente apenas CSV) possam ser compartilhados de forma segura, sem exposição de dados pessoais, conforme a LGPD.

> Contribua sem compromisso, **talvez isso se transforme em algo grande, talvez não**, o que importa é **praticar e estudar**. O projeto foi criado para estimular programadores de todos os níveis a praticarem **Python, testes, versionamento e boas praticas de engenharia de dados**, aplicados a um problema real: anonimizacao de dados pessoais no contexto brasileiro.

***Contribuições de qualquer nível são bem-vindas, desde correção de typos até novos detectores.***

## Configurando o ambiente

1. Faça um fork do repositório e clone localmente:

```bash
git clone https://github.com/seu-usuario/anonbr.git
cd anonbr
```

2. Instale as dependências com uv:

```bash
uv sync --group dev 
```

Isso instala o projeto e as ferramentas de desenvolvimento (pytest, pytest-cov).

3. Verifique que os testes passam antes de comecar:

```bash
uv run pytest tests/ -v
```

ou, sem pyproject:

```bash
# Crie e ative seu ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instale as dependências do projeto
pip install -r requirements.txt
pip install -e .

# Execute o teste
pytest tests/ -v
```
Se todos passarem, o ambiente está pronto.

## Estrutura do projeto

Antes de contribuir, entenda como o projeto está organizado:

```bash
anonbr/
├── __init__.py   # API pública do pacote (imports e __all__)
├── anonymizer.py  # Orquestrador que processa DataFrames
└── detectors/
    ├── cpf.py  # Detecção e mascaramento de CPF
    ├── email.py  # Detecção e mascaramento de email
    ├── pdf.py  # Detecção e mascaramento de PDF
    └── telefone.py  # Detecção e mascaramento de telefone

tests/
├── test_cpf.py
├── test_email.py
├── test_pdf.py 
└── test_telefone.py

main.py  # Script de execucao
```
Cada detector segue o mesmo padrão: uma classe com métodos `detect` e `mask`, e funções auxiliares (helpers) fora da classe para uso rápido. A detecção é baseada em padrões visuais via regex, sem validação matemática. Isso é intencional: para anonimização, qualquer dado que pareça um CPF, email ou telefone deve ser mascarado.

O mascaramento tem três níveis: high (mascara tudo), default (equilíbrio) e low (revela mais). Novos detectores devem seguir esse mesmo padrão.

## Sugestões para contribuição

O projeto precisa de ajuda em diversas frentes. Algumas ideias: corrigir erros de escrita na documentação, implementar novos detectores (CNPJ, RG, CEP, CNH), suporte a processamento em batch com múltiplos arquivos, etc.

> Não se limite a essa lista. Se identificar algo que pode melhorar, abra uma issue ou mande um PR.

## Regras gerais

- Escreva testes para qualquer código novo
- Não quebre testes existentes
- Mantenha o código legível e com comentários onde necessário
- Textos de outputs em PT-BR, devido ao foco atual em dados com padrão brasileiro