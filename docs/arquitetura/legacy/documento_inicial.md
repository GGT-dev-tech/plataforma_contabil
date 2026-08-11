Perfeito. Vamos avançar para o próximo documento da linha de engenharia.

Agora entraremos no:

# Documento de Requisitos Funcionais (RF)

## Plataforma de Conciliação Financeira e Contábil Multissistema

**Versão:** 1.0
**Status:** Documento Inicial
**Baseado em:** Documento de Arquitetura de Software v1.0

---

# 1. Introdução

## 1.1 Objetivo

Este documento descreve os requisitos funcionais da plataforma de conciliação financeira e contábil.

O objetivo é definir **o que o sistema deverá fazer**, quais funcionalidades serão disponibilizadas aos usuários e quais regras de negócio deverão ser atendidas.

---

# 2. Perfis de Usuário

A solução deverá considerar inicialmente os seguintes perfis:

---

## RF-PERFIL-001 — Administrador do Sistema

Responsável por:

* configurar empresas;
* cadastrar usuários;
* controlar permissões;
* acompanhar integrações.

Permissões:

* acesso completo.

---

## RF-PERFIL-002 — Analista Financeiro

Responsável por:

* importar despesas;
* analisar pagamentos;
* revisar divergências;
* validar conciliações.

---

## RF-PERFIL-003 — Analista Contábil

Responsável por:

* importar razão contábil;
* analisar lançamentos;
* validar correspondência contábil.

---

## RF-PERFIL-004 — Auditor/Gestor

Responsável por:

* consultar relatórios;
* acompanhar indicadores;
* verificar histórico.

---

# 3. Módulo de Empresas

## RF-EMP-001 — Cadastro de Empresa

O sistema deverá permitir o cadastro das empresas participantes.

### Dados mínimos

* Razão social;
* CNPJ;
* Nome fantasia;
* Sistema de origem;
* Data de cadastro.

---

### Exemplo

```
Empresa:
VNP Empreendimentos Imobiliários Ltda

Sistema origem:
Financeiro próprio

Conta:
Banco Inter
```

---

# 4. Módulo de Projetos / Obras

## RF-PROJ-001 — Cadastro de Projetos

O sistema deverá permitir registrar os projetos vinculados às despesas.

Campos:

* Código do projeto;
* Nome;
* Empresa responsável.

Exemplo:

```
PROJ02
Casa Bioma

B01
Residência Nilson e Laura
```

---

# 5. Módulo de Importação de Arquivos

Esse é o primeiro módulo crítico do sistema.

---

# RF-IMP-001 — Upload de Arquivos

O sistema deverá permitir que usuários enviem arquivos financeiros e contábeis.

Formatos previstos:

* XLSX;
* CSV;
* PDF (futuro).

---

## Dados armazenados

Para cada arquivo:

* nome;
* usuário responsável;
* data de envio;
* empresa relacionada;
* tipo de arquivo;
* status do processamento.

---

Exemplo:

```
Arquivo:
Despesas 06-2026.xlsx

Tipo:
Financeiro

Status:
Processando
```

---

# RF-IMP-002 — Classificação Automática do Arquivo

O sistema deverá identificar o tipo de arquivo recebido.

Categorias:

* Despesas;
* Extrato bancário;
* Razão contábil;
* Outros.

---

Exemplo:

Arquivo recebido:

```
Razão SUCESSOR.xlsx
```

Sistema identifica:

```
Tipo:
Razão Contábil SCI
```

---

# RF-IMP-003 — Validação Inicial

Antes do processamento, o sistema deverá validar:

* extensão do arquivo;
* tamanho;
* estrutura mínima;
* campos obrigatórios.

---

Exemplo:

Arquivo:

```
Despesas.xlsx
```

Esperado:

```
Fornecedor
Valor parcela
Data pagamento parcela
```

Caso falte:

```
Erro:
Campo obrigatório ausente
```

---

# 6. Módulo de Normalização de Dados

Este módulo será responsável por transformar arquivos diferentes em um padrão interno.

---

# RF-NORM-001 — Normalização de Fornecedores

O sistema deverá padronizar nomes.

Exemplo:

Entrada:

```
UP ESQUADRIAS LTDA

UP ESQUADRIAS

Pix enviado UP Esquadrias
```

Resultado:

```
Fornecedor Canonizado:

UP ESQUADRIAS LTDA
```

---

# RF-NORM-002 — Normalização Monetária

O sistema deverá interpretar diferentes formatos.

Exemplos:

Entrada:

```
-R$ 1.392,20
```

Resultado:

```
-1392.20
```

---

Entrada:

```
149.795,17
```

Resultado:

```
149795.17
```

---

# RF-NORM-003 — Normalização de Datas

O sistema deverá converter diferentes formatos.

Exemplos:

Extrato:

```
1 de Junho de 2026
```

Resultado:

```
01/06/2026
```

---

Razão:

```
01/06/2026
```

Resultado:

```
01/06/2026
```

---

# 7. Módulo Modelo Canônico

Após tratamento, os dados deverão ser persistidos no modelo interno.

---

## RF-CAN-001 — Cadastro de Movimentação Bancária

O sistema deverá armazenar:

* data;
* histórico;
* valor;
* tipo operação;
* contraparte;
* saldo.

---

## RF-CAN-002 — Cadastro de Despesas

O sistema deverá armazenar:

* fornecedor;
* projeto;
* parcela;
* pagamento;
* valor.

---

## RF-CAN-003 — Cadastro de Lançamentos Contábeis

O sistema deverá armazenar:

* chave SCI;
* histórico;
* débito;
* crédito;
* conta contra.

---

# 8. Módulo de Conciliação

Este é o núcleo da aplicação.

---

# RF-CON-001 — Executar Conciliação Tripla

O sistema deverá permitir executar:

```
Despesa
   |
   |
Banco
   |
   |
Razão Contábil
```

---

# RF-CON-002 — Matching Automático

O sistema deverá comparar:

## Valor

Exemplo:

```
Despesa:
-1392,20

Banco:
-1392,20
```

---

## Data

Aceitar:

```
Pagamento:
10/06

Banco:
11/06
```

---

## Fornecedor

Comparar:

```
Fornecedor:
BH MATERIAIS

Banco:
PIX BH MATERIAIS
```

---

# RF-CON-003 — Gerar Score de Conciliação

Cada cruzamento deverá possuir um índice.

Exemplo:

```
Conciliação:

Fornecedor:
100%

Valor:
100%

Data:
90%

Nota fiscal:
100%


Score final:
97%

Status:
Conciliado
```

---

# RF-CON-004 — Classificação das Situações

O sistema deverá classificar:

## Conciliado

Quando:

```
Score >= 90%
```

---

## Revisão Manual

Quando:

```
70% <= Score < 90%
```

---

## Divergente

Quando:

```
Score < 70%
```

---

# 9. Módulo de Divergências

## RF-DIV-001 — Identificar pagamentos sem banco

Exemplo:

Existe:

```
Despesa:
UP ESQUADRIAS
R$ 33.500
```

Mas não existe:

```
Extrato Bancário
```

Resultado:

```
Pagamento não localizado
```

---

## RF-DIV-002 — Identificar saída bancária sem despesa

Exemplo:

Banco:

```
Tarifa bancária
R$ 50
```

Não encontrado:

```
Controle financeiro
```

Resultado:

```
Despesa não identificada
```

---

## RF-DIV-003 — Identificar lançamento contábil ausente

Exemplo:

Banco:

```
PIX R$ 5.000
```

Existe:

```
Despesa
```

Mas não existe:

```
Razão SCI
```

Resultado:

```
Lançamento contábil pendente
```

---

# 10. Módulo de Relatórios

## RF-REL-001 — Relatório Executivo

Gerar:

* total de despesas;
* total movimentado banco;
* total contabilizado;
* divergências.

---

## RF-REL-002 — Relatório Analítico

Detalhar:

* item conciliado;
* item pendente;
* score;
* origem dos dados.

---

## RF-REL-003 — Exportação Excel

Gerar arquivo:

```
Relatorio_Conciliacao_06-2026.xlsx
```

Com abas:

```
Itens Conciliados

Pendências

Divergências
```

---

# 11. Histórico e Auditoria

## RF-AUD-001

O sistema deverá registrar:

* usuário;
* data;
* arquivo processado;
* alterações realizadas;
* resultado da conciliação.

---

# 12. Requisitos Funcionais Prioritários para MVP

A primeira versão deverá entregar:

| Prioridade | Funcionalidade            |
| ---------- | ------------------------- |
| Alta       | Upload de arquivos        |
| Alta       | Parser das três fontes    |
| Alta       | Modelo canônico           |
| Alta       | Motor de conciliação      |
| Alta       | Relatório de divergências |
| Média      | Dashboard                 |
| Média      | Controle de usuários      |
| Baixa      | Integrações API           |

---

## Próximo documento recomendado

Agora que temos:

✅ Arquitetura
✅ Requisitos Funcionais

O próximo passo técnico correto é criar:

# Documento de Requisitos Não Funcionais (RNF)

Ele vai definir:

* segurança;
* performance;
* escalabilidade;
* disponibilidade;
* padrões de código;
* banco de dados;
* logs;
* LGPD;
* critérios de produção.

Depois disso entramos no:

**Modelo de Dados Canônico + DER + UML.**

Vou seguir nessa sequência.
