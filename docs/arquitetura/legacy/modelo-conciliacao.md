Perfeito. Vou continuar a construção do projeto assumindo o papel de **Tech Lead + Analista de Sistemas Sênior**, mantendo a visão de arquitetura, contabilidade e engenharia de software.

Até aqui temos os três pilares documentados:

1. **Despesas 06-2026.xlsx** → visão financeira/gerencial (contas a pagar)
2. **Extrato Bancário Banco Inter** → visão financeira real (movimentação de caixa)
3. **Razão SUCESSOR SCI** → visão contábil oficial

Agora vamos avançar para a próxima etapa técnica.

# 10. MODELO DE CONCILIAÇÃO TRIPARTITE (VISÃO FUNCIONAL)

## 10.1 Objetivo do Motor de Conciliação

O objetivo principal do sistema será automatizar a validação entre três fontes distintas de informação:

```
              SISTEMA FINANCEIRO
              Despesas.xlsx
                    |
                    |
                    ↓
            +----------------+
            |                |
            | Motor de       |
            | Conciliação    |
            | Inteligente    |
            |                |
            +----------------+
             ↑             ↑
             |             |
             |             |
Extrato Bancário      Razão Contábil
 Banco Inter          SCI Sucessor
```

O sistema deverá responder:

* O pagamento previsto realmente saiu do banco?
* O valor pago corresponde ao fornecedor correto?
* O lançamento bancário foi contabilizado?
* Existe alguma despesa paga sem contabilização?
* Existe algum lançamento contábil sem origem financeira?
* Existem diferenças de valor, data ou classificação?

---

# 10.2 Fluxo Macro do Processo

## Etapa 1 - Ingestão dos Arquivos

Entrada:

```
/uploads

├── Despesas 06-2026.xlsx
├── Extrato-01-06-2026-a-30-06-2026-PDF.xlsx
└── Razão SUCESSOR.xlsx
```

O sistema recebe os arquivos.

Cada arquivo passa por:

* validação de formato;
* identificação do tipo;
* leitura;
* armazenamento original;
* processamento.

---

# 10.3 Camada de Staging (Dados Brutos)

Uma decisão importante de arquitetura:

**Nunca devemos jogar diretamente os dados importados no banco final.**

Precisamos de uma camada intermediária.

Exemplo:

```
Arquivo Original
       |
       |
       ↓
+----------------+
| STAGING        |
| Dados brutos   |
+----------------+
       |
       |
       ↓
+----------------+
| CANONICAL      |
| Dados limpos   |
+----------------+
       |
       |
       ↓
+----------------+
| MATCH ENGINE   |
| Conciliação    |
+----------------+
```

Motivo:

* auditoria;
* rastreabilidade;
* possibilidade de reprocessamento;
* correção de regras sem perder origem.

---

# 10.4 Modelo Canônico Inicial

Esse será o modelo independente do sistema de origem.

Ou seja:

Hoje temos:

* SCI
* Excel financeiro
* Banco Inter

Amanhã pode entrar:

* Sienge
* Mega
* TOTVS
* SAP
* outro ERP de construtora

O sistema não deve depender deles.

---

# Entidades principais

# Empresa

Representa a SPE.

Tabela:

```
empresa
```

Campos:

```
id
razao_social
cnpj
created_at
```

---

# Projeto / Obra

Muito importante para construção civil.

```
projeto
```

Campos:

```
id
codigo
nome
descricao
```

Exemplo:

```
PROJ02
Casa Bioma

PROJ01
Casa Mina
```

---

# Fornecedor

Tabela:

```
fornecedor
```

Campos:

```
id

nome_original

nome_normalizado

documento

tipo_pessoa
```

Exemplo:

Origem:

```
UP ESQUADRIAS LTDA
```

Normalizado:

```
UP ESQUADRIAS
```

Isso será usado no matching.

---

# Despesa

Representa o título financeiro.

```
despesa
```

Campos:

```
id

origem_id

nome

status

valor_total

data_competencia

fornecedor_id

projeto_id

empresa_id
```

---

# Parcela

A unidade real de pagamento.

```
parcela_despesa
```

Campos:

```
id

despesa_id

valor

data_vencimento

data_pagamento

forma_pagamento

nota_fiscal

status
```

Essa tabela será uma das mais importantes.

Porque:

O banco não paga uma despesa.

O banco paga uma parcela.

---

# Movimentação Bancária

```
movimentacao_bancaria
```

Campos:

```
id

data_movimento

descricao_original

tipo_operacao

valor

saldo

codigo_contraparte

nome_contraparte

arquivo_origem
```

---

# Lançamento Contábil

```
lancamento_contabil
```

Campos:

```
id

chave_sci

data

historico

debito

credito

saldo

conta_contrapartida

arquivo_origem
```

---

# 10.5 Motor de Matching

Agora entra a parte mais importante do projeto.

Não vamos simplesmente comparar igualdade.

Porque na prática:

Financeiro:

```
UP ESQUADRIAS
26/06
R$ 13.500
```

Banco:

```
PIX enviado:
Cp:123456
UP ESQ
27/06
-13.500,00
```

Contabilidade:

```
Compra a Vista de Esquadrias Bioma
26/06
13.500 Crédito
```

São três representações diferentes.

Então vamos usar pontuação.

---

# Algoritmo de Score

Exemplo:

## Critério 1 - Valor

Peso:

40%

```
Valor parcela = valor banco
```

Resultado:

+40 pontos

---

## Critério 2 - Data

Peso:

20%

Mesmo dia:

+20

Diferença 1 dia:

+15

Diferença 2 dias:

+10

---

## Critério 3 - Fornecedor

Peso:

30%

Comparação:

* nome normalizado;
* similaridade;
* código Cp.

Exemplo:

```
UP ESQUADRIAS

UP ESQ
```

similaridade alta.

---

## Critério 4 - Nota Fiscal

Peso:

10%

Se existir:

```
NF 124139
```

no financeiro e razão:

```
NFE 124139
```

match perfeito.

---

Resultado:

```
Score >=90

MATCH AUTOMÁTICO


70-89

REVISÃO HUMANA


<70

DIVERGÊNCIA
```

---

# 10.6 Resultado esperado do sistema

Ao final:

## Aba: Conciliados

Exemplo:

| Fornecedor    | Valor  | Banco | Razão | Status     |
| ------------- | ------ | ----- | ----- | ---------- |
| UP Esquadrias | 13.500 | OK    | OK    | Conciliado |

---

## Aba: Pendências

Exemplo:

| Tipo              | Descrição                    |
| ----------------- | ---------------------------- |
| Banco sem despesa | PIX 5.000                    |
| Despesa sem banco | Fornecedor X                 |
| Banco sem razão   | Lançamento não contabilizado |

---

# 10.7 Arquitetura Técnica Inicial

Agora falando da sua stack.

A escolha está coerente.

Minha sugestão:

## Backend

Python:

* FastAPI
* Pandas
* Openpyxl
* Pydantic
* SQLAlchemy
* Alembic

Responsável:

* upload;
* processamento;
* parser;
* motor de conciliação.

---

## Frontend

React + TypeScript:

Responsável:

* dashboard;
* upload;
* acompanhamento;
* aprovação manual dos matches.

---

## Banco

Desenvolvimento:

SQLite

Produção:

PostgreSQL

Correto.

Porém:

Eu faria desde o início pensando em PostgreSQL.

SQLite somente para protótipo local.

---

## Infraestrutura

Docker:

```
frontend container

backend container

database container
```

CI/CD:

GitHub Actions:

Pipeline:

```
git push

↓

testes

↓

build docker

↓

deploy Railway

↓

migração banco

↓

produção
```

---

# Minha validação como Tech Lead

A estratégia é tecnicamente viável.

O projeto não deve ser apresentado como "importador de planilhas".

A proposta de valor é:

> "Uma plataforma de integração e conciliação financeira-contábil capaz de receber dados de diferentes ERPs utilizados por construtoras, padronizar essas informações em um modelo único e realizar automaticamente validações entre financeiro, banco e contabilidade."

Esse posicionamento muda completamente a negociação.

Você não está criando uma automação pontual.

Você está criando um **middleware contábil-financeiro para múltiplos ERPs**.

---

Próxima etapa que eu sugiro construirmos:

**11. Documento UML Inicial**

Com:

1. Diagrama de Caso de Uso
2. Diagrama de Componentes
3. Diagrama de Sequência da Importação
4. Diagrama de Sequência da Conciliação
5. Modelo Entidade Relacionamento inicial

Depois disso entramos na criação do protótipo com a sua stack.
