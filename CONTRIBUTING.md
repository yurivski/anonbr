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
├── __init__.py        # API pública do pacote (imports e __all__)
├── anonymizer.py      # Orquestrador que processa DataFrames
├── pattern_loader.py  # Carregador central dos padrões regex do YAML
└── detectors/
    ├── cpf.py         # Detecção e mascaramento de CPF
    ├── cnpj.py        # Detecção e mascaramento de CNPJ
    ├── email.py       # Detecção e mascaramento de email
    ├── pdf.py         # Detecção e mascaramento em PDF
    └── telefone.py    # Detecção e mascaramento de telefone

config/
└── patterns.yaml      # Fonte única de todos os padrões regex

tests/
├── test_cpf.py
├── test_cnpj.py
├── test_email.py
├── test_pdf.py
├── test_pattern_loader.py
└── test_telefone.py

main.py  # Script de execução
```

Cada detector segue o mesmo padrão: uma classe com métodos `detect` e `mask`, e funções auxiliares (helpers) fora da classe para uso rápido. A detecção é baseada em padrões visuais via regex, sem validação matemática. Isso é intencional: para anonimização, qualquer dado que pareça um CPF, email ou telefone deve ser mascarado.

**Os padrões regex não ficam no código dos detectores.** Todos são definidos no `config/patterns.yaml` e carregados via `pattern_loader`. Isso centraliza as expressões regulares num único lugar e evita duplicação entre os detectores de CSV e PDF.

O mascaramento tem três níveis: high (mascara tudo), default (equilíbrio) e low (revela mais). Novos detectores devem seguir esse mesmo padrão.

## Sugestões para contribuição

O projeto precisa de ajuda em diversas frentes. Algumas ideias: implementar novos detectores (RG, CEP, CNH, PIS, etc), suporte a processamento em batch com múltiplos arquivos, etc.

> [!TIP]
> Não se limite a essa lista. Se identificar algo que pode melhorar, abra uma issue ou mande um PR.

## Como adicionar um novo padrão

Aqui está o caminho mais direto para quem quer adicionar um padrão de dado novo ou uma variação de padrão existente.

### Variação de padrão existente

Se o dado já tem um detector (CPF, CNPJ, email, telefone) e você quer adicionar uma nova forma de escrita que ainda não é reconhecida, o fluxo é simples:

**1. Abra o `config/patterns.yaml` e localize a chave do detector.**

Cada chave tem uma lista `patterns`. Cada item da lista tem:

```yaml
- name: nome_do_padrao        # identificador único, usado pelo código
  regex: r'sua_expressao'     # expressão regular no formato r'...'
  description: descrição      # texto legível explicando o padrão
```

**2. Adicione seu padrão ao final da lista, respeitando a ordem de prioridade.**

Os padrões são carregados na ordem em que aparecem no YAML. Padrões mais específicos devem vir antes dos mais genéricos para que a deduplicação por posição funcione corretamente.

> [!IMPORTANT]
> Use sempre a notação `r'...'` na chave `regex`. O `pattern_loader` remove automaticamente esse prefixo antes de compilar, mas ele precisa estar presente no YAML.

**3. Verifique se o detector existente consegue usar o novo padrão sem alteração.**

Para detectores que carregam os padrões como lista ordenada (como `telefone.py`), o novo padrão é capturado automaticamente. Para detectores que acessam por nome (como `cpf.py`), pode ser necessário adicionar uma linha no `__init__` do detector para carregar o novo nome.

**4. Escreva testes para o novo padrão** no arquivo de testes correspondente em `tests/`.

---

### Detector completamente novo

Se o dado ainda não tem nenhum suporte (RG, CEP, CNH, etc.), o processo tem mais etapas mas segue sempre o mesmo padrão:

**1. Defina os padrões no `config/patterns.yaml`** com uma nova chave no nível raiz:

```yaml
rg:
  description: "Registro Geral"
  priority: 4
  patterns:
    - name: formatted
      regex: r'seu_regex_aqui'
      description: "RG formatado com ponto e traço"
    - name: unformatted
      regex: r'outro_regex'
      description: "RG apenas com dígitos"
```

**2. Crie o arquivo do detector em `anonbr/detectors/nome_dado.py`** seguindo a estrutura dos detectores existentes:

```python
from anonbr.pattern_loader import get_compiled_by_name

class NomeDadoDetector:
    def __init__(self):
        compiled = get_compiled_by_name('chave_no_yaml')
        self.formatted_regex = compiled['formatted']
        self.unformatted_regex = compiled['unformatted']

    def detect(self, text: str) -> list:
        ...

    def mask(self, value: str, level: str = 'default') -> str:
        ...

# Funções auxiliares
def detect_nome_dado(text: str) -> list:
    return NomeDadoDetector().detect(text)

def mask_nome_dado(value: str, level: str = 'default') -> str:
    return NomeDadoDetector().mask(value, level)
```

**3. Exporte o detector em `anonbr/__init__.py`** para que fique disponível na API pública do pacote.

**4. Integre ao `anonymizer.py`** se quiser que o novo detector seja chamado automaticamente no fluxo principal de CSV.

**5. Integre ao `pdf.py`** se quiser suporte em PDF também. Nesse caso, adicione o padrão ao dict `self.patterns` e implemente o método `_nome_dado_mask_pattern`.

**6. Escreva os testes** em `tests/test_nome_dado.py`. Cubra pelo menos: detecção do formato principal, detecção de variações, mascaramento nos três níveis e casos que não devem ser detectados (falsos positivos).

> [!NOTE]
> Antes de criar um detector novo, confira se o dado que você quer detectar tem um padrão visual suficientemente distinto para não gerar falsos positivos em excesso. A validação aqui é sempre visual, não matemática.

---

## Regras gerais

* Escreva testes para qualquer código novo
* Não quebre testes existentes
* Mantenha o código legível e com comentários onde necessário
* Textos de outputs em PT-BR, devido ao foco atual em dados com padrão brasileiro