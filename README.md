# Anonbr

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

Biblioteca Python para detectar e mascarar dados pessoais sensíveis em DataFrames.

Identifica automaticamente CPF, email e telefone em colunas e aplica mascaramento com três níveis de privacidade.

Desenvolvida com foco na **LGPD** (Lei Geral de Proteção de Dados) e no **tratamento de dados pessoais no contexto brasileiro**.

> *Os dados usados na pasta `exemples/` são fictícios, gerados por IA para simulação de dados pessoais.*


## Níveis de Mascaramento

| Dado| Alto | Padrão | Baixo | 
|-----|------|--------|-------|
| **CPF**| XXX.XXX.XXX-XX | XXX.567.XXX-XX | XXX.XX9.567-01 |
| **Telefone** | +XX (XX) XXXXX-XXXX | +55 (21) XXXXX-5678 | +55 (21) XXXX2-3456 |
| **E-Mail** | xxxxxxxxx@xxxxx.xxx | bxxxxxxx@gmail.com | xxxxosilva@gmail.com |

A biblioteca oferece três níveis de privacidade. Cada nível controla quanta informação fica visível após o mascaramento.

### Nível alto (mascara tudo)

Oculta toda a informação. Útil quando nenhum dado pode ser revelado.

| Tipo     | Entrada                         | Saída                            |
|----------|---------------------------------|----------------------------------|
| CPF      | 375.096.646-08                  | XXX.XXX.XXX-XX                   |
| Email    | bruno.silva@empresa.com.br       | xxxxxxxxxx@xxxxxxx.xxx.xx        |
| Telefone | (21) 98765-4321                 | (XX) XXXXX-XXXX                  |

### Nível padrão (equilíbrio)

Revela uma parte pequena para conferência, sem expor o dado completo.

| Tipo     | Entrada                         | Saída                            |
|----------|---------------------------------|----------------------------------|
| CPF      | 375.096.646-08                  | XXX.096.XXX-XX                   |
| Email    | bruno.silva@empresa.com.br       | bxxxxxxxxx@empresa.com.br        |
| Telefone | (21) 98765-4321                 | (21) XXXXX-4321                  |

### Nível baixo (revela mais)

Revela mais informação. Útil para conferência em ambientes controlados.

| Tipo     | Entrada                         | Saída                            |
|----------|---------------------------------|----------------------------------|
| CPF      | 375.096.646-08                  | XXX.XX6.646-08                   |
| Email    | bruno.silva@empresa.com.br       | xxxxosilva@empresa.com.br        |
| Telefone | (21) 98765-4321                 | (21) XXXX5-4321                  |

## Como funciona a detecção

A detecção é baseada em padrões visuais (regex), sem validação matemática. Isso garante que qualquer dado que pareça um CPF, email ou telefone será detectado e mascarado.

### CPF

O detector busca dois formatos: formatado (com pontos e hífen) e apenas números.

![lógica do cpf](images/logica_cpf.png)

> **Padrões que o detector reconhece:** **Formatado:** 123.456.789-00  *(3 dígitos, ponto, 3 dígitos, ponto, 3 dígitos, hífen, 2 dígitos)* **Não formatado:** 12345678900 *(11 dígitos seguidos)*


Quando o texto tem um CPF formatado como `375.096.646-08`, os dois padrões poderiam encontrar o mesmo número (um com pontuação, outro só os dígitos). Para evitar duplicatas, o método `_sobrepoe_formatado` verifica se as posições do match já foram cobertas por um CPF formatado encontrado antes.

---

### Email

O detector busca o padrão clássico de email: caracteres antes do `@`, seguidos
de um domínio com pelo menos um ponto.

![lógica do email](images/logica_email.png)

> **Padrão que o detector reconhece:**  
usuario@dominio.com  
nome.sobrenome@empresa.com.br  
usuario123@servidor.net  

O regex exige: pelo menos um caractere antes do `@`, pelo menos um ponto no domínio, e pelo menos duas letras na extensão (`.com`, `.br`, `.net`). Textos sem `@` são ignorados, pois não representam emails.

---

### Telefone

O detector cobre os formatos brasileiros mais comuns, do mais específico para o mais genérico.

![lógica do telefone](images/logica_telefone.png)

> **Padrões que o detector reconhece (em ordem de prioridade):**  
**1. Internacional:** +55 (21) 98765-4321, +55 21 987654321  
**2. Com DDD:** (21) 98765-4321, (21) 3456-7890  
**3. Apenas números:** 21987654321, 2134567890  

A ordem importa: o padrão internacional é testado primeiro. Se um número já foi encontrado por um padrão mais específico, os padrões seguintes ignoram aquela posição no texto. Isso evita que `+55 (21) 98765-4321`
seja detectado duas vezes (uma pelo padrão internacional e outra pelo padrão com DDD).

## Como funciona o mascaramento

O mascaramento segue três etapas em todos os detectores:

1. Extrair apenas os números/caracteres do dado original  
2. Montar a versão mascarada substituindo posições por `X` ou `x`  
3. Reconstruir o formato original (pontos, hifens, parênteses, `@`)  

Isso garante que o dado mascarado mantém a mesma estrutura visual do original.  

Por exemplo, um CPF formatado sai formatado, e um CPF sem pontuação sai sem pontuação.

## Caso de Uso

Você é DBA e recebe pedidos constantes de acesso ao banco para desenvolvimento. Não pode autorizar acesso direto (dados sensíveis em produção), mas a equipe precisa dos dados reais para trabalhar. Fazer exports manuais e editar cada campo sensível em Excel consome horas e é propenso a erros. O Anonbr automatiza esse processo: você exporta a tabela para CSV, executa a ferramenta (CPF: de 123.456.789-09 para XXX.XXX.789-XX, Email: de bruno@email.com para b***@email.com) e compartilha o arquivo com segurança. A equipe trabalha com dados reais sem expor informações pessoais.

## Execução

Para rodar a anonimização no arquivo, instale as dependências do projeto:

> **Com uv (gerenciamento de dependências)**  
`uv sync` e execute `uv run main.py`

ou  

> **Com ambiente virtual:**  
Crie o ambiente virtual: `python3 -m venv venv`, ative-o `source venv/bin/activate`, depois `pip install -e "."` ou `pip install -r requirements.txt`, execute o arquivo `python3 main.py`  

*Edite as linhas no arquivo `main.py`:*  

Antes de executar o arquivo que irá detectar, mascarar e salvar como CSV automaticamente, edite as seguintes linhas:

```python
# Pasta `exemples` onde você moverá o arquivo CSV original e substitua `dados_teste_validacao.csv` pelo nome do arquivo.
arquivo_entrada = os.path.join('exemples', 'dados_teste_validacao.csv')  

# Pasta `anonymized_data` dentro de `exemples` onde ficará salvo o arquivo de saída.
diretorio_saida = os.path.join('exemples', 'anonymized_data')

# `censurados.csv` é o nome do arquivo de saída dentro da pasta `anonymized_data`.
arquivo_saida = os.path.join(diretorio_saida, 'censurados.csv')
```  

**Edite o nível de mascaramento entre: `padrao`, `alto` ou `baixo`:**

```python
# Altere o nível do mascaramento conforme a prioridade:
anonimizador = Anonymizer(nivel='padrao')
```

![Nível de mascaramento](images/nivel_mascaramento.png)  

## Tecnologias  

- Python 3.8+
- pandas (processamento de DataFrames)
- re (expressoes regulares, biblioteca padrao)
- pytest (testes)
- uv (gerenciamento de dependencias)  

## Autor
***Yuri Pontes***  
**LinkedIn:** [Yuri Pontes](https://www.linkedin.com/in/yuri-pontes-4ba24a345/)  
**GitHub:** [yurivski](https://github.com/yurivski)

---
Este projeto nasceu de uma necessidade real identificada em posts do linkedin, onde DEVs e Analistas ficam P* da vida com DBAs que não dão acesso ao banco de dados para o desenvolvimento de seus respectivos projetos.