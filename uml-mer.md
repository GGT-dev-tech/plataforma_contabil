Vamos continuar. Agora entramos em uma das partes mais importantes do projeto: o **Modelo Entidade-Relacionamento (MER) do Sistema de Conciliação Financeira e Contábil**.

Esse documento é o que vai orientar a criação do banco PostgreSQL, as entidades da aplicação Python, as APIs e posteriormente os componentes React.

A decisão arquitetural principal aqui é:

> Não criar um banco baseado nas planilhas atuais.
> Criar um modelo baseado no negócio, onde qualquer ERP futuro consiga se encaixar.

Ou seja, as planilhas são apenas **fontes de entrada**.

---

# DOCUMENTO UML 02

# MODELO ENTIDADE-RELACIONAMENTO (MER)

## 1. Objetivo do Modelo

Representar as entidades necessárias para suportar:

* múltiplas empresas;
* múltiplos clientes contábeis;
* múltiplos ERPs;
* diferentes layouts de arquivos;
* conciliação financeira;
* conciliação contábil;
* auditoria;
* rastreabilidade.

---

# 2. Visão Geral das Entidades

O modelo será dividido em 5 grandes domínios:

```
                CADASTRO
                   |
                   |
        Empresa / Cliente / Usuário


                   |

             ORIGEM DOS DADOS

        Arquivo
        Sistema Origem
        Importação


                   |

              DADOS FINANCEIROS

        Despesa
        Pagamento
        Movimento Bancário


                   |

              DADOS CONTÁBEIS

        Conta Contábil
        Lançamento Contábil


                   |

              INTELIGÊNCIA

        Conciliação
        Match
        Divergência

```

---

# 3. Entidades Principais

---

# ENTIDADE: Empresa

Representa a construtora, SPE ou cliente da contabilidade.

Exemplo:

* VNP Empreendimentos
* Outra construtora futura

---

Tabela:

```sql
empresa
```

Campos:

| Campo         | Tipo      |
| ------------- | --------- |
| id            | UUID      |
| razao_social  | varchar   |
| nome_fantasia | varchar   |
| cnpj          | varchar   |
| ativo         | boolean   |
| created_at    | timestamp |

---

Relacionamentos:

```
Empresa

1:N

Projetos

1:N

Arquivos Importados

1:N

Despesas

```

---

# ENTIDADE: Sistema Origem

Muito importante para o objetivo do cliente.

Porque cada construtora terá seu ERP.

Exemplos:

* SCI
* ERP próprio
* Sistema financeiro X
* Excel manual

---

Tabela:

```sql
sistema_origem
```

Campos:

| Campo  | Tipo    |
| ------ | ------- |
| id     | UUID    |
| nome   | varchar |
| tipo   | varchar |
| versao | varchar |

---

Exemplo:

```
SCI VISUAL
ERP CONSTRUTORA A
PLANILHA MANUAL
```

---

# ENTIDADE: Arquivo Importado

Representa qualquer arquivo recebido.

---

Tabela:

```sql
arquivo_importacao
```

Campos:

| Campo                | Tipo      |
| -------------------- | --------- |
| id                   | UUID      |
| nome_original        | varchar   |
| tipo_arquivo         | varchar   |
| hash_arquivo         | varchar   |
| data_upload          | timestamp |
| status_processamento | varchar   |
| sistema_origem_id    | UUID      |

---

Status:

```
RECEBIDO

PROCESSANDO

PROCESSADO

ERRO

```

---

Relacionamento:

```
Sistema Origem

1:N

Arquivo Importação

```

---

# ENTIDADE: Layout de Importação

Aqui está uma decisão estratégica.

Como cada ERP é diferente, precisamos guardar o "mapa".

Exemplo:

ERP A:

```
Fornecedor
Valor
Data
```

ERP B:

```
Favorecido
Valor Parcela
Pagamento
```

Ambos viram:

```
Fornecedor
Valor
Data Pagamento

```

---

Tabela:

```sql
layout_importacao
```

Campos:

| Campo             | Tipo    |
| ----------------- | ------- |
| id                | UUID    |
| nome_layout       | varchar |
| tipo_documento    | varchar |
| configuracao_json | jsonb   |

---

Exemplo:

```json
{
 "fornecedor":"coluna_G",
 "valor":"coluna_O",
 "data":"coluna_Q"
}

```

---

# DOMÍNIO FINANCEIRO

---

# ENTIDADE: Fornecedor

Base para matching.

---

Tabela:

```sql
fornecedor
```

Campos:

| Campo            | Tipo    |
| ---------------- | ------- |
| id               | UUID    |
| nome_original    | varchar |
| nome_normalizado | varchar |
| documento        | varchar |
| tipo_pessoa      | varchar |

---

Exemplo:

Original:

```
UP ESQUADRIAS LTDA
```

Normalizado:

```
UP ESQUADRIAS

```

---

# ENTIDADE: Projeto / Obra

Muito relevante para construção civil.

---

Tabela:

```sql
projeto
```

Campos:

| Campo      | Tipo    |
| ---------- | ------- |
| id         | UUID    |
| codigo     | varchar |
| nome       | varchar |
| empresa_id | UUID    |

---

Exemplo:

```
PROJ02

Casa Bioma

```

---

Relacionamento:

```
Empresa

1:N

Projeto

```

---

# ENTIDADE: Despesa

Representa a obrigação financeira.

---

Tabela:

```sql
despesa
```

Campos:

| Campo            | Tipo    |
| ---------------- | ------- |
| id               | UUID    |
| id_origem        | varchar |
| fornecedor_id    | UUID    |
| projeto_id       | UUID    |
| valor_total      | decimal |
| data_competencia | date    |
| status           | varchar |
| origem_sistema   | varchar |

---

Exemplo:

```
Fornecedor:
BH Materiais

Projeto:
Casa Bioma

Valor:
R$ 15.000,00

```

---

Relacionamento:

```
Despesa

1:N

Parcela

```

---

# ENTIDADE: Parcela Despesa

Essa é a entidade mais importante para conciliação.

Porque pagamento acontece na parcela.

---

Tabela:

```sql
parcela_despesa
```

Campos:

| Campo           | Tipo    |
| --------------- | ------- |
| id              | UUID    |
| despesa_id      | UUID    |
| valor           | decimal |
| data_vencimento | date    |
| data_pagamento  | date    |
| forma_pagamento | varchar |
| nota_fiscal     | varchar |

---

Relacionamento:

```
Despesa

1:N

Parcela

```

---

# DOMÍNIO BANCÁRIO

---

# ENTIDADE: Conta Bancária

Representa contas reais.

---

Tabela:

```sql
conta_bancaria
```

Campos:

| Campo        | Tipo    |
| ------------ | ------- |
| id           | UUID    |
| banco        | varchar |
| agencia      | varchar |
| numero_conta | varchar |
| empresa_id   | UUID    |

---

# ENTIDADE: Movimento Bancário

Vem do extrato.

---

Tabela:

```sql
movimento_bancario
```

Campos:

| Campo             | Tipo    |
| ----------------- | ------- |
| id                | UUID    |
| conta_bancaria_id | UUID    |
| data_movimento    | date    |
| historico         | text    |
| valor             | decimal |
| tipo_operacao     | varchar |
| contraparte       | varchar |
| arquivo_origem_id | UUID    |

---

Exemplo:

```
PIX enviado UP ESQUADRIAS

R$ -33.500,00

30/06/2026

```

---

# DOMÍNIO CONTÁBIL

---

# ENTIDADE: Conta Contábil

---

Tabela:

```sql
conta_contabil
```

Campos:

| Campo     | Tipo    |
| --------- | ------- |
| codigo    | varchar |
| descricao | varchar |
| natureza  | varchar |

---

Exemplo:

```
01.1.1.02.004

Banco Inter

Ativo

```

---

# ENTIDADE: Lançamento Contábil

Vem do SCI.

---

Tabela:

```sql
lancamento_contabil
```

Campos:

| Campo             | Tipo    |
| ----------------- | ------- |
| id                | UUID    |
| chave_origem      | varchar |
| data_lancamento   | date    |
| historico         | text    |
| debito            | decimal |
| credito           | decimal |
| saldo             | decimal |
| conta_contabil_id | UUID    |

---

# DOMÍNIO DE INTELIGÊNCIA

Agora entra a parte que transforma isso em produto.

---

# ENTIDADE: Conciliação

Representa uma execução.

---

Tabela:

```sql
conciliacao
```

Campos:

| Campo          | Tipo      |
| -------------- | --------- |
| id             | UUID      |
| empresa_id     | UUID      |
| periodo_inicio | date      |
| periodo_fim    | date      |
| status         | varchar   |
| data_execucao  | timestamp |

---

Exemplo:

```
Conciliação Junho/2026

Status:
Finalizada

```

---

# ENTIDADE: Match Conciliação

Guarda o relacionamento encontrado.

---

Tabela:

```sql
conciliacao_item
```

Campos:

| Campo                  | Tipo    |
| ---------------------- | ------- |
| id                     | UUID    |
| conciliacao_id         | UUID    |
| despesa_id             | UUID    |
| movimento_bancario_id  | UUID    |
| lancamento_contabil_id | UUID    |
| score                  | decimal |
| status_match           | varchar |

---

Exemplo:

```
Despesa:
UP ESQUADRIAS

Banco:
PIX UP ESQUADRIAS

Razão:
Compra Esquadrias


Score:
98%

Status:
CONCILIADO

```

---

# ENTIDADE: Divergência

Tudo que não bate.

---

Tabela:

```sql
divergencia
```

Campos:

| Campo     | Tipo    |
| --------- | ------- |
| id        | UUID    |
| tipo      | varchar |
| descricao | text    |
| gravidade | varchar |
| status    | varchar |

---

Tipos:

```
BANCO_SEM_DESPESA

DESPESA_SEM_BANCO

BANCO_SEM_CONTABILIDADE

VALOR_DIVERGENTE

```

---

# 4. Relacionamentos Principais

Representação:

```
EMPRESA

 |
 |
 +---- PROJETO

 |
 |
 +---- DESPESA

          |
          |
          +---- PARCELA

                    |
                    |
                    +------ MOVIMENTO BANCO


MOVIMENTO BANCO

          |
          |
          +------ LANÇAMENTO CONTÁBIL



TODOS

          |
          |
          +------ CONCILIAÇÃO

```

---

# 5. Decisão Técnica Importante

Eu recomendo que o banco tenha também:

## Tabela de Auditoria

Porque estamos falando de contabilidade.

```sql
auditoria_evento
```

Campos:

```
id

usuario

acao

registro_afetado

valor_anterior

valor_novo

data

```

Exemplo:

"Usuário alterou uma regra de matching."

Isso aumenta muito a confiança do produto.

---

# Próximo documento técnico

Agora que o MER está definido, o próximo passo será:

## UML 03 — Diagramas de Sequência

Vamos criar:

1. Sequência de importação de um Excel do ERP.
2. Sequência de processamento do Extrato Bancário PDF.
3. Sequência de leitura do Razão SCI.
4. Sequência completa do motor de conciliação 3-way.

Depois disso teremos uma arquitetura pronta para iniciar o código do MVP.
