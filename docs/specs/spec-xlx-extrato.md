**Documentação Técnica da Estrutura de Dados**  
Arquivo: `Extrato-01-06-2026-a-30-06-2026-PDF.xlsx`

---

### 1. IDENTIFICAÇÃO DO ARQUIVO

- **Nome do arquivo**: `Extrato-01-06-2026-a-30-06-2026-PDF.xlsx`
- **Finalidade aparente**: Extrato bancário (statement) de conta corrente do Banco Inter, gerado a partir de PDF e convertido para Excel (evidência clara pela estrutura irregular e células multilinha).
- **Processo de negócio representado**: Movimentação financeira diária de conta bancária empresarial (entradas, saídas, resgates de fundo e pagamentos) no período de 01/06/2026 a 30/06/2026.
- **Usuários prováveis**: Contabilidade, Controladoria, Financeiro (tesouraria), Analistas de Conciliação e Auditores internos/externos da empresa VNP – SPE Empreendimentos Imobiliários.
- **Papel em uma solução de conciliação financeira/contábil**: Fonte primária de dados bancários (lado “banco”). Serve como input para matching automático/semi-automático com lançamentos contábeis, notas fiscais, ordens de pagamento, contas a pagar/receber e extratos de outros sistemas. Também alimenta reconciliação de saldo, classificação de despesas por fornecedor/projeto e geração de razão bancário.

---

### 2. ESTRUTURA DAS COLUNAS

O arquivo possui **uma única planilha** (“Table 1”) com dimensões A1:I179 (9 colunas físicas, 179 linhas).  
**Não existe cabeçalho tabular estável**. A estrutura é altamente irregular devido à conversão PDF → Excel. As colunas físicas mudam de significado conforme a “página” original do PDF.

Documentação lógica (campos conceituais extraídos):

**Campo: Descrição / Histórico**  
Tipo: Texto  
Descrição: Descrição completa da movimentação ou cabeçalho de dia. Contém tipo de operação + identificador (Cp :código-Nome ou número de conta + nome).  
Obrigatório: Sim (sempre presente nas linhas de movimento)  
Exemplo: `Pix enviado: "Cp :10573521-PIX Marketplace"` / `Resgate Imediato Fundo: "INTER RESGATE 24H FIC FIRF RL"`  
Observação: Pode conter quebras de linha e misturar cabeçalho de dia + descrição na mesma célula. Formato variável.

**Campo: Valor da Transação**  
Tipo: Moeda (texto formatado com R$ e vírgula decimal)  
Descrição: Valor da movimentação. Negativo = saída; positivo = entrada.  
Obrigatório: Sim para linhas de movimento  
Exemplo: `-R$ 239,00` / `R$ 149.795,17`  
Observação: Aparece em colunas físicas variáveis (B, C, D ou E – índices 1, 2, 3 ou 4). Formato brasileiro (ponto milhar, vírgula decimal).

**Campo: Saldo por Transação / Saldo do Dia**  
Tipo: Moeda (texto formatado)  
Descrição: Saldo da conta após a transação ou saldo de fechamento do dia.  
Obrigatório: Sim para linhas de movimento e cabeçalhos de dia  
Exemplo: `R$ 45.861,60` / `-R$ 107.393,29`  
Observação: Aparece em colunas físicas variáveis (F, G ou H – índices 5, 6 ou 7). Pode ficar negativo durante o dia (overdraft temporário).

**Campo: Data do Dia (implícita)**  
Tipo: Data (texto em português)  
Descrição: Data de referência do agrupamento de movimentações.  
Obrigatório: Presente apenas em linhas de cabeçalho de dia  
Exemplo: `1 de Junho de 2026 Saldo do dia: R$ 34.255,05`  
Observação: Não existe coluna de data por transação. A data deve ser propagada a partir do cabeçalho de dia.

**Campo: Tipo de Operação (extraído da descrição)**  
Tipo: Texto / Lista de valores  
Descrição: Classificação da natureza da movimentação.  
Obrigatório: Derivado  
Exemplos encontrados:  

- Pix enviado  
- Pix recebido  
- Pix enviado devolvido  
- Pagamento efetuado  
- Pagamento de Titulo - Inter  
- Resgate Imediato Fundo  
- DARF NUMERADO  
- Pagamento PM Nova Lima  

**Campo: Identificador do Contraparte / Código (extraído)**  
Tipo: Código / Texto  
Descrição: Código “Cp :XXXXXXX” ou número de conta + nome do beneficiário/pagador.  
Obrigatório: Opcional (nem todas as linhas possuem)  
Exemplo: `Cp :60701190` / `00019 278370870`  

**Campos de Cabeçalho do Extrato (linhas 1-11)**  

- Data/hora de solicitação  
- Razão social  
- CNPJ + Instituição + Agência + Conta  
- Período  
- Saldo total / disponível / bloqueado  

---

### 3. ANÁLISE DOS DADOS

- **Quantidade de linhas**: 179 (incluindo cabeçalho, saldos e linhas de dia).
- **Quantidade de colunas físicas**: 9 (A–I). Uso real concentrado nas colunas 0, 1/2/3/4 (valor) e 5/6/7 (saldo).
- **Campos vazios**: Extremamente altos. A grande maioria das células é `None`. Estrutura esparsa típica de OCR/PDF extraction.
- **Dados duplicados**: Não há linhas inteiras duplicadas, mas nomes de contrapartes e códigos “Cp :” se repetem (padrão normal de fornecedores recorrentes).
- **Inconsistências aparentes**:
  - Colunas de valor e saldo **migram de posição** ao longo do arquivo (provável efeito de layout de páginas do PDF original).
  - Células multilinha (descrição + cabeçalho de dia misturados).
  - Saldo negativo intermediário (ex.: após grande Pix para UP ESQUADRIAS).
  - Formatação de moeda sempre como texto (“R$ X.XXX,XX”).
  - Datas apenas em português por extenso nos cabeçalhos de dia.
- **Formatos diferentes no mesmo campo**: Sim – valor e saldo aparecem em diferentes colunas físicas.
- **Problemas que impactam integração de sistema**:
  1. Ausência de estrutura tabular estável (parser deve ser resiliente a mudança de coluna).
  2. Necessidade de parsing de texto livre para extrair tipo, código e nome do contraparte.
  3. Propagação de data (não existe data por transação).
  4. Conversão de moeda brasileira (remover “R$”, trocar ponto/vírgula).
  5. Tratamento de células multilinha e quebras de linha.
  6. Identificação confiável de linhas de cabeçalho de dia vs. movimento vs. resgate de fundo.

---

### 4. IDENTIFICAÇÃO DE ENTIDADES DE NEGÓCIO

Entidades candidatas a tabelas:

**ContaBancaria**  

- CNPJ da empresa  
- Razão social  
- Banco / Instituição  
- Agência  
- Número da conta  
- Saldo disponível / bloqueado / total (snapshot)

**ExtratoBancario / StatementHeader**  

- Período (data início / fim)  
- Data/hora de geração  
- Conta associada  
- Saldo inicial / final do período

**MovimentacaoBancaria (Transação)**  

- Data  
- Tipo de operação  
- Descrição original  
- Valor (signed)  
- Saldo após movimento  
- Código do contraparte (Cp :)  
- Nome do contraparte  
- Identificador de conta destino/origem (quando presente)  
- Flag de devolução  
- Referência a resgate de fundo (quando aplicável)

**Contraparte / FornecedorBeneficiario**  

- Código Cp : (quando existir)  
- Nome / Razão social  
- Documento (parcialmente extraível em alguns casos)

**FundoInvestimento** (para resgates)  

- Nome do fundo (“INTER RESGATE 24H FIC FIRF RL”)

**TipoOperacao** (domínio)  

- Lista controlada dos tipos observados.

---

### 5. REGRAS DE NEGÓCIO IDENTIFICADAS

- Valores com sinal negativo representam **saídas** (Pix enviado, pagamentos, DARF). Valores positivos representam **entradas** (Pix recebido, resgates de fundo, devoluções).
- O saldo por transação é sequencial e deve bater com o saldo do dia no cabeçalho.
- Cabeçalhos de dia (“X de Junho de 2026 Saldo do dia: R$ ...”) delimitam grupos de movimentações daquela data. A data deve ser herdada pelas linhas seguintes até o próximo cabeçalho.
- Resgates de fundo (“Resgate Imediato Fundo”) são entradas de liquidez e frequentemente ocorrem quando o saldo está baixo ou negativo.
- Existe relação recorrente entre códigos “Cp :” e nomes de fornecedores (mesmo código aparece várias vezes).
- Alguns pagamentos usam descrição diferente (“Pagamento efetuado”, “Pagamento de Titulo - Inter”, “DARF NUMERADO”, “Pagamento PM Nova Lima”) – indicam canais distintos.
- Devoluções de Pix aparecem explicitamente como “Pix enviado devolvido”.
- Saldo pode ficar temporariamente negativo (overdraft intradía permitido pelo banco ou pela natureza da conta).
- O saldo final do período (R$ 99.114,75) é igual ao saldo disponível; saldo bloqueado = 0.

---

### 6. RELACIONAMENTOS

Possíveis relacionamentos com outras planilhas/sistemas:

- **MovimentacaoBancaria** ↔ **Fornecedor** (via código Cp : ou nome normalizado)
- **MovimentacaoBancaria** ↔ **ContaBancaria** (via agência + conta)
- **MovimentacaoBancaria** ↔ **DocumentoContabil / Lançamento** (via valor + data + contraparte – chave de conciliação)
- **MovimentacaoBancaria** ↔ **Projeto / Centro de Custo / Obra** (hipótese – comum em SPE imobiliária; não existe no extrato, deve vir de outro sistema)
- **MovimentacaoBancaria** ↔ **Titulo / Boleto / Nota Fiscal** (quando a descrição contiver referência)
- **ResgateFundo** ↔ **PosicaoFundo** (outro sistema de investimentos)

Chaves candidatas de relacionamento:

- Código “Cp :XXXXXXX” (mais estável que o nome)
- CNPJ da conta + data + valor + tipo (para matching fuzzy)
- Nome normalizado do contraparte + valor + data

---

### 7. PROPOSTA DE MODELO DE DADOS (inicial)

**Tabela: conta_bancaria**  
Campos: id, cnpj_empresa, razao_social, banco, agencia, numero_conta, created_at  
Chave primária: id (surrogate) ou (banco + agencia + numero_conta)  
Relacionamentos: 1:N com extrato_bancario e movimentacao_bancaria

**Tabela: extrato_bancario**  
Campos: id, conta_bancaria_id, data_inicio, data_fim, data_geracao, saldo_inicial, saldo_final, saldo_disponivel, saldo_bloqueado, arquivo_origem  
Chave primária: id  
Relacionamentos: N:1 conta_bancaria; 1:N movimentacao_bancaria

**Tabela: movimentacao_bancaria**  
Campos:  

- id  
- extrato_id  
- data_movimento  
- tipo_operacao (enum/texto)  
- descricao_original  
- valor (decimal, signed)  
- saldo_apos (decimal)  
- codigo_contraparte  
- nome_contraparte  
- documento_contraparte (nullable)  
- is_devolucao (boolean)  
- is_resgate_fundo (boolean)  
- nome_fundo (nullable)  
- linha_origem (para rastreabilidade)  
- hash_unicidade (para deduplicação)  

Chave primária: id  
Relacionamentos: N:1 extrato_bancario; N:1 contraparte (opcional)

**Tabela: contraparte**  
Campos: id, codigo_cp, nome_canonico, documento, tipo (PF/PJ)  
Chave primária: id  
Relacionamentos: 1:N movimentacao_bancaria

**Tabela: tipo_operacao** (domínio)  
Campos: codigo, descricao, natureza (entrada/saida)

---

### 8. VISÃO PARA DESENVOLVIMENTO DE SOFTWARE

**Como a planilha entra no sistema automatizado**  
Pipeline de ingestão de extratos bancários (source-agnostic). O arquivo Excel (ou o PDF original) é depositado em um bucket/hot-folder ou enviado via API de upload.

**Processo de importação recomendado**

1. Detecção de layout (identificar se é PDF convertido ou extrato nativo).
2. Parser resiliente linha a linha (não depender de posição fixa de coluna).
3. Identificação de seções: cabeçalho do extrato → cabeçalhos de dia → linhas de movimento.
4. Extração de data por propagação de contexto.
5. Parsing de descrição com regex para tipo, código Cp e nome.
6. Normalização de valores monetários (pt-BR → decimal).
7. Geração de hash de unicidade (data + valor + descrição normalizada + saldo_apos).
8. Persistência em staging → validação → carga na tabela canônica.
9. Gatilho de motor de conciliação.

**Validações necessárias**

- Soma dos valores do dia deve fechar com a variação de saldo do dia.
- Saldo final do arquivo deve bater com o último saldo por transação.
- Ausência de gaps de data (ou flag de dia sem movimento).
- Detecção de duplicidade por hash.
- Validação de formato de moeda e sinais.
- CNPJ/Agência/Conta consistentes com cadastro mestre.

**Transformações necessárias**

- Conversão de data por extenso (“1 de Junho de 2026”) → date.
- Limpeza e normalização de nomes de contraparte.
- Extração estruturada de códigos.
- Classificação automática de tipo_operacao.
- Enriquecimento com dados mestres de fornecedor (quando código Cp existir).

**APIs / Serviços futuros que podem consumir**

- Motor de Conciliação Bancária
- Dashboard de Fluxo de Caixa / Previsão
- Classificação automática de despesas (ML ou regras)
- Integração com ERP (lançamentos contábeis)
- Auditoria e trilha de conformidade
- API de consulta de movimentações por período/fornecedor/projeto

---

### 9. RESUMO TÉCNICO PARA CONTINUIDADE DO DESENVOLVIMENTO

**Resumo Técnico para Continuidade do Desenvolvimento**

Esta planilha representa um **extrato bancário diário** (Banco Inter) da conta da SPE VNP Empreendimentos Imobiliários (CNPJ 59.120.530/0001-16), período junho/2026. É uma fonte clássica de dados do lado “banco” para processos de conciliação financeira e contábil.

**Entidades principais**:

- ContaBancaria
- ExtratoBancario (header)
- MovimentacaoBancaria (fato principal)
- Contraparte (fornecedor/beneficiário)
- TipoOperacao / FundoInvestimento (domínios)

**Campos críticos**:

- Data do movimento (precisa ser inferida/propagada)
- Valor assinado
- Saldo após movimento
- Tipo de operação
- Código Cp + Nome do contraparte
- Descrição original (para auditoria e matching fuzzy)

**Regras identificadas**:

- Sinal do valor define natureza (entrada/saída).
- Cabeçalhos de dia definem o contexto temporal.
- Resgates de fundo são eventos de liquidez distintos.
- Códigos “Cp :” são a melhor chave natural para fornecedores.
- Saldo pode ser negativo intradía.

**Cuidados obrigatórios na implementação**:

1. **Não assumir layout tabular fixo** – o parser deve ser orientado a conteúdo e resiliente a mudança de coluna.
2. Tratar células multilinha e quebras de linha.
3. Implementar conversão robusta de moeda pt-BR.
4. Gerar hash de deduplicação e manter rastreabilidade da linha de origem.
5. Propagar data corretamente a partir dos cabeçalhos de dia.
6. Separar claramente staging (dados brutos) de modelo canônico.
7. Prever matching fuzzy (valor + data ±1 dia + nome normalizado) além de matching exato por código.
8. O arquivo atual é resultado de conversão PDF; idealmente o sistema deve aceitar também o PDF original ou extratos nativos via Open Banking / API do banco.

Esta documentação é suficiente para iniciar:

- Modelo Entidade-Relacionamento
- Modelo de Dados Canônico
- Diagramas de sequência de ingestão
- Especificação do parser e das regras de validação
- Arquitetura do serviço de conciliação

Nenhuma suposição de negócio adicional (centro de custo, projeto, obra etc.) foi feita além do que está explicitamente presente no arquivo.
