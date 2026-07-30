**Documentação Técnica da Estrutura de Dados**  
Arquivo: `Razão SUCESSOR.xlsx`

---

### 1. IDENTIFICAÇÃO DO ARQUIVO

- **Nome do arquivo**: `Razão SUCESSOR.xlsx`
- **Finalidade aparente**: Razão contábil (ledger) da conta bancária específica “85 - INTER - 01.1.1.02.004 Banco Inter”, exportada do sistema contábil **SCI VISUAL Sucessor**.
- **Processo de negócio representado**: Registro contábil de todas as movimentações da conta corrente Banco Inter no período de 01/06/2026 a 30/06/2026, com partidas dobradas (débito/crédito), identificação de lote, chave do lançamento e conta de contrapartida.
- **Usuários prováveis**: Contabilidade, Controller, Analistas de Conciliação Contábil/Bancária, Auditores e o Contador responsável (Clayton Bielau – CRC 039.081/SC).
- **Papel em uma solução de conciliação financeira/contábil**: Fonte primária do lado **contábil** (razão). É o contraponto direto do extrato bancário. Serve para matching 1:1 ou N:1 entre lançamentos contábeis e movimentações bancárias, validação de saldo contábil × saldo bancário, identificação de diferenças de timing (flutuação), classificação por conta de contrapartida e rastreabilidade via “Chave” e “Lote”.

---

### 2. ESTRUTURA DAS COLUNAS

O arquivo possui **1 planilha** com dimensões A1:U224 (21 colunas físicas).  
Trata-se de um **export de layout de impressão** (print layout). As colunas lógicas são **repetidas várias vezes** horizontalmente para ocupar a largura da página. Não existe uma tabela limpa de dados; o conteúdo é altamente redundante.

**Colunas lógicas identificadas** (a partir do cabeçalho da linha 4 e do padrão de dados):

**Campo: Histórico**  
Tipo: Texto  
Descrição: Descrição do lançamento contábil. Pode ser o texto original do extrato bancário, “Vlr. Ref. ...”, “Compra a Vista de ...”, “Aquisição de Serviços a Vista de ...”, “Resgate Imediato Fundo”, “DARF NUMERADO”, etc.  
Obrigatório: Sim (nas linhas de movimento)  
Exemplo: `Pix enviado: "Cp :60701190-AUTO POSTO VILA ROMANA LTDA"` / `Compra a Vista de Bh Materiais de Construcao LTDA - NFE 124139` / `Resgate Imediato Fundo: "INTER RESGATE 24H FIC FIRF RL"`  
Observação: Aparece repetido nas colunas A–C (e equivalentes nas páginas seguintes). Contém quebras de linha em alguns casos.

**Campo: Lote**  
Tipo: Texto / Código  
Descrição: Identificador do lote de lançamento.  
Obrigatório: Opcional  
Exemplo: `LANCA` (valor predominante) ou vazio  
Observação: Aparece nas colunas D–E. Muitas linhas de Pix simples não possuem lote preenchido.

**Campo: Chave**  
Tipo: Código (numérico sequencial)  
Descrição: Identificador único do lançamento contábil dentro do sistema SCI VISUAL.  
Obrigatório: Sim (nas linhas de movimento)  
Exemplo: `40070`, `40088`, `39969`, `38580`  
Observação: Aparece nas colunas F–H. É a melhor chave natural para rastreabilidade e deduplicação. Valores observados na faixa aproximada 38580–40375.

**Campo: Contra (Conta de Contrapartida)**  
Tipo: Código  
Descrição: Código da conta contábil de contrapartida do lançamento.  
Obrigatório: Opcional (presente principalmente em lançamentos classificados)  
Exemplos encontrados: `51`, `1763`, `1771`, `1795`, `1905`, `1908`, `1909`, `1914`, `7739`, `7891`, `7939`, `8397`  
Observação: Aparece nas colunas I–J. Códigos mais frequentes: 1905, 1909, 1908, 51.

**Campo: Débito**  
Tipo: Moeda (texto formatado com ponto de milhar e vírgula decimal + indicador implícito)  
Descrição: Valor lançado a débito na conta bancária.  
Obrigatório: Condicional (mutuamente exclusivo com Crédito na maioria dos casos)  
Exemplo: `370,05` / `149.795,17`  
Observação: Valores de saída bancária aparecem a crédito na conta banco (padrão contábil brasileiro: banco é conta de ativo → entrada = Débito, saída = Crédito).

**Campo: Crédito**  
Tipo: Moeda  
Descrição: Valor lançado a crédito na conta bancária.  
Obrigatório: Condicional  
Exemplo: `3.690,00` / `132.500,00`  

**Campo: Saldo atual**  
Tipo: Moeda + Indicador de natureza (D/C)  
Descrição: Saldo da conta após o lançamento, com sufixo D (devedor) ou C (credor).  
Obrigatório: Sim  
Exemplo: `32.769,30D` / `3.338,74C` / `161.970,63D`  
Observação: Mantém o saldo corrente. Pode mudar de natureza (D ↔ C) ao longo do período.

**Campos de contexto (não colunas de movimento)**:

- Conta contábil: `85 - INTER - 01.1.1.02.004 Banco Inter`
- Saldo anterior: `33.139,35D`
- Período: `Razão nº 1 de 01/06/2026 a 30/06/2026`
- Empresa: `Vnp - Spe Empreendimentos Imobiliarios Ltda`
- Data de emissão do relatório: 27/07/2026 08:34:39
- Sistema: contábil SCI VISUAL Sucessor
- Assinaturas: Sócio-Administrador (Vinicius Moreira Santolia) e Contador (Clayton Bielau)

**Campo: Data**  
Tipo: Data (texto dd/mm/yyyy)  
Descrição: Data do lançamento (aparece como linha de cabeçalho de dia, não como coluna por movimento).  
Obrigatório: Presente nos cabeçalhos de dia  
Exemplo: `01/06/2026`, `03/06/2026`, `12/06/2026`, `30/06/2026`  
Observação: A data deve ser propagada para as linhas de movimento subsequentes até o próximo cabeçalho de data.

---

### 3. ANÁLISE DOS DADOS

- **Quantidade de linhas**: 224 (incluindo múltiplos cabeçalhos de página, linhas de conta, saldos, rodapés e assinaturas).
- **Quantidade de colunas físicas**: 21 (A–U). Uso real concentrado nas primeiras colunas de cada “bloco” de página.
- **Campos vazios**: Extremamente elevados. Layout de impressão gera grande esparsidade e repetição.
- **Dados duplicados**: Altíssima redundância horizontal (o mesmo texto é repetido 2–3 vezes por linha para formatação visual). Verticalmente existem movimentos legítimos repetidos apenas quando há mais de um lançamento semelhante.
- **Inconsistências aparentes**:
  - Layout de impressão (não é uma tabela de dados limpa).
  - Datas e textos de cabeçalho aparecem misturados nas mesmas colunas usadas para movimentos.
  - Alguns históricos começam com “Vlr. Ref.” (valor referente) enquanto outros usam o texto original do banco.
  - Saldo muda de natureza (D → C e vice-versa).
  - Lote preenchido apenas em parte dos lançamentos (principalmente os classificados como “LANCA”).
- **Formatos diferentes no mesmo campo**: Valores monetários como texto com formatação brasileira; saldo com sufixo D/C; datas apenas em cabeçalhos.
- **Problemas que impactam integração de sistema**:
  1. Necessidade de parser inteligente que ignore a redundância horizontal e identifique o “bloco lógico”.
  2. Propagação de data a partir de linhas de cabeçalho de dia.
  3. Distinção entre linhas de movimento, cabeçalho de conta, cabeçalho de página e rodapé.
  4. Conversão de valores monetários + indicador D/C.
  5. Tratamento de células com quebra de linha.
  6. O arquivo contém estilos XML inválidos (cores não-aRGB), o que impede abertura limpa com openpyxl padrão (é necessário tratamento especial ou correção do stylesheet).

---

### 4. IDENTIFICAÇÃO DE ENTIDADES DE NEGÓCIO

**ContaContabil**  

- Código completo (`85 - INTER - 01.1.1.02.004`)  
- Descrição (`Banco Inter`)  
- Natureza (ativo)

**LancamentoContabil** (entidade principal)  

- Data  
- Histórico  
- Lote  
- Chave (ID do sistema de origem)  
- Conta de contrapartida (Contra)  
- Valor Débito  
- Valor Crédito  
- Saldo após lançamento + natureza  
- Conta contábil de origem (banco)

**LoteContabil**  

- Código do lote (`LANCA` etc.)

**ContaContrapartida**  

- Código (51, 1905, 1909, 1908, 1914, 1795, 7739, 7891, 8397…)  
- (Hipótese: esses códigos representam centros de custo, despesas, fornecedores ou contas de resultado no plano de contas da empresa)

**Empresa**  

- Razão social  
- (CNPJ não aparece neste arquivo, mas é o mesmo da SPE)

**Responsavel / Assinatura**  

- Sócio-Administrador  
- Contador + CRC

Entidades que naturalmente viram tabelas: `conta_contabil`, `lancamento_contabil`, `lote_contabil`, `conta_contrapartida`, `periodo_razao`.

---

### 5. REGRAS DE NEGÓCIO IDENTIFICADAS

- A conta bancária é de natureza **devedora** (ativo). Entradas aumentam o saldo a Débito; saídas aumentam o saldo a Crédito.
- Todo lançamento possui uma **Chave** única gerada pelo sistema SCI VISUAL.
- Lançamentos podem ou não ter **Lote** preenchido (quando preenchido, o valor dominante é “LANCA”).
- Existe conta de **contrapartida** (Contra) na maioria dos lançamentos classificados; lançamentos “puros” de Pix muitas vezes não a possuem.
- O saldo é mantido corrente e pode inverter a natureza (D ↔ C) ao longo do mês.
- Cabeçalhos de data delimitam os movimentos do dia; a data não é atributo de cada linha de movimento no layout.
- Históricos que começam com “Vlr. Ref.” indicam lançamentos que referenciam uma movimentação bancária (tipicamente classificados).
- Resgates de fundo, DARF, pagamentos de títulos e compras a vista têm tratamentos descritivos distintos.
- O relatório é assinado digitalmente/ formalmente pelo Sócio-Administrador e pelo Contador.

---

### 6. RELACIONAMENTOS

**Relacionamentos diretos com o extrato bancário anterior**:

- `LancamentoContabil` ↔ `MovimentacaoBancaria`  
  Chaves de matching possíveis:
  - Valor + Data (± 0–2 dias) + trecho do Histórico / descrição do Pix
  - Código “Cp :XXXXXXX” extraído do histórico
  - Chave contábil (quando houver referência cruzada futura)

**Outros relacionamentos**:

- `LancamentoContabil` → `ContaContabil` (conta banco)
- `LancamentoContabil` → `ContaContrapartida` (via campo Contra)
- `LancamentoContabil` → `LoteContabil`
- `LancamentoContabil` → `Empresa` / `Periodo`
- (Hipótese) Conta de contrapartida → Centro de Custo / Natureza de Despesa / Fornecedor / Projeto (comum em SPEs imobiliárias)

Campos mais fortes para chave de relacionamento:

- **Chave** (dentro do sistema contábil)
- Código “Cp :” + Valor + Data (para conciliação com o banco)
- Conta de contrapartida + Valor + Data

---

### 7. PROPOSTA DE MODELO DE DADOS

**Tabela: conta_contabil**  
Campos: id, codigo_completo, codigo_reduzido, descricao, natureza (D/C), tipo (ativo/passivo/resultado)  
Chave primária: id  
Relacionamentos: 1:N com lancamento_contabil

**Tabela: periodo_razao**  
Campos: id, empresa_id, data_inicio, data_fim, data_emissao, sistema_origem, arquivo_origem  
Chave primária: id

**Tabela: lote_contabil**  
Campos: id, codigo_lote, descricao  
Chave primária: id

**Tabela: conta_contrapartida**  
Campos: id, codigo, descricao (a enriquecer), tipo  
Chave primária: id

**Tabela: lancamento_contabil**  
Campos:  

- id  
- periodo_id  
- conta_contabil_id  
- data_lancamento  
- historico  
- lote_id (nullable)  
- chave_origem (string – Chave do SCI)  
- conta_contrapartida_id (nullable)  
- valor_debito (decimal)  
- valor_credito (decimal)  
- saldo_apos (decimal)  
- natureza_saldo (D/C)  
- linha_origem / pagina  
- hash_unicidade  

Chave primária: id  
Relacionamentos: N:1 conta_contabil, periodo, lote, conta_contrapartida  
Índice único sugerido: (periodo_id + chave_origem)

---

### 8. VISÃO PARA DESENVOLVIMENTO DE SOFTWARE

**Como a planilha entra no sistema**  
Pipeline de ingestão de razões contábeis (source-agnostic). O arquivo é depositado em hot-folder ou enviado via API. Por ser layout de impressão, o parser deve ser específico para o formato SCI VISUAL Sucessor (ou genérico o suficiente para outros ERPs brasileiros que exportam razão em formato de página).

**Processo de importação recomendado**

1. Correção ou bypass do stylesheet inválido (problema conhecido neste arquivo).
2. Identificação de seções: cabeçalho de empresa/período → definição da conta contábil → saldo anterior → blocos de data → linhas de movimento → rodapé/assinaturas.
3. Normalização horizontal (pegar apenas a primeira ocorrência lógica de cada campo por linha).
4. Propagação da data do cabeçalho de dia.
5. Extração e normalização de valores monetários + indicador D/C.
6. Extração de código “Cp :” e número de NF-e / NFS-e do histórico (quando presente).
7. Geração de hash de unicidade (chave_origem + data + valor + historico normalizado).
8. Carga em staging → regras de validação → modelo canônico.
9. Disparo do motor de conciliação com o extrato bancário.

**Validações necessárias**

- Existência e unicidade da Chave dentro do período.
- Soma dos débitos/créditos do dia deve explicar a variação do saldo.
- Saldo final do razão deve ser reconciliável com o saldo do extrato bancário (após ajustes de flutuação).
- Conta contábil constante em todo o arquivo.
- Natureza do saldo coerente com o movimento.

**Transformações necessárias**

- Conversão de data dd/mm/yyyy.
- Parsing de valor monetário brasileiro + sufixo D/C.
- Limpeza de quebras de linha e espaços.
- Extração estruturada de contrapartes e documentos fiscais do histórico.
- Mapeamento dos códigos de “Contra” para o plano de contas mestre.

**APIs / Serviços futuros**

- Motor de Conciliação Bancária × Contábil
- Classificação automática de despesas via conta de contrapartida
- Geração de razão auxiliar / razão por fornecedor
- Integração com ERP / sistema de gestão de obras (SPE)
- Auditoria e trilha de conformidade (chave + lote + assinatura)
- Dashboard de diferenças de conciliação (timing, valor, classificação)

---

### 9. RESUMO TÉCNICO PARA CONTINUIDADE DO DESENVOLVIMENTO

**Resumo Técnico para Continuidade do Desenvolvimento**

Esta planilha representa a **Razão Contábil** da conta “85 - INTER - 01.1.1.02.004 Banco Inter” da empresa VNP – SPE Empreendimentos Imobiliários Ltda, gerada pelo sistema **SCI VISUAL Sucessor** para o período de junho/2026. É a visão contábil oficial das mesmas movimentações presentes no extrato bancário analisado anteriormente.

**Entidades principais**:

- ContaContabil
- LancamentoContabil (fato central)
- LoteContabil
- ContaContrapartida
- PeriodoRazao

**Campos críticos**:

- **Chave** (identificador único do lançamento no sistema de origem)
- Data (propagada dos cabeçalhos)
- Histórico
- Valor Débito / Crédito
- Saldo atual + natureza (D/C)
- Código de Contrapartida (Contra)
- Lote

**Regras identificadas**:

- Conta de ativo → entrada = Débito, saída = Crédito.
- Chave é única e sequencial.
- Saldo é corrente e pode inverter natureza.
- Layout é de impressão (alta redundância horizontal).
- Muitos lançamentos carregam referência explícita ao Pix ou à NF-e/NFS-e.

**Cuidados obrigatórios na implementação**:

1. Tratar o arquivo como **layout de impressão**, não como tabela tabular limpa.
2. Implementar parser resiliente à repetição horizontal e às múltiplas páginas.
3. Corrigir ou contornar o problema de stylesheet inválido (cores não-aRGB).
4. Propagar corretamente a data dos cabeçalhos de dia.
5. Preservar a **Chave** como identificador de origem para rastreabilidade e deduplicação.
6. Mapear os códigos de “Contra” para o plano de contas (enriquecimento necessário).
7. Projetar o matching com o extrato bancário usando combinação de valor + data + trecho do histórico / código Cp :.
8. Manter staging separado do modelo canônico e registrar a linha/página de origem para auditoria.

Esta documentação, em conjunto com a análise do extrato bancário (`Extrato-01-06-2026-a-30-06-2026-PDF.xlsx`), fornece a base completa para:

- Modelo Entidade-Relacionamento da conciliação
- Modelo de Dados Canônico
- Regras de matching e scoring
- Arquitetura do serviço de ingestão e conciliação
- Diagramas de sequência e de classes

Nenhuma hipótese de negócio adicional (centro de custo, obra, projeto etc.) foi assumida além do que está explicitamente presente no arquivo.
