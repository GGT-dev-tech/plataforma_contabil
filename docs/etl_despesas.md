# Pipeline ETL: Extrato de Despesas Financeiras

Este documento detalha o funcionamento, as regras de negócios e a arquitetura do parser criado para ler os relatórios de "Despesas Financeiras" e carregar na camada canônica.

## 1. Arquitetura do Parser (ParserBase)

Todos os parsers implementam a classe abstrata `ParserBase`, garantindo o seguinte ciclo de vida:
1. **Extract**: Leitura do RAW File e geração de DTOs da Staging Area (`StagingDespesa`).
2. **Validate**: Auditoria e verificação dos campos mínimos obrigatórios (ex: IDs originais).
3. **Transform**: Conversão e normalização dos dados Staging para entidades do Modelo Canônico (Despesa, Parcela, Fornecedor, etc).
4. **Load**: Persistência do Modelo Canônico associado à entidade de auditoria `ImportacaoArquivo`.

## 2. Fluxo: Despesas (`Despesas 06-2026.xlsx`)

- **RAW**: O arquivo `.xlsx` intocado.
- **STAGING**: Representação em memória (`StagingDespesa`), abstraindo colunas do Excel e mantendo valores brutos, com getters inteligentes.
- **CANONICAL**: Entidades explícitas no banco (Tabelas: `despesas`, `parcelas_despesa`, `fornecedores`, `projetos`, `categorias_financeiras`).

## 3. Regras de Transformação Implementadas

Conforme diretrizes definidas:

1. **Preservação de UUIDs**: 
   - A coluna `ID` é mapeada para `Despesa.id_uuid_origem`.
   - A coluna `ID Parcela` é mapeada para `ParcelaDespesa.id_parcela_origem`.
   Esses IDs garantem a rastreabilidade externa e suportam idempotência.

2. **Valores Inalterados e Sinal Convencionado**:
   - Originalmente, o Excel traz os valores de saída como negativos (ex: `-132500.00`). 
   - **Convenção Canônica**: Os valores no Modelo Canônico de Despesas são armazenados com **sinal positivo** (valor absoluto), visto que a natureza da entidade "Despesa" já implica saída de caixa.

3. **Datas**:
   - Campos `Data de competência`, `Vencimento parcela` e `Data de pagamento parcela` são limpos, fazendo parse do formato Brasileiro (dd/mm/yyyy) para o tipo `Date` do SQL.

4. **Fuzzy Fornecedor (Normalização)**:
   - Para evitar cadastros duplicados que prejudicariam a acurácia (25%) no Motor de Conciliação, o nome do fornecedor original ("BH MATERIAIS DE CONSTRUCAO LTDA") gera um **nome_normalizado**:
   - Remoção de acentos (`ç` -> `c`, `ã` -> `a`).
   - Caixa alta (`.upper()`).
   - Remoção de caracteres especiais.
   - Remoção dos sufixos societários (`LTDA`, `ME`, `EIRELI`, `SA`, `S A`).
   - Exemplo final: `BH MATERIAIS CONSTRUCAO`.

## 4. Auditoria e Validações Realizadas
Ao iniciar a ingestão, cria-se um `ImportacaoArquivo` (`status="EM_PROCESSAMENTO"`).
Os testes validam com sucesso a carga, atestando que todas as parcelas foram injetadas e que a auditoria final reflete a `quantidade_registros` precisa sem erros, gerando o commit na transação.
