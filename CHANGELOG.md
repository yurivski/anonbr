<div align="center">

![Banner](images/Anonbr_banner.png)

# Changelog - Anonbr
Histórico de versões do anonbr.

</div>
<br>

## v0.5.0 — Comandos isolados por tipo de dado e modo detecção

Adição de filtros de tipo de dado (`--cpf`, `--email`, `--phone`) e modo detecção sem mascaramento (`--detect`) à CLI. Refatoração de `Anonymizer` e `PDFDetector` para aceitar o parâmetro `data_types`.

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
<td>2026-04-22</td>
<td>v0.5.0</td>
<td>feat/refact</td>
<td>Adicionar filtros de tipo de dado e modo detecção à CLI</td>
<td>Adicionar argumentos <code>--cpf</code>, <code>--email</code> e <code>--phone</code> à CLI para executar o sistema isoladamente para um ou mais tipos de dado; adicionar argumento <code>--detect</code> para executar apenas a detecção sem mascarar os dados, tanto em modo completo quanto em modo filtrado; refatorar <code>Anonymizer</code> para aceitar <code>data_types</code> no construtor, inicializando apenas os detectores necessários e filtrando o relatório e a anonimização conforme os tipos ativos; refatorar <code>PDFDetector</code> para aceitar <code>data_types</code> no construtor, filtrando a property <code>patterns</code> e a ordem de aplicação em <code>_detect_in_text</code>, incluindo a segunda varredura de telefones separados por <code>/</code>; atualizar a string de uso (<code>usage</code>) do parser com os novos comandos.</td>
</tr>
</tbody>
</table>

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
<td>2026-04-14</td>
<td>v0.4.2</td>
<td>perf/fix</td>
<td>Otimizar deduplicação de matches e corrigir fusão de barras no PDF</td>
<td>Substituir o <code>set</code> de posições individuais (<code>used_positions</code>) por lista ordenada de intervalos (<code>used_intervals</code>) com busca binária via <code>bisect</code> em <code>_detect_in_text</code>: verificação de sobreposição passa de O(comprimento do match) para O(log n) em ambas as varreduras; corrigir tolerância de fusão de bounding boxes adjacentes em <code>_build_mask_map</code> de <code>&lt; 1</code> para <code>&lt; 2</code> pontos, evitando fragmentação de barras de redação na mesma linha em PDFs com variação de <code>top</code> por fonte.</td>
</tr>
<tr>
<td>2026-04-14</td>
<td>v0.4.1</td>
<td>refact</td>
<td>Remover suporte à notação <code>r'...'</code> no YAML</td>
<td>Remover a função <code>_strip_python_raw</code> do <code>pattern_loader</code> e a classe <code>TestStripPythonRaw</code> de <code>test_pattern_loader</code>, pois os padrões regex no <code>config/patterns.yaml</code> já não usam a notação <code>r'...'</code>; <code>get_compiled</code> e <code>get_compiled_by_name</code> passam o campo <code>regex</code> diretamente para <code>re.compile()</code>.</td>
</tr>
<tr>
<td>2026-04-11</td>
<td>v0.4.0</td>
<td>feat/refact</td>
<td>Centralizar padrões regex, refatorar detectores e criar suite de testes</td>
<td>Adicionar <code>pattern_loader</code> como ponto central de leitura do <code>config/patterns.yaml</code>; adicionar carregadores de padrão com acesso direto por nome ao YAML; refatorar todos os detectores para importar padrões via <code>pattern_loader</code>, removendo strings regex hardcoded do código; adicionar comentários detalhados em todas as funções dos detectores; documentar nos detectores a fonte dos padrões carregados; criar <code>test_pattern_loader</code> com testes organizados em classes, cobrindo estrutura do YAML, ordem dos padrões, nomes corretos e detecção funcional.</td>
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
