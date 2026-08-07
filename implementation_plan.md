# Sprint de Confiabilidade da Importação

A prioridade atual foi invertida. O foco agora não é o frontend, mas garantir que a ingestão de dados (o motor do sistema) seja confiável e capaz de processar os arquivos reais exportados pelos sistemas contábeis, financeiros e bancos.

O cenário atual usa arquivos CSV simples gerados para testes, o que não reflete a realidade das planilhas originadas de ERPs. Se a ingestão falha, todo o pipeline de conciliação fica comprometido ("A fila de revisão está vazia").

## Objetivo

Garantir que planilhas reais (como as encontradas no diretório `Architecture/`) sejam lidas, formatadas corretamente e persistidas no modelo canônico, sem perdas de informações cruciais.

## Open Questions

> [!WARNING]
> **Formato do Razão Contábil**: O arquivo `Razão SUCESSOR.xlsx` apresentou erro de "invalid XML" nativo do Excel. Costuma acontecer quando o sistema exporta um HTML mascarado de `.xlsx` ou quando a planilha está corrompida. Gostaria de saber qual ERP gerou esse Razão para usarmos o motor correto (ex: `calamine` ou `html5lib`) ou se você costuma abri-lo e salvá-lo novamente antes de usar.
> 
> **Mapeamento de Despesas**: O arquivo `Despesas 06-2026.xlsx` possui a coluna "Valor total" e "Valor parcela". Na criação do modelo, usaremos cada linha como uma Parcela individual associada à mesma Despesa pai (usando a coluna ID para agrupar)?

## Proposed Changes

A estratégia envolve abandonar o parser estático (`parsers.py` atual) e adotar o padrão **Adapter/Strategy**. O sistema tentará descobrir o layout do arquivo e aplicará o Parser específico.

### Componente de Parsing (Backend)

#### [MODIFY] [parsers/__init__.py](file:///Users/gustavo/Documents/dev/projects/plataforma_contabil/backend/app/services/parsers/__init__.py)
Refatorar a estrutura para um pacote de parsers. Criar o `ParserFactory` que receberá o arquivo, executará o método `can_parse()` de cada adapter registrado e retornará o parser correto para o arquivo.

#### [NEW] [parsers/base.py](file:///Users/gustavo/Documents/dev/projects/plataforma_contabil/backend/app/services/parsers/base.py)
Criar a classe abstrata `ImportAdapter` com a interface:
- `can_parse(file_stream, tipo_arquivo) -> bool`
- `parse(file_stream, db_session, execucao_id) -> ImportResult`

#### [NEW] [parsers/banco_inter.py](file:///Users/gustavo/Documents/dev/projects/plataforma_contabil/backend/app/services/parsers/banco_inter.py)
Implementar o parser específico para o `Extrato-01-06-2026-a-30-06-2026-PDF.xlsx`.
- **Lógica**: Ignorar o cabeçalho descritivo (linhas 0 a 9). Identificar as linhas de data (ex: "1 de Junho de 2026 Saldo do dia...") para guardar a data vigente, e as linhas subsequentes como as transações do dia.
- Tratar os valores string formatados ("-R$ 239,00") para `float`.

#### [NEW] [parsers/despesas_erp.py](file:///Users/gustavo/Documents/dev/projects/plataforma_contabil/backend/app/services/parsers/despesas_erp.py)
Implementar o parser para `Despesas 06-2026.xlsx`.
- **Lógica**: Mapear as colunas específicas ("ID", "Fornecedor", "Valor total", "Valor parcela", "Vencimento parcela", "Status parcela").
- Agrupar linhas que pertencem ao mesmo "ID" na mesma `Despesa`, criando múltiplas `ParcelaDespesa`.

#### [NEW] [parsers/razao_sucessor.py](file:///Users/gustavo/Documents/dev/projects/plataforma_contabil/backend/app/services/parsers/razao_sucessor.py)
Implementar o parser para o Razão, resolvendo o problema de leitura do arquivo XML/Excel corrompido ou mal formatado.

### Atualização do Pipeline

#### [MODIFY] [pipeline/runner.py](file:///Users/gustavo/Documents/dev/projects/plataforma_contabil/backend/app/pipeline/runner.py)
Substituir a chamada hardcoded de `parse_despesas` / `parse_extrato` pela chamada ao `ParserFactory.get_parser(file).parse()`. Inserir logs detalhados de sucesso/falha por linha para facilitar auditoria.

## Verification Plan

### Teste de Ingestão Real
- Criarei um script `verify_import.py` que carregará diretamente os 3 arquivos originais do diretório `Architecture/`.
- O script fará a simulação completa: rodará os adapters, contará quantas linhas úteis existem nas planilhas e baterá exatamente com os `COUNT(*)` gerados no banco de dados.
- O relatório será impresso no console contendo as informações que você exigiu (nome do fornecedor parseado, histórico das transações, valor formatado, etc.).
- Os logs mostrarão em tempo real quantas linhas foram ignoradas e o motivo (ex: linha de saldo do Banco Inter, linha de cabeçalho).
