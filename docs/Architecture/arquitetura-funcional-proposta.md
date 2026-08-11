Perfeito. Vou continuar a partir daqui estruturando como **Tech Lead / Analista de Sistemas Sênior**, consolidando tudo que já foi levantado. Como o material é extenso, vou seguir por blocos. O próximo passo natural é transformar a documentação das três fontes em uma **Arquitetura Funcional do Sistema + Modelo UML inicial**.

---

# 10. Arquitetura Funcional Proposta do Sistema

## 10.1 Objetivo do Sistema

Desenvolver uma plataforma de automação de conciliação financeira e contábil capaz de receber dados provenientes de diferentes sistemas utilizados por construtoras, normalizar essas informações e realizar uma conciliação de três dimensões:

```
                 SISTEMAS DAS CONSTRUTORAS
                         |
                         |
                  Arquivos / APIs / Exportações
                         |
                         v

              CAMADA DE INGESTÃO DE DADOS
                         |
                         |
                         v

              CAMADA DE PADRONIZAÇÃO
              (Modelo Canônico)
                         |
                         |
          +--------------+--------------+
          |              |              |
          v              v              v

     DESPESAS        BANCO          RAZÃO CONTÁBIL
     Financeiro      Extrato        SCI / ERP

          \              |              /
           \             |             /
            \            |            /

             MOTOR DE CONCILIAÇÃO
                    |
                    |
                    v

          RELATÓRIOS + DASHBOARD
          Divergências + Auditoria

```

---

# 10.2 Conceito Principal: Modelo Canônico

O ponto mais importante do projeto é entender que **não vamos integrar diretamente cada sistema com cada sistema**.

O problema atual:

```
Construtora A
      |
      | ERP próprio
      |
      v

Contabilidade


Construtora B
      |
      | Outro ERP
      |
      v

Contabilidade


Construtora C
      |
      | Outro sistema
      |
      v

Contabilidade

```

Isso gera uma matriz impossível de manter:

```
ERP A -> Sistema Contábil
ERP B -> Sistema Contábil
ERP C -> Sistema Contábil
ERP D -> Sistema Contábil

```

A solução profissional:

Criar um **Hub de Integração Financeira**.

Cada sistema conversa com uma camada intermediária.

Exemplo:

```
ERP Construtora A
          |
          |
          v

     ADAPTER A
          |
          |
          v

       MODELO
      CANÔNICO
          |
          |
          v

     Sistema Contábil

```

Assim:

```
ERP A
ERP B
ERP C
ERP D

   |
   |
   v

Modelo Financeiro Padronizado

   |
   |
   v

SCI / Contabilidade

```

Esse é o diferencial comercial do projeto.

---

# 11. Modelo Conceitual das Entidades

Com base nas três planilhas:

## Entidade Empresa

Representa a empresa/construtora.

```
Empresa

id
razao_social
cnpj
sistema_origem
created_at

```

Relacionamento:

```
Empresa

1:N

Projetos
Despesas
Contas Bancárias

```

---

# Entidade Projeto / Obra

Muito importante para construção civil.

```
Projeto

id

codigo_projeto

nome

descricao

empresa_id

```

Exemplo:

```
PROJ02
Casa Bioma

B01
Residência Nilson e Laura

```

Relacionamento:

```
Projeto

1:N

Despesa

```

---

# Entidade Fornecedor

Elemento crítico para matching.

```
Fornecedor

id

nome_original

nome_normalizado

cpf_cnpj

tipo_pessoa

```

Exemplo:

Entrada:

```
BH MATERIAIS DE CONSTRUCAO LTDA

```

Normalização:

```
BH MATERIAIS

```

Objetivo:

Encontrar:

Banco:

```
PIX enviado:
BH MATERIAIS

```

Despesa:

```
Fornecedor:
BH MATERIAIS DE CONSTRUCAO LTDA

```

---

# Entidade Despesa

Representa o financeiro.

```
Despesa

id_origem

nome

fornecedor_id

projeto_id

categoria_id

valor_total

data_competencia

status

```

---

# Entidade Parcela

A entidade mais importante para conciliação.

```
ParcelaDespesa

id_origem

despesa_id

valor

data_pagamento

forma_pagamento

nota_fiscal

status

```

Porque o pagamento acontece na parcela.

---

# Entidade Movimentação Bancária

Origem:

Extrato Banco Inter.

```
MovimentoBanco

id

data

historico_original

tipo_operacao

valor

saldo

contraparte

codigo_cp

```

---

# Entidade Lançamento Contábil

Origem:

SCI VISUAL.

```
LancamentoContabil

id

chave_sci

data

historico

debito

credito

contra

saldo

```

---

# 12. Motor de Conciliação (Core do Sistema)

Esse é o componente mais valioso.

Ele não deve fazer apenas:

```
valor igual = conciliado

```

Isso é frágil.

Devemos criar um sistema de pontuação.

---

## Modelo de Score

Exemplo:

Pagamento:

```
Despesa:

Fornecedor:
UP ESQUADRIAS

Valor:
-132.500,00

Data:
10/06/2026


```

Banco:

```
PIX enviado UP ESQUADRIAS

Valor:
-132.500,00

Data:
11/06/2026

```

Regras:

| Critério           | Peso |
| ------------------ | ---: |
| Valor igual        |  40% |
| Data próxima       |  20% |
| Fornecedor similar |  25% |
| Forma pagamento    |  10% |
| Conta bancária     |   5% |

Resultado:

```
Score: 95%

Status:

CONCILIADO AUTOMATICAMENTE

```

---

# 13. Classificação das Conciliações

## Tipo A

### Financeiro x Banco

Pergunta:

"O que eu planejei pagar realmente saiu?"

Exemplo:

```
Despesa:
UP ESQUADRIAS

Banco:
PIX UP ESQUADRIAS

Resultado:

OK

```

---

## Tipo B

### Banco x Contabilidade

Pergunta:

"O que saiu do banco foi contabilizado?"

Exemplo:

Banco:

```
- R$ 3.500

```

Razão:

```
Crédito Banco

R$ 3.500

```

Resultado:

OK

---

## Tipo C

### Financeiro x Contabilidade

Pergunta:

"O financeiro está refletindo a contabilidade?"

---

# 14. Arquitetura Técnica Inicial

Considerando sua stack proposta:

## Backend

Python

Sugestão:

```
FastAPI

Pandas

Pydantic

SQLAlchemy

Alembic

OpenPyXL

RapidFuzz

Pytest

```

Responsabilidades:

* Upload arquivos
* Processamento Excel
* Parsing
* Normalização
* Matching
* Relatórios

---

## Frontend

React + TypeScript

Sugestão:

```
React

TypeScript

Vite

Tailwind

Shadcn/UI

React Query

```

Telas:

### Dashboard

```
Total processado

Conciliados

Pendentes

Divergências

```

---

### Tela Importação

Usuário envia:

```
Despesas.xlsx

Extrato.xlsx

Razão.xlsx

```

Sistema:

```
Validando arquivo...

Processando...

Concluído

```

---

### Tela Divergências

Exemplo:

```
Fornecedor:
UP ESQUADRIAS

Valor:
R$ 132.500,00

Problema:

Encontrado no banco
Não encontrado no razão

```

---

# 15. Banco de Dados

Para desenvolvimento:

SQLite local:

OK.

Para produção:

PostgreSQL.

Modelo:

```
Postgres

 |
 +-- empresas

 |
 +-- projetos

 |
 +-- fornecedores

 |
 +-- despesas

 |
 +-- parcelas

 |
 +-- movimentos_bancarios

 |
 +-- lancamentos_contabeis

 |
 +-- conciliacoes

 |
 +-- auditoria

```

---

# 16. Infraestrutura

Sua proposta:

Docker ✅

Railway ✅

GitHub Actions ✅

Pipeline:

```
Código

 |
 |
GitHub

 |
 |
GitHub Actions

 |
 |
Teste automático

 |
 |
Build Docker

 |
 |
Deploy Railway

 |
 |
Produção

```

---

# 17. Primeira Versão do MVP

Eu não começaria tentando fazer tudo.

O MVP comercial seria:

## Fase 1

Importação:

✅ Despesas Excel
✅ Extrato Excel
✅ Razão Excel

## Fase 2

Parser:

✅ Banco Inter
✅ SCI Visual

## Fase 3

Motor:

✅ Matching por valor
✅ Data
✅ Fornecedor

## Fase 4

Relatório:

✅ Conciliados
✅ Pendências
✅ Divergências

## Fase 5

Dashboard.

---

# Minha validação como Tech Lead

A estratégia está tecnicamente correta.

A grande decisão arquitetural é:

**Não construir um importador para SCI.**

Construir:

> "Uma plataforma de normalização e conciliação independente de ERP."

Isso atende o problema real do cliente, porque amanhã ele pode ter 20 construtoras usando 20 ERPs diferentes.

A SCI passa a ser apenas **um dos destinos ou fontes**, não uma dependência.

---

Próximo documento que eu sugiro criar:

**Documento UML - Versão 1**

Contendo:

1. Diagrama de Caso de Uso
2. Diagrama de Componentes
3. Diagrama de Sequência da Importação
4. Diagrama de Sequência da Conciliação
5. Modelo Entidade-Relacionamento inicial

Depois disso entramos no desenvolvimento do protótipo usando sua stack.
