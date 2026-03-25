## Relatório de bugs e vulnerabilidades atuais da ferramenta

**Título:** Falso positivo   
**Versão:** 1.2.0   
**Descrição:** Ainda não analisa o contexto e, em uma sequência grande de dígitos sem formatação, a ferramenta confunde os primeiros 14 com CNPJ e sequências com 12 ou 12+1 têm os primeiros 11 confundidos com CPF. Isso inclui detecção de dígitos que foram, intencionalmente ou não, ocultados no documento, por exemplo: se você digita algo e sublinha na mesma cor, o texto fica "oculto", mas a ferramenta ainda detecta e censura se os dados sublinhados forem alvos.

**Título:** Imagens   
**Versão:** 1.2.0   
**Descrição:** A ferramenta ainda não detecta dados em imagens exportadas como PDF. No entanto, reconhece em arquivos digitalizados.
