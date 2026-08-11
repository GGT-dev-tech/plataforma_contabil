Vamos continuar. Agora vamos para o próximo documento técnico.

# DOCUMENTO UML 03

# DIAGRAMAS DE SEQUÊNCIA DO SISTEMA

Neste momento vamos sair da visão **estrutural** (entidades e tabelas) e definir o **comportamento do sistema**.

A pergunta que esse documento responde é:

> "Quando um arquivo entra no sistema, quais componentes são acionados, em qual ordem, e como a informação chega até a conciliação?"

Esse documento será extremamente importante para a implementação usando:

* Python + FastAPI
* React + TypeScript
* PostgreSQL
* Docker
* Railway
* GitHub Actions

---

# 1. Arquitetura dos Componentes Envolvidos

Antes dos diagramas, vamos definir os participantes.

```text
                    USUÁRIO
                       |
                       |
                 Frontend React
                       |
                       |
                  API FastAPI
                       |
        --------------------------------
        |              |               |
        |              |               |
 Import Service   Validation     Database
        |
        |
 Parser Engine
        |
        |
 Normalizer
        |
        |
 Canonical Model
        |
        |
 Reconciliation Engine
        |
        |
 Report Generator

```

---

# DIAGRAMA DE SEQUÊNCIA 01

# Importação de Arquivo Financeiro (ERP / Excel)

## Objetivo

Processar arquivos enviados pela construtora ou cliente contábil.

Exemplo:

`Despesas 06-2026.xlsx`

---

## Fluxo

```text
Usuário
  |
  |
  | Upload arquivo
  |
  v
Frontend React
  |
  |
  | POST /upload
  |
  v
API FastAPI
  |
  |
  | valida usuário
  |
  v
Import Service
  |
  |
  | salva arquivo bruto
  |
  v
Storage
  |
  |
  | envia processamento
  |
  v
Parser Engine
  |
  |
  | identifica layout
  |
  v
Normalizer
  |
  |
  | transforma dados
  |
  v
PostgreSQL
  |
  |
  | retorna sucesso
  |
  v
Frontend

```

---

# Detalhamento Técnico

## Etapa 1 — Upload

Endpoint:

```
POST /api/import/upload
```

Recebe:

```json
{
 "empresa_id": "uuid",
 "arquivo": "Despesas.xlsx",
 "tipo": "financeiro"
}
```

---

## Etapa 2 — Validação

Sistema verifica:

* extensão;
* tamanho;
* hash duplicado;
* empresa vinculada.

---

Exemplo:

Arquivo:

```
Despesas 06-2026.xlsx
```

Hash:

```
a8938ab72f...
```

Caso já exista:

```
Arquivo já processado.
```

---

# Etapa 3 — Identificação do Layout

Aqui está um diferencial do produto.

O sistema não deve perguntar sempre:

"Esse arquivo é de qual sistema?"

Ele pode sugerir.

Exemplo:

Analisa colunas:

Encontrou:

```
Fornecedor
Valor parcela
Data pagamento parcela
Projeto
```

Resultado:

```
Possível origem:
Sistema Financeiro ERP

Confiança:
96%
```

---

# DIAGRAMA DE SEQUÊNCIA 02

# Processamento do Extrato Bancário

Arquivo:

```
Extrato-01-06-2026-a-30-06-2026-PDF.xlsx
```

---

Esse é o cenário mais complexo.

Porque não é uma tabela.

É um relatório.

---

Fluxo:

```text

Arquivo Excel/PDF

        |
        |
        v

Parser Bancário

        |
        |
        v

Identifica Cabeçalho

        |
        |
        v

Encontra Data do Dia

        |
        |
        v

Propaga Data

        |
        |
        v

Extrai Movimento

        |
        |
        v

Converte Valores

        |
        |
        v

Normaliza Histórico

        |
        |
        v

Salva Movimento Bancário


```

---

# Exemplo do Parser

Entrada:

```
2 de Junho de 2026
Saldo do dia R$ 50.000

Pix enviado:
Cp:60701190
UP ESQUADRIAS

-R$ 33.500

```

---

Processamento:

Sistema cria:

```json
{
 "data":
 "2026-06-02",

 "tipo":
 "PIX_ENVIADO",

 "contraparte":
 "UP ESQUADRIAS",

 "valor":
 -33500
}

```

---

# DIAGRAMA DE SEQUÊNCIA 03

# Processamento do Razão SCI

Arquivo:

```
Razão SUCESSOR.xlsx
```

---

Esse possui uma característica:

Ele é um relatório de impressão.

Então:

não devemos ler por posição fixa.

Devemos interpretar conteúdo.

---

Fluxo:

```text

Arquivo SCI

     |
     |
     v

SCI Parser

     |
     |
     v

Identifica Conta Contábil

     |
     |
     v

Localiza Datas

     |
     |
     v

Extrai Lançamentos

     |
     |
     v

Converte Débito/Crédito

     |
     |
     v

Preserva Chave SCI

     |
     |
     v

Salva Lançamento Contábil


```

---

Exemplo:

Entrada:

```
Chave: 40070

Histórico:
Pix enviado UP ESQUADRIAS

Crédito:
33.500,00

Saldo:
50.000D

```

Saída:

```json
{
"chave_origem":"40070",

"historico":
"Pix enviado UP ESQUADRIAS",

"credito":
33500,

"saldo":
50000

}

```

---

# DIAGRAMA DE SEQUÊNCIA 04

# Motor de Conciliação Tripla

Esse é o núcleo da solução.

---

Participantes:

```
Despesa

Movimento Bancário

Lançamento Contábil

Motor Matching

Score Engine

Banco

```

---

Fluxo:

```text

Motor Conciliação

        |
        |
Busca despesas pagas

        |
        |
Busca movimentos banco

        |
        |
Busca lançamentos contábeis

        |
        |
Executa regras

        |
        |
Calcula Score

        |
        |
Classifica resultado

        |
        |
Salva conciliação


```

---

# Regras do Motor

## Regra 01 — Valor

Peso:

40%

Exemplo:

Financeiro:

```
-33.500,00
```

Banco:

```
-33.500,00
```

Resultado:

```
MATCH
```

---

## Regra 02 — Data

Peso:

20%

Aceita:

```
Pagamento:
30/06

Banco:
01/07

```

Status:

```
Possível compensação
```

---

## Regra 03 — Fornecedor

Peso:

25%

Aplicação:

Normalização:

Antes:

```
UP ESQUADRIAS LTDA
```

Depois:

```
UP ESQUADRIAS

```

Comparação:

similaridade.

---

## Regra 04 — Documento Fiscal

Peso:

15%

Exemplo:

Financeiro:

```
NF 124139
```

Razão:

```
NFE 124139

```

---

# Resultado do Motor

Exemplo:

```json
{
"despesa":
"UP ESQUADRIAS",

"banco":
"PIX enviado UP ESQUADRIAS",

"razao":
"Compra Esquadrias",

"score":
98,

"status":
"CONCILIADO"

}

```

---

# DIAGRAMA DE SEQUÊNCIA 05

# Geração do Relatório Final

Após processamento:

```text

Usuário

 |
 |
Solicita relatório

 |
 |
API

 |
 |
Report Service

 |
 |
Consulta conciliações

 |
 |
Monta relatório

 |
 |
Gera Excel/PDF

 |
 |
Disponibiliza download


```

---

# Estrutura do Relatório

## Aba 1 — Resumo

```
Total despesas:
R$ XXX

Total banco:
R$ XXX

Total contábil:
R$ XXX

Percentual conciliado:
XX%

```

---

## Aba 2 — Conciliados

Campos:

```
Fornecedor

Valor

Data

Projeto

Banco

Razão

Score

```

---

## Aba 3 — Pendências

Exemplo:

```
Pagamento no banco sem despesa

Despesa sem pagamento

Banco sem contabilização

```

---

# Consideração de Arquitetura

Com esses diagramas, temos uma decisão clara:

O sistema deve ser desenvolvido como uma arquitetura baseada em serviços.

Minha sugestão inicial para o MVP:

```
backend
|
|-- api
|
|-- importers
|      |
|      |-- despesas_parser.py
|      |-- extrato_parser.py
|      |-- razao_parser.py
|
|-- normalization
|
|-- reconciliation
|
|-- reports
|
|-- database

```

---

# Próximo documento

Agora temos:

✅ Visão geral
✅ Casos de uso
✅ Modelo de dados
✅ Sequências de processamento

O próximo documento será:

# DOCUMENTO UML 04 — DIAGRAMA DE CLASSES + ARQUITETURA DE SOFTWARE

Nele vamos transformar as entidades em objetos Python:

Exemplo:

```python
class MovimentoBancario:
    data
    valor
    historico
    contraparte
```

e definir a estrutura real do backend.

Depois disso já estaremos praticamente na fase de criação do repositório e início do MVP.
