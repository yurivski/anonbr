## Histórico de Atualizações e Versões

| **Data** | **Início** | **Fim** | **Versão** | **Atualização** | **Descrição** |
|:--------:|:----------:|:-------:|:----------:|:-------------:|:---------------:|
|29/03/2026|11h|12h|v1.2.1|Corrigir bugs, melhorar performance|Corrige bugs de falsos positivos de CNPJ, CPF e telefone em sequências de dígitos maiores que os padrões definidos.|
|23/03/2026|10h|15h|v1.2.0|Adicionar nova funcionalidade, corrigir de bugs e otimizar desempenho de detecção|Adicionar detecção e censura de CNPJ em arquivos CSV e PDF, adicionar tratamento de erros com warnings, otimizar detecção de dados e identificação de tipo.|
|22/03/2026|11h30|13h30|v1.1.3|Adicionar novo estilo|Adicionar novo padrão regex para detecção de telefone, adicionar exibição de barra de progresso ao CLI.|
|21/03/2026|14h30|15h30|v1.1.2|Correção de bug|Define a lista de padrões de telefones como um sistema de redundância para detecção de padrões visuais, definidos por uma série de inconsistências em diferentes tipos de PDFs para otimizar a identificação dos dados alvos.|
|20/03/2026|10h|14h30|v1.1.1|Correção de bugs|Detectar e-mails corporativos em URLs de redirecionamento e não censurar, tendo em vista não ser um dado pessoal. Detectar e censurar números de telefones em listas separadas por "/".|
|18/03/2026| - | - |v1.1.0|Nova funcionalidade|Censurar de dados em PDF sem quebrar o formato do arquivo.|
|15/03/2026| - | - |v1.0.0| Criação da ferramenta|Detectar e censurar CPF, E-Mail e Telefone apenas em arquivos CSV.|