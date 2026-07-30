**Documentação Técnica da Estrutura de Dados**  
Arquivo: `Despesas 06-2026.xlsx`

---

### 1. IDENTIFICAÇÃO DO ARQUIVO

- **Nome do arquivo**: `Despesas 06-2026.xlsx`
- **Finalidade aparente**: Exportação estruturada de despesas (contas a pagar) do período de junho/2026, incluindo informações de parcelas, pagamentos, projetos e fornecedores.
- **Processo de negócio representado**: Gestão de despesas operacionais e de obra de uma SPE imobiliária (construção civil). Abrange registro de despesas, classificação por categoria financeira e projeto, controle de parcelas, formas de pagamento e vínculo com notas fiscais.
- **Usuários prováveis**: Financeiro, Controladoria, Gestores de Obra/Projeto, Contabilidade e Analistas de Conciliação.
- **Papel em uma solução de conciliação financeira/contábil**: Fonte do lado **negócio/orçamentário**. Serve como ponte entre o que foi planejado/registrado no sistema de gestão financeira e o que efetivamente saiu no banco (extrato) e foi contabilizado (razão). É essencial para:
  - Matching de pagamentos bancários × despesas
  - Rateio por projeto / obra
  - Conciliação de títulos e parcelas
  - Classificação contábil e gerencial
  - Apuração de custo por obra (Casa Bioma, Casa Mina, Residência Nilson e Laura etc.)

---

### 2. ESTRUTURA DAS COLUNAS

Planilha única: **Exportado**  
174 linhas de dados + 1 cabeçalho | 25 colunas.

**Campo: Tipo**  
Tipo: Lista de valores (Texto)  
Descrição: Tipo do lançamento.  
Obrigatório: Sim  
Exemplo: `Despesa`  
Observação: Valor único em todo o arquivo (“Despesa”).

**Campo: Nome**  
Tipo: Texto  
Descrição: Título/descrição curta da despesa.  
Obrigatório: Sim  
Exemplo: `Pagamento OC00098` / `Esquadrias Bioma - Entrada` / `MO Gesso liso` / `Locação de Caçamba`  
Observação: Livre. Frequentemente indica a natureza (MO = Mão de Obra, materiais, locação etc.).

**Campo: ID**  
Tipo: Código (UUID)  
Descrição: Identificador único da despesa (cabeçalho do título).  
Obrigatório: Sim  
Exemplo: `1054076f-0128-4612-9379-5059e51afff1`  
Observação: UUID. Pode se repetir quando a despesa possui mais de uma parcela (3 casos de ID duplicado = despesas parceladas).

**Campo: Status**  
Tipo: Lista de valores  
Descrição: Status geral da despesa.  
Obrigatório: Sim  
Exemplos: `Pago` (173), `Em aberto` (1)  
Observação: Quase todo o arquivo está “Pago”.

**Campo: Categoria financeira**  
Tipo: Texto / Lista de valores  
Descrição: Classificação gerencial/contábil da despesa.  
Obrigatório: Opcional (133 nulos – 76%)  
Exemplos: `Mão de Obra Direta`, `Materiais Aplicados na Prestação de Serviços`, `Imposto Federal`, `Condomínio`, `Honorários Advocatícios`, `Honorários Contábeis`, `Adiantamento Salarial`, `Imposto Municipal`, `Exames Médicos`  
Observação: Campo importante para classificação, porém pouco preenchido.

**Campo: Cliente**  
Tipo: Texto  
Descrição: Cliente associado (quando aplicável).  
Obrigatório: Não  
Exemplo: (todos nulos)  
Observação: Coluna vazia em 100% dos registros.

**Campo: Fornecedor**  
Tipo: Texto  
Descrição: Nome do fornecedor/prestador de serviço/beneficiário do pagamento.  
Obrigatório: Sim  
Exemplo: `BH MATERIAIS DE CONSTRUCAO`, `UP ESQUADRIAS`, `Ismael Lima Alves`, `COMERCIAL RIO SENNA LTDA ME`, `CENTRAL LOC`  
Observação: Campo crítico para matching. Contém tanto pessoas físicas quanto jurídicas. Variação de grafia existe.

**Campo: Métodos de pagamento**  
Tipo: Texto  
Descrição: Método de pagamento cadastrado na despesa.  
Obrigatório: Opcional (156 nulos)  
Exemplo: raramente preenchido  
Observação: Pouco utilizado; a informação útil está em “Forma de pagamento parcela”.

**Campo: Data de competência**  
Tipo: Data (texto dd/mm/yyyy)  
Descrição: Data de competência contábil/gerencial da despesa.  
Obrigatório: Sim  
Exemplo: `01/06/2026`, `27/05/2026`, `03/06/2026`  
Observação: Pode ser anterior ao período de pagamento (competência ≠ caixa).

**Campo: Projeto**  
Tipo: Texto / Lista de valores  
Descrição: Obra/projeto ao qual a despesa está vinculada.  
Obrigatório: Sim  
Exemplos:  

- `PROJ02 - Casa Bioma` (106)  
- `B01 - Residência Nilson e Laura` (55)  
- `PROJ01 - Casa Mina` (12)  
- `Lote 296C` (1)  
Observação: Campo estratégico para custo por obra.

**Campo: Conta bancária**  
Tipo: Texto / Lista de valores  
Descrição: Conta bancária de onde o pagamento foi (ou será) efetuado.  
Obrigatório: Quase sempre (2 nulos)  
Exemplos: `Conta VNP` (118), `Conta Casa Nilson` (54)  
Observação: Mapeia diretamente para as contas do extrato bancário.

**Campo: Centro de custo**  
Tipo: Texto  
Descrição: Centro de custo.  
Obrigatório: Não  
Exemplo: (100% nulo)  
Observação: Coluna existente mas não utilizada neste export.

**Campo: Valor total**  
Tipo: Moeda (número negativo)  
Descrição: Valor total da despesa (soma das parcelas).  
Obrigatório: Sim  
Exemplo: `-1392.2`, `-132500.0`, `-18.75`  
Observação: Sempre negativo (padrão de despesa/saída). Range: –132.500 a –18,75.

**Campo: Parcela**  
Tipo: Texto  
Descrição: Descrição da parcela específica.  
Obrigatório: Sim  
Exemplo: `Materiais diversos 1/1`, `Esquadrias Bioma - Entrada 1/4`, `Pedras 2/2`, `FORNECIMENTO DE CIMENTO 1/2`  
Observação: Indica se é parcela única ou parte de um parcelamento (n/m).

**Campo: Valor parcela**  
Tipo: Moeda (número negativo)  
Descrição: Valor da parcela específica.  
Obrigatório: Sim  
Exemplo: `-1392.2`, `-33500.0`, `-4642.0`  
Observação: Em despesas de parcela única, coincide com Valor total.

**Campo: Vencimento parcela**  
Tipo: Data (texto dd/mm/yyyy)  
Descrição: Data de vencimento da parcela.  
Obrigatório: Sim  
Exemplo: `01/06/2026`, `06/07/2026`  

**Campo: Status parcela**  
Tipo: Lista de valores  
Descrição: Status da parcela.  
Obrigatório: Sim  
Exemplo: `Pago` (100% dos registros)  

**Campo: Data de pagamento parcela**  
Tipo: Data (texto dd/mm/yyyy)  
Descrição: Data em que a parcela foi efetivamente paga.  
Obrigatório: Sim  
Exemplo: `01/06/2026`, `26/06/2026`, `30/06/2026`  
Observação: Campo mais importante para conciliação com o extrato bancário.

**Campo: Forma de pagamento parcela**  
Tipo: Lista de valores  
Descrição: Meio de pagamento utilizado na liquidação da parcela.  
Obrigatório: Sim  
Exemplos: `PIX` (149), `Boleto` (25)  

**Campo: ID Parcela**  
Tipo: Código (UUID)  
Descrição: Identificador único da parcela.  
Obrigatório: Sim  
Exemplo: `d5446c37-40ac-441b-9114-b2a1bbcf3029`  
Observação: UUID. Único em todo o arquivo (chave natural ideal da linha).

**Campo: Notas fiscais**  
Tipo: Texto / Código  
Descrição: Número(s) da nota fiscal vinculada.  
Obrigatório: Opcional (162 nulos – 93%)  
Exemplos: `124.139`, `124.140`, `000.006.628`, `ND-072163`, `498`  
Observação: Quando preenchido, é excelente chave de matching com documentos fiscais e razão contábil.

**Campo: Juros**  
Tipo: Moeda  
Descrição: Valor de juros cobrado na parcela.  
Obrigatório: Opcional  
Exemplo: `0` (quando preenchido)  
Observação: Praticamente não utilizado.

**Campo: Multa**  
Tipo: Moeda  
Descrição: Valor de multa.  
Obrigatório: Sim (sempre 0)  

**Campo: Desconto**  
Tipo: Moeda  
Descrição: Valor de desconto.  
Obrigatório: Sim (sempre 0)  

**Campo: Empresa**  
Tipo: Texto  
Descrição: Empresa responsável pela despesa.  
Obrigatório: Sim  
Exemplo: `VNP EMPREENDIMENTOS IMOBILIARIOS LTDA`  
Observação: Valor único.

---

### 3. ANÁLISE DOS DADOS

- **Quantidade de linhas**: 174 (dados) + 1 cabeçalho.
- **Quantidade de colunas**: 25.
- **Campos vazios relevantes**:
  - Cliente: 100%
  - Centro de custo: 100%
  - Categoria financeira: 76%
  - Métodos de pagamento: 90%
  - Notas fiscais: 93%
  - Juros: maioria nulo ou zero
- **Dados duplicados**:
  - ID da despesa se repete em 3 casos (despesas com 2 parcelas).
  - ID Parcela é único (bom).
- **Inconsistências aparentes**:
  - Valores sempre negativos (padrão do sistema de origem).
  - Datas em formato texto brasileiro (dd/mm/yyyy).
  - Algumas datas de competência anteriores a junho/2026 (competência ≠ caixa).
  - Uma despesa “Em aberto” no Status, porém Status parcela = “Pago” e com data de pagamento preenchida (possível inconsistência de status do título vs parcela).
  - Conta bancária nula em 2 registros.
  - Variação de grafia em nomes de fornecedores (ex.: “Isaías” vs “Isaias”, “VISÃO HIDRÁULICA” vs “Visão Hidráulica”).
- **Formatos diferentes no mesmo campo**: Datas como string; valores monetários como float negativo.
- **Problemas para integração**:
  1. Datas como texto → necessidade de parsing robusto.
  2. Valores negativos → padronizar sinal conforme convenção do sistema destino.
  3. Baixo preenchimento de Categoria financeira e Notas fiscais reduz qualidade do matching automático.
  4. Fornecedor sem documento (CNPJ/CPF) estruturado → matching por nome fuzzy é necessário.
  5. Parcelas de uma mesma despesa compartilham o mesmo ID (tratar como cabeçalho + itens).

---

### 4. IDENTIFICAÇÃO DE ENTIDADES DE NEGÓCIO

**Despesa (Título)**  

- ID (UUID)  
- Nome  
- Status  
- Categoria financeira  
- Data de competência  
- Valor total  
- Fornecedor  
- Projeto  
- Conta bancária  
- Empresa  

**ParcelaDespesa**  

- ID Parcela (UUID)  
- Despesa ID  
- Descrição da parcela  
- Valor parcela  
- Vencimento  
- Status parcela  
- Data de pagamento  
- Forma de pagamento  
- Juros / Multa / Desconto  
- Nota fiscal  

**Fornecedor**  

- Nome (único campo disponível)  
- (Hipótese futura: CNPJ/CPF extraído de observações ou de outros sistemas)

**Projeto / Obra**  

- Código + Nome (`PROJ02 - Casa Bioma`, `B01 - Residência Nilson e Laura`, etc.)

**ContaBancaria** (visão gerencial)  

- Nome (`Conta VNP`, `Conta Casa Nilson`)

**CategoriaFinanceira**  

- Nome da categoria

**Empresa**  

- Razão social

Entidades prioritárias para tabelas: `despesa`, `parcela_despesa`, `fornecedor`, `projeto`, `categoria_financeira`, `conta_bancaria_gerencial`.

---

### 5. REGRAS DE NEGÓCIO IDENTIFICADAS

- Valores de despesa e parcela são sempre **negativos** (convenção do sistema de origem).
- Uma Despesa (ID) pode ter uma ou mais Parcelas (ID Parcela). A grande maioria é 1:1; existem poucos casos 1:2.
- Status da parcela é “Pago” em 100% dos registros deste export (mesmo quando o Status do título está “Em aberto”).
- Data de pagamento da parcela é o campo que deve ser usado para conciliação com o extrato bancário.
- Forma de pagamento dominante é PIX; Boleto aparece em menor volume.
- Projeto é obrigatório e altamente discriminante (custo por obra).
- Categoria financeira e Nota fiscal são opcionais e pouco preenchidas.
- Conta bancária gerencial (`Conta VNP` × `Conta Casa Nilson`) determina de qual conta física o dinheiro saiu.
- Existe relação clara entre Fornecedor + Valor + Data de pagamento e as movimentações do extrato bancário e da razão contábil.

---

### 6. RELACIONAMENTOS

**Com o Extrato Bancário** (`Extrato-01-06-2026-a-30-06-2026-PDF.xlsx`):

- ParcelaDespesa ↔ MovimentacaoBancaria  
  Chaves candidatas:  
  - Data de pagamento parcela ≈ Data do extrato  
  - Valor parcela (absoluto) ≈ Valor do extrato  
  - Nome do Fornecedor ≈ trecho da descrição / código Cp :  
  - Conta bancária gerencial → Conta física do extrato  

**Com a Razão Contábil** (`Razão SUCESSOR.xlsx`):

- ParcelaDespesa ↔ LancamentoContabil  
  Chaves candidatas:  
  - Valor + Data  
  - Nota fiscal (quando existir)  
  - Histórico × Nome da despesa / Fornecedor  
  - Conta de contrapartida (Contra) pode ser derivada da Categoria financeira ou Projeto  

**Outros relacionamentos internos**:

- Despesa 1:N ParcelaDespesa (via ID)
- Despesa N:1 Fornecedor
- Despesa N:1 Projeto
- Despesa N:1 ContaBancaria gerencial
- Despesa N:1 CategoriaFinanceira
- Despesa N:1 Empresa

---

### 7. PROPOSTA DE MODELO DE DADOS

**Tabela: empresa**  
Campos: id, razao_social, cnpj (futuro)  
Chave primária: id

**Tabela: projeto**  
Campos: id, codigo, nome, descricao  
Chave primária: id  
Exemplo de dados: PROJ02, B01, PROJ01, Lote 296C

**Tabela: fornecedor**  
Campos: id, nome_canonico, nome_original, documento (nullable), tipo_pessoa  
Chave primária: id

**Tabela: categoria_financeira**  
Campos: id, nome, natureza  
Chave primária: id

**Tabela: conta_bancaria_gerencial**  
Campos: id, nome, conta_contabil_id (link futuro), banco_conta_fisica  
Chave primária: id

**Tabela: despesa**  
Campos: id (UUID origem), nome, status, categoria_financeira_id, data_competencia, valor_total, fornecedor_id, projeto_id, conta_bancaria_id, empresa_id, origem_sistema, arquivo_origem  
Chave primária: id (UUID)  
Relacionamentos: N:1 com fornecedor, projeto, categoria, conta, empresa

**Tabela: parcela_despesa**  
Campos: id (UUID origem), despesa_id, descricao_parcela, numero_parcela, total_parcelas, valor_parcela, data_vencimento, status_parcela, data_pagamento, forma_pagamento, nota_fiscal, juros, multa, desconto, hash_unicidade  
Chave primária: id (UUID)  
Relacionamentos: N:1 despesa  
Índice único sugerido: id (UUID da parcela)

---

### 8. VISÃO PARA DESENVOLVIMENTO DE SOFTWARE

**Como a planilha entra no sistema**  
Ingestão periódica (diária/semanal/mensal) de exportações do sistema de gestão financeira. Pode ser via upload manual, pasta monitorada ou API do sistema de origem (se disponível).

**Processo de importação recomendado**

1. Leitura do Excel (aba “Exportado”).
2. Validação de schema (colunas esperadas).
3. Parsing de datas (dd/mm/yyyy → date).
4. Normalização de valores (manter sinal ou converter para positivo + tipo “despesa”).
5. Separação cabeçalho (Despesa) × itens (Parcela) usando o campo ID.
6. Upsert de Fornecedor, Projeto, Categoria e Conta Bancária gerencial (deduplicação por nome normalizado).
7. Carga das despesas e parcelas com preservação dos UUIDs de origem.
8. Geração de hash de conciliação (data_pagamento + valor_absoluto + fornecedor_normalizado).
9. Enfileiramento para o motor de matching com extrato e razão.

**Validações necessárias**

- ID e ID Parcela no formato UUID.
- Valor total ≈ soma das parcelas da mesma despesa (tolerância de arredondamento).
- Data de pagamento não nula quando Status parcela = “Pago”.
- Projeto e Fornecedor obrigatórios.
- Consistência de status (título × parcela).

**Transformações necessárias**

- Conversão de datas.
- Normalização de nomes de fornecedor (uppercase, remoção de acentos, abreviações).
- Extração de CNPJ/CPF quando aparecer em campos de texto (observações futuras).
- Padronização de forma de pagamento (PIX / Boleto).
- Criação de chave de matching composta.

**APIs / Serviços futuros**

- Motor de Conciliação tripartite (Despesa × Extrato × Razão)
- Custo por Obra / Projeto em tempo real
- Fluxo de caixa realizado × previsto
- Classificação automática de categoria financeira (ML)
- Integração com ERP contábil e sistema de gestão de obras
- Dashboard de contas a pagar e aging

---

### 9. RESUMO TÉCNICO PARA CONTINUIDADE DO DESENVOLVIMENTO

**Resumo Técnico para Continuidade do Desenvolvimento**

Esta planilha representa o **cadastro e liquidação de despesas** (contas a pagar) da VNP Empreendimentos Imobiliários Ltda para junho/2026, exportada de um sistema de gestão financeira. É a visão de **negócio/orçamento/obra** que completa o triângulo da conciliação:

1. Extrato Bancário (caixa)
2. Razão Contábil (contabilidade)
3. **Despesas** (gestão financeira + custo por projeto)

**Entidades principais**:

- Despesa (título)
- ParcelaDespesa
- Fornecedor
- Projeto/Obra
- CategoriaFinanceira
- ContaBancaria gerencial

**Campos críticos**:

- **ID Parcela** (UUID – chave natural da linha)
- **ID** da despesa (UUID – agrupa parcelas)
- Data de pagamento parcela
- Valor parcela (sinal negativo)
- Fornecedor
- Projeto
- Conta bancária
- Forma de pagamento
- Nota fiscal (quando existir)

**Regras identificadas**:

- Valores sempre negativos.
- Relação 1:N entre Despesa e Parcela (maioria 1:1).
- Projeto e Fornecedor são dimensões obrigatórias e de alto valor analítico.
- Data de pagamento é o elo principal com o extrato bancário.
- Categoria financeira e Nota fiscal estão subutilizadas no export atual.

**Cuidados obrigatórios na implementação**:

1. Preservar os UUIDs originais (ID e ID Parcela) como chaves de origem.
2. Tratar corretamente despesas parceladas (mesmo ID, múltiplos ID Parcela).
3. Normalizar nomes de fornecedores para matching fuzzy com extrato e razão.
4. Converter datas de string brasileira para tipo data.
5. Decidir convenção de sinal (manter negativo ou positivar + flag de natureza).
6. Mapear `Conta VNP` e `Conta Casa Nilson` para as contas físicas do extrato/razão.
7. Usar Projeto como dimensão analítica principal de custo.
8. Projetar o motor de matching com scoring (valor + data + fornecedor + conta + nota fiscal).

Este arquivo, em conjunto com o Extrato Bancário e a Razão Contábil já documentados, forma a base completa de dados necessária para o desenho do Modelo Canônico de Conciliação, do motor de matching e da arquitetura do sistema de automação financeira/contábil da SPE.
