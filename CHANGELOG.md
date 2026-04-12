<div align="center">

# Changelog - Anonbr

Histórico de versões do anonbr.

</div>

---

## v0.4.0 — Centralização de padrões regex

Extração dos padrões regex para um YAML centralizado, refatoração de todos os detectores para importar desse arquivo e suite de testes para o carregador de padrões.

<table>
<thead>
<tr>
<th>Data</th>
<th>Versão</th>
<th>Tipo</th>
<th>Resumo</th>
<th>Detalhes</th>
</tr>
</thead>
<tbody>
<tr>
<td>2026-04-11</td>
<td>v0.4.0</td>
<td>feat/refact</td>
<td>Centralizar padrões regex, refatorar detectores e criar suite de testes</td>
<td>Adicionar <code>pattern_loader</code> como ponto central de leitura do <code>config/patterns.yaml</code>; adicionar carregadores de padrão com acesso direto por nome ao YAML; refatorar todos os detectores para importar padrões via <code>pattern_loader</code>, removendo strings regex hardcoded do código; adicionar comentários detalhados em todas as funções dos detectores; documentar nos detectores a fonte dos padrões carregados; criar <code>test_pattern_loader</code> com 37 testes organizados em 6 classes, cobrindo estrutura do YAML, remoção da notação <code>r'...'</code>, ordem dos padrões, nomes corretos e detecção funcional.</td>
</tr>
</tbody>
</table>

---

## v0.3.0 — Detecção de CNPJ e otimizações

Suporte a CNPJ em CSV e PDF, tratamento de erros e correções de falsos positivos.

<table>
<thead>
<tr>
<th>Data</th>
<th>Versão</th>
<th>Tipo</th>
<th>Resumo</th>
<th>Detalhes</th>
</tr>
</thead>
<tbody>
<tr>
<td>2026-03-29</td>
<td>v0.3.1</td>
<td>fix</td>
<td>Corrigir bugs, melhorar performance</td>
<td>Corrige bugs de falsos positivos de CNPJ, CPF e telefone em sequências de dígitos maiores que os padrões definidos.</td>
</tr>
<tr>
<td>2026-03-23</td>
<td>v0.3.0</td>
<td>feat</td>
<td>Adicionar nova funcionalidade, corrigir bugs e otimizar desempenho de detecção</td>
<td>Adicionar detecção e censura de CNPJ em arquivos CSV e PDF, adicionar tratamento de erros com warnings, otimizar detecção de dados e identificação de tipo.</td>
</tr>
</tbody>
</table>

---

## v0.2.0 — Suporte a PDF e novas detecções

Censura de dados em PDF, detecção aprimorada de telefone e correções de comportamento.

<table>
<thead>
<tr>
<th>Data</th>
<th>Versão</th>
<th>Tipo</th>
<th>Resumo</th>
<th>Detalhes</th>
</tr>
</thead>
<tbody>
<tr>
<td>2026-03-22</td>
<td>v0.2.3</td>
<td>feat</td>
<td>Adicionar novo estilo</td>
<td>Adicionar novo padrão regex para detecção de telefone, adicionar exibição de barra de progresso ao CLI.</td>
</tr>
<tr>
<td>2026-03-21</td>
<td>v0.2.2</td>
<td>fix</td>
<td>Correção de bug</td>
<td>Define a lista de padrões de telefones como um sistema de redundância para detecção de padrões visuais, definidos por uma série de inconsistências em diferentes tipos de PDFs para otimizar a identificação dos dados alvos.</td>
</tr>
<tr>
<td>2026-03-20</td>
<td>v0.2.1</td>
<td>fix</td>
<td>Correção de bugs</td>
<td>Detectar e-mails corporativos em URLs de redirecionamento e não censurar, tendo em vista não ser um dado pessoal. Detectar e censurar números de telefones em listas separadas por "/".</td>
</tr>
<tr>
<td>2026-03-18</td>
<td>v0.2.0</td>
<td>feat</td>
<td>Nova funcionalidade</td>
<td>Censurar dados em PDF sem quebrar o formato do arquivo.</td>
</tr>
</tbody>
</table>

---

## v0.1.0 — Criação da ferramenta

Versão inicial: detecção e censura de CPF, E-Mail e Telefone em arquivos CSV.

<table>
<thead>
<tr>
<th>Data</th>
<th>Versão</th>
<th>Tipo</th>
<th>Resumo</th>
<th>Detalhes</th>
</tr>
</thead>
<tbody>
<tr>
<td>2026-03-15</td>
<td>v0.1.0</td>
<td>feat</td>
<td>Criação da ferramenta</td>
<td>Detectar e censurar CPF, E-Mail e Telefone apenas em arquivos CSV.</td>
</tr>
</tbody>
</table>
