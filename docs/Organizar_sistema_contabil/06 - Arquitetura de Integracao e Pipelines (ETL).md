# 06 - Arquitetura de Integração e Pipelines (ETL)

## 1. Visão Geral
A Ingestão de Dados (Staging & Ingestion) é a primeira camada da Plataforma Contábil. Sua responsabilidade primária é conectar fontes heterogêneas, extrair dados em formatos não estruturados (PDFs, planilhas Excel) e semi-estruturados (APIs, Webhooks), e transformar essas informações em um modelo de dados estruturado e unificado, pronto para as etapas de Motor Fiscal e Motor Contábil.

## 2. Abordagem Arquitetural (Design Patterns)
O design implementado segue o padrão de **Pipeline Architecture** com **Adapters**:
- **Interface Segregation:** Todos os parsers estendem de uma classe abstrata (`BaseParser`), garantindo um contrato fixo.
- **Strategy Pattern:** Dependendo do tipo do arquivo (Extrato Inter, Razão SCI, Relatório Conta Azul), uma estratégia específica de parser é acionada em tempo de execução (`ExtratoInterParser`, `SciRazaoParser`, etc.).
- **Idempotência:** A ingestão de um mesmo arquivo múltiplas vezes não gera duplicidade. O pipeline verifica _hashes_ do documento ou das transações extraídas.

## 3. Fluxo de Ingestão de Arquivos (Uploads)
O fluxo padrão para processamento de extratos e relatórios em PDF/Excel ocorre em quatro etapas:

1. **Upload & Armazenamento Seguro:** 
   O documento é recebido pela API (`/api/v1/executions/upload`), sanitizado e gravado em um Object Storage ou filesystem isolado por `workspace_id`.
   
2. **Reconhecimento (Routing):**
   O motor avalia o formato e metadados do documento. Baseado nessas informações, roteia o documento para o `Adapter` correto (ex: `GenericPDFAdapter`, `ExcelDespesasParser`).

3. **Extração (Parsing):**
   O documento é escaneado em busca de colunas-chave (Data, Histórico, Débito, Crédito, Saldo). A leitura em PDF faz o uso de bibliotecas como `PyPDF2` com regexes específicos. Arquivos de banco normalmente exigem tratamento para lidar com múltiplas páginas e cabeçalhos residuais.

4. **Staging (Normalização):**
   A saída é mapeada para uma entidade intermediária (tabelas de Staging, ex: `MovimentacaoBancaria`), aguardando conciliação. 

## 4. Integração de APIs (Webhooks & Polling)
Para ERPs que disponibilizam endpoints REST, o sistema utiliza *Background Tasks* para orquestrar a ingestão contínua.

- **Workers Assíncronos:** Tarefas enfileiradas gerenciam a extração contínua (Polling) respeitando limites de taxa (Rate Limits) das APIs de terceiros.
- **Dead Letter Queues (DLQ):** Caso uma API de ERP fique instável, as mensagens de extração não se perdem. Elas são encaminhadas para uma DLQ, sendo reenfileiradas automaticamente com _Exponential Backoff_ (esperas progressivas de 2s, 4s, 8s, etc.).

## 5. Auditoria de Ingestão
Todo arquivo ou payload ingerido possui uma tabela de "Execução de Pipeline" vinculada.
O *status* transita entre:
- `CRIADA`
- `EM_PROCESSAMENTO`
- `CONCLUIDA`
- `FALHA`

Nenhum arquivo processado é destruído, garantindo assim que em caso de disputas legais sobre falhas na contabilidade, a construtora ou escritório contábil possua a evidência exata do arquivo bruto original que subsidiou as movimentações contábeis finais.
