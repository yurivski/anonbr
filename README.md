# Anonbr

Anonimização automática de dados pessoais em DataFrames Python.

![Status](https://img.shields.io/badge/status-em%20desenvolvimento-yellow.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## Objetivo

Detectar e anonimizar automaticamente:
- CPF (com validação de dígitos)
- Email
- Telefone (padrão BR)
- Nomes completos

## Caso de Uso

Você é DBA e recebe pedidos constantes de acesso ao banco para desenvolvimento. Não pode autorizar acesso direto (dados sensíveis em produção), mas a equipe precisa dos dados reais para trabalhar. Fazer exports manuais e editar cada campo sensível em Excel consome horas e é propenso a erros. O Anonbr automatiza esse processo: você exporta a tabela para CSV, executa a ferramenta (CPF: de 123.456.789-09 para XXX.XXX.789-XX, Email: de joao@email.com para j***@email.com) e compartilha o arquivo com segurança. A equipe trabalha com dados reais sem expor informações pessoais.

## Exemplo
```python
# Antes
CPF: 123.456.789-09
Email: joao.silva@empresa.com.br
Telefone: (11) 98765-4321

# Depois
CPF: XXX.XXX.789-XX
Email: j***o@empresa.com.br
Telefone: (XX) XXXXX-4321
```

## Status

Projeto em desenvolvimento ativo.

