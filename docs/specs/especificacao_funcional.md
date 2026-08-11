# ESPECIFICAÇÃO FUNCIONAL E DE DADOS

## Plataforma Corporativa de Integração entre ERPs de Construtoras e Sistema Contábil

**Versão:** 1.0
**Documento:** Modelo de Domínio, Dados e Fluxos de Negócio

---

# 77. Objetivo desta Especificação

Esta etapa tem como objetivo definir a estrutura conceitual das informações que trafegarão pela plataforma.

O princípio adotado é:

> O ERP de origem não define o modelo interno da plataforma.

O modelo interno deverá representar as necessidades do negócio contábil.

Dessa forma, os diferentes ERPs serão adaptados ao modelo corporativo.

---

# 78. Arquitetura de Dados

A arquitetura de dados será organizada em quatro níveis:

```text
┌──────────────────────────────┐
│ DADOS DE ORIGEM              │
│ ERP / Arquivo / API / Banco  │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│ RAW                          │
│ Dados originais              │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│ NORMALIZAÇÃO                 │
│ Transformação estrutural     │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│ MODELO CANÔNICO              │
│ Modelo corporativo           │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│ MODELO DE DESTINO            │
│ Sistema contábil             │
└──────────────────────────────┘
```

---

# 79. Entidades Principais

O modelo inicial deverá considerar as seguintes entidades:

```text
Tenant
Company
ERP
Integration
Person
Customer
Supplier
Employee
Project
Construction
Contract
CostCenter
Account
Tax
Invoice
InvoiceItem
Payment
Receivable
Payable
AccountingEntry
Document
Processing
ProcessingItem
ProcessingError
AuditEvent
```

A modelagem definitiva dependerá do levantamento dos processos contábeis.

---

# 80. Tenant

Representa a empresa cliente dentro da plataforma.

Exemplo:

```text
Tenant
--------------------------------
id
name
document
status
createdAt
updatedAt
```

O `Tenant` é a principal unidade de isolamento lógico da plataforma.

---

# 81. ERP

Representa o sistema utilizado pelo cliente.

```text
ERP
--------------------------------
id
tenantId
type
name
version
status
createdAt
```

Exemplo:

```text
Tenant: Construtora A
ERP: ERP_X
```

Outro cliente:

```text
Tenant: Construtora B
ERP: ERP_Y
```

---

# 82. Integration

Representa uma configuração de integração.

```text
Integration
--------------------------------
id
tenantId
erpId
destination
status
schedule
lastExecution
nextExecution
```

Um mesmo cliente poderá futuramente possuir múltiplas integrações.

---

# 83. Person

Entidade base para pessoas físicas e jurídicas.

```text
Person
--------------------------------
id
tenantId
type
document
name
email
phone
address
status
```

Especializações:

```text
Person
  │
  ├── Customer
  ├── Supplier
  └── Employee
```

---

# 84. Supplier

Representa fornecedores.

Informações possíveis:

* CNPJ/CPF;
* razão social;
* nome fantasia;
* endereço;
* município;
* UF;
* contatos;
* situação cadastral;
* código externo.

O código do ERP deverá ser preservado como referência externa.

---

# 85. Customer

Representa clientes da construtora.

Poderá conter:

* CPF/CNPJ;
* nome;
* endereço;
* contatos;
* código externo;
* status.

---

# 86. Project / Obra

Esta entidade é especialmente importante para o contexto de construção civil.

```text
Project
--------------------------------
id
tenantId
externalId
code
name
description
status
startDate
endDate
```

Uma construtora poderá possuir dezenas ou centenas de obras.

---

# 87. Cost Center

Centro de custo:

```text
CostCenter
--------------------------------
id
tenantId
externalId
code
description
parentId
status
```

A hierarquia deverá ser suportada quando existir.

Exemplo:

```text
OBRA 001
 ├── Administrativo
 ├── Materiais
 ├── Mão de Obra
 └── Equipamentos
```

---

# 88. Accounting Account

Representa a conta contábil.

```text
Account
--------------------------------
id
tenantId
externalId
code
description
type
parentId
status
```

É importante separar:

**Conta do ERP**

de

**Conta contábil de destino.**

O relacionamento poderá ser parametrizado.

---

# 89. Mapping

O conceito de mapeamento será fundamental.

Exemplo:

```text
Mapping
--------------------------------
id
tenantId
sourceSystem
sourceType
sourceCode
targetType
targetCode
validFrom
validUntil
status
```

Exemplo:

```text
ERP:
Conta 4.01.002

↓

Contabilidade:
Conta 3.2.01.05
```

---

# 90. Invoice

Representa documento fiscal/financeiro.

```text
Invoice
--------------------------------
id
tenantId
externalId
number
series
issueDate
dueDate
supplierId
customerId
projectId
totalAmount
status
```

---

# 91. Invoice Item

Itens da nota:

```text
InvoiceItem
--------------------------------
id
invoiceId
description
quantity
unitPrice
totalAmount
costCenterId
accountId
taxId
```

---

# 92. Payment

Representa pagamentos.

```text
Payment
--------------------------------
id
tenantId
externalId
invoiceId
paymentDate
amount
bankAccount
status
```

---

# 93. Accounting Entry

Representa o lançamento contábil.

```text
AccountingEntry
--------------------------------
id
tenantId
externalId
date
description
accountId
costCenterId
debit
credit
documentId
status
```

---

# 94. Processing

Representa uma execução de integração.

```text
Processing
--------------------------------
id
tenantId
integrationId
correlationId
startedAt
finishedAt
status
totalRecords
successRecords
errorRecords
```

Status possíveis:

```text
RECEIVED
PROCESSING
COMPLETED
PARTIAL
FAILED
CANCELLED
```

---

# 95. Processing Item

Cada registro processado deverá poder ser rastreado individualmente.

```text
ProcessingItem
--------------------------------
id
processingId
externalId
entityType
status
errorCode
processedAt
```

Isso permite saber exatamente quais registros foram processados.

---

# 96. Processing Error

```text
ProcessingError
--------------------------------
id
processingItemId
code
message
severity
retryable
createdAt
resolvedAt
```

Exemplo:

```text
Código: ACCOUNT_NOT_MAPPED

Mensagem:
A conta 4.02.003 não possui mapeamento
para o plano contábil de destino.

Retryable:
false
```

---

# 97. Audit Event

Toda operação importante deverá gerar evento de auditoria.

```text
AuditEvent
--------------------------------
id
tenantId
userId
action
entityType
entityId
timestamp
metadata
```

Exemplo:

```text
Usuário alterou mapeamento
Conta ERP: 4001
Conta destino: 5.2.03
Data: XX/XX/XXXX
```

---

# 98. Dicionário de Dados

A plataforma deverá possuir um dicionário formal.

Exemplo:

| Campo       | Tipo    | Obrigatório | Descrição                |
| ----------- | ------- | ----------: | ------------------------ |
| tenantId    | UUID    |         Sim | Identificador do cliente |
| externalId  | String  |         Sim | ID do sistema de origem  |
| document    | String  |         Não | CPF/CNPJ                 |
| name        | String  |         Sim | Nome                     |
| issueDate   | Date    |         Sim | Data de emissão          |
| totalAmount | Decimal |         Sim | Valor total              |
| projectId   | UUID    |         Não | Obra relacionada         |

Esse dicionário deverá ser versionado.

---

# 99. Regras de Normalização

Exemplos:

### Datas

Todos os sistemas deverão ser convertidos para um padrão interno.

### Valores monetários

Deverão ser tratados com precisão decimal adequada, evitando cálculos financeiros baseados em ponto flutuante inadequado.

### Documentos

CPF/CNPJ deverão possuir formato interno padronizado.

### Textos

Deverão possuir normalização definida para evitar inconsistências de codificação.

---

# 100. Regras de Identificação

Um dos principais problemas de integração é descobrir quando dois registros representam a mesma entidade.

Exemplo:

ERP A:

```text
123
Fornecedor ABC Ltda.
```

ERP B:

```text
987
ABC LTDA
```

O identificador externo não é suficiente.

A plataforma deverá definir regras de matching.

Possíveis critérios:

1. documento fiscal;
2. identificador externo;
3. combinação de campos;
4. regra configurável;
5. análise manual quando houver ambiguidade.

---

# 101. Master Data

Deverá ser definida a origem oficial de cada informação.

Por exemplo:

```text
Fornecedor
    ↓
ERP da construtora
```

ou:

```text
Plano contábil
    ↓
Sistema contábil
```

A plataforma não deverá permitir que duas fontes concorram indefinidamente pela autoridade sobre o mesmo dado.

---

# 102. Fluxo de Cadastro

Exemplo de fornecedor:

```text
ERP
 ↓
Extração
 ↓
Normalização
 ↓
Busca fornecedor existente
 ↓
Encontrado?
 ├── SIM → Atualização
 └── NÃO → Cadastro
```

---

# 103. Fluxo de Nota Fiscal

```text
ERP
 ↓
Extrair nota
 ↓
Validar documento
 ↓
Identificar fornecedor
 ↓
Identificar obra
 ↓
Identificar centro de custo
 ↓
Identificar conta
 ↓
Aplicar regras
 ↓
Gerar modelo canônico
 ↓
Enviar ao sistema contábil
 ↓
Registrar resultado
```

---

# 104. Fluxo de Erro

```text
Registro
 ↓
Validação
 ↓
ERRO
 ↓
Classificação
 │
 ├── Técnico
 ├── Cadastro
 ├── Parametrização
 └── Regra de negócio
 ↓
Correção
 ↓
Reprocessamento
```

---

# 105. Classificação de Erros

## Erro Técnico

Exemplo:

```text
ERP indisponível
```

Pode permitir retry automático.

## Erro de Dados

Exemplo:

```text
CNPJ inválido
```

Necessita correção na origem.

## Erro de Parametrização

Exemplo:

```text
Conta não mapeada
```

Necessita ajuste de configuração.

## Erro de Regra

Exemplo:

```text
Período contábil fechado
```

Necessita decisão operacional.

---

# 106. Máquina de Estados

Uma integração poderá utilizar:

```text
CREATED
   ↓
SCHEDULED
   ↓
RUNNING
   ↓
VALIDATING
   ↓
PROCESSING
   ↓
EXPORTING
   ↓
COMPLETED
```

Em caso de problema:

```text
RUNNING
   ↓
FAILED
   ↓
RETRYING
   ↓
RUNNING
```

Ou:

```text
VALIDATING
   ↓
PARTIAL
```

quando apenas parte dos registros apresentar problemas.

---

# 107. Modelo de Eventos

A arquitetura poderá utilizar eventos internos.

Exemplos:

```text
ImportStarted
ImportCompleted
ImportFailed
RecordReceived
RecordValidated
RecordRejected
RecordProcessed
ExportCompleted
```

Isso permitirá evolução futura para arquitetura orientada a eventos.

---

# 108. Contratos de Integração

Cada connector deverá possuir um contrato.

Exemplo conceitual:

```text
extractSuppliers()
extractCustomers()
extractProjects()
extractInvoices()
extractPayments()
```

O connector retorna dados em um formato interno intermediário.

O restante da plataforma não precisa conhecer o formato original.

---

# 109. Separação entre Adapter e Domain

Uma regra importante:

```text
ERP
 ↓
Adapter
 ↓
DTO de origem
 ↓
Mapper
 ↓
Domain Model
```

Não devemos permitir que classes específicas do ERP contaminem o domínio central.

Isso evita que o sistema se torne dependente de uma tecnologia específica.

---

# 110. Estratégia de Configuração

Configurações específicas de cliente deverão ser armazenadas fora do código.

Exemplo:

```text
Tenant A

ERP:
ERP_A

Importação:
02:00

Conta:
4001 → 5.1.02

Centro:
OBRA-001 → CC-100
```

Isso permitirá alteração sem nova implantação da aplicação.

---

# 111. Segurança por Tenant

Toda consulta deverá possuir contexto de tenant.

Conceitualmente:

```text
Request
 ↓
Authenticated User
 ↓
Tenant Context
 ↓
Authorization
 ↓
Database Query
```

O tenant nunca deverá ser simplesmente confiado a um parâmetro enviado pelo cliente sem validação de autorização.

---

# 112. Estratégia de Auditoria

A auditoria deverá registrar, no mínimo:

* quem;
* quando;
* o quê;
* origem;
* valor anterior;
* valor novo;
* motivo;
* resultado.

Isso será especialmente importante para alterações de parametrização.

---

# 113. Retenção

Deverão ser definidas políticas para:

* dados operacionais;
* arquivos originais;
* logs;
* auditoria;
* erros;
* backups.

O período de retenção deverá ser definido de acordo com requisitos legais, contábeis, contratuais e de negócio.

---

# 114. Arquitetura de Ambientes

```text
DESENVOLVIMENTO
      ↓
INTEGRAÇÃO
      ↓
HOMOLOGAÇÃO
      ↓
PRODUÇÃO
```

Dados reais de produção não deverão ser utilizados indiscriminadamente nos ambientes inferiores.

---

# 115. Estratégia de Homologação

Cada novo ERP deverá possuir um conjunto de dados conhecido.

Exemplo:

```text
Dataset de Homologação ERP A
--------------------------------
10 fornecedores
10 clientes
5 obras
100 notas
50 pagamentos
```

O resultado esperado deverá ser previamente definido.

Isso permitirá testes automatizados de regressão.

---

# 116. Teste de Contrato

Sempre que possível, o connector deverá possuir testes que validem:

```text
ERP
 ↓
Connector
 ↓
Modelo esperado
```

Se o fornecedor do ERP alterar uma API, o teste deverá detectar a alteração antes de chegar à produção.

---

# 117. Teste de Reprocessamento

Um cenário obrigatório:

```text
Importação
 ↓
Erro
 ↓
Correção
 ↓
Retry
 ↓
Sucesso
```

E um segundo cenário:

```text
Importação
 ↓
Sucesso
 ↓
Mesma importação novamente
 ↓
Nenhuma duplicidade
```

---

# 118. Teste de Indisponibilidade

Outro cenário fundamental:

```text
ERP indisponível
 ↓
Connector tenta conexão
 ↓
Retry
 ↓
Falha
 ↓
Alerta
 ↓
Processamento permanece pendente
 ↓
ERP retorna
 ↓
Reprocessamento
```

A plataforma não deverá simplesmente perder o processamento.

---

# 119. Requisitos para o Primeiro ERP

Antes de desenvolver o primeiro connector, deverão ser levantados:

* documentação da API;
* autenticação;
* limites de requisição;
* paginação;
* endpoints;
* estrutura de dados;
* eventos;
* filtros;
* histórico;
* exclusões;
* atualizações;
* disponibilidade;
* ambiente de homologação.

Se não existir API:

* formato de exportação;
* frequência;
* estrutura dos arquivos;
* banco;
* acesso;
* permissões;
* mecanismo de atualização.

---

# 120. Checklist de Discovery

Antes do desenvolvimento, a equipe deverá responder:

### Origem

* Qual ERP?
* Qual versão?
* Existe API?
* Existe documentação?
* Existe ambiente de testes?

### Dados

* Quais entidades serão importadas?
* Qual volume?
* Qual frequência?
* Existe histórico?

### Destino

* Qual sistema contábil?
* Existe API?
* Existe layout de importação?
* Quais campos são obrigatórios?

### Negócio

* Quais regras contábeis?
* Quais mapeamentos?
* Quem valida?
* Quem corrige?

### Segurança

* Quais dados pessoais?
* Quem pode acessar?
* Como as credenciais serão armazenadas?

---

# 121. Critério para Escolha do Primeiro ERP

O primeiro ERP não deve necessariamente ser o mais simples.

Idealmente, deve ser suficientemente representativo para validar a arquitetura.

Critérios:

* volume relevante;
* cliente estratégico;
* variedade de dados;
* integração tecnicamente viável;
* disponibilidade de ambiente de testes;
* participação de usuários para homologação.

---

# 122. Critério de Aceitação do Primeiro Fluxo

Um fluxo deverá ser considerado concluído quando:

* dados forem extraídos automaticamente;
* dados originais forem preservados;
* transformação ocorrer;
* modelo canônico for gerado;
* validações forem executadas;
* erros forem registrados;
* dados válidos chegarem ao destino;
* processamento puder ser auditado;
* reprocessamento funcionar;
* nenhuma duplicidade for gerada.

---

# 123. Indicadores Técnicos do MVP

Sugere-se acompanhar:

```text
Taxa de sucesso
Taxa de rejeição
Tempo médio
Registros/hora
Falhas por ERP
Falhas por regra
Tempo de recuperação
Quantidade de intervenções manuais
```

Esses indicadores permitirão medir objetivamente a evolução da automação.

---

# 124. Arquitetura Evolutiva

A arquitetura deverá permitir a evolução:

```text
FASE 1
Monólito modular
+
Batch
+
1 ERP

        ↓

FASE 2
Múltiplos ERPs
+
Mensageria

        ↓

FASE 3
Escalabilidade horizontal
+
Portal administrativo

        ↓

FASE 4
Eventos
+
Near Real-Time

        ↓

FASE 5
Plataforma corporativa
+
Múltiplos destinos
```

Essa abordagem reduz o risco de tentar resolver todos os problemas simultaneamente.

---

# 125. Recomendação Final de Arquitetura

A recomendação técnica inicial é:

**Arquitetura modular + API + processamento assíncrono + modelo canônico + connectors independentes + banco relacional + armazenamento de objetos + observabilidade + auditoria.**

Microsserviços deverão ser utilizados somente quando houver justificativa operacional, de escala ou de domínio.

O principal ativo tecnológico da solução não será a linguagem de programação nem o framework escolhido.

Será a **arquitetura de integração e o modelo canônico de dados**.

---

# 126. Próximo Documento

Com esta especificação concluída, a próxima etapa natural será produzir o:

# DOCUMENTO DE ARQUITETURA DE IMPLEMENTAÇÃO

Esse documento deverá conter:

1. Arquitetura física;
2. Infraestrutura cloud/on-premise;
3. Diagrama detalhado de componentes;
4. Banco de dados;
5. APIs;
6. Filas;
7. Workers;
8. Connectors;
9. Segurança;
10. CI/CD;
11. Observabilidade;
12. Backup;
13. Disaster Recovery;
14. Monitoramento;
15. Estratégia de deploy;
16. Estrutura de código;
17. Organização dos repositórios;
18. Estratégia de versionamento;
19. Roadmap de desenvolvimento;
20. Estimativa de esforço por módulo.

Esse será o documento que permitirá sair da pergunta **“o que vamos construir?”** para **“como exatamente vamos construir?”**.
