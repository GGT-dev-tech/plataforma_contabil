Perfeito. Vou continuar a partir daqui seguindo a visão de **Tech Lead + Analista de Sistemas + Especialista em processos contábeis/financeiros**.

Como já temos a documentação das três fontes:

1. **Despesas 06-2026.xlsx** → visão financeira/gerencial (contas a pagar)
2. **Extrato-01-06-2026-a-30-06-2026-PDF.xlsx** → visão bancária (caixa realizado)
3. **Razão SUCESSOR.xlsx** → visão contábil oficial (SCI)

Agora o próximo passo correto não é começar a codificar. Primeiro precisamos consolidar a **arquitetura funcional do protótipo** e o **modelo UML inicial**, porque isso vai definir como o software será construído.

Vou iniciar pela primeira etapa:

# ETAPA 1 — Definição do Objetivo do Sistema

## Nome provisório do projeto

**Sistema Automatizado de Conciliação Financeira e Contábil Multissistema**

ou

**SACF — Sistema de Automação de Conciliação Financeira**

---

# 1. Visão Geral do Projeto

## Problema atual

A contabilidade recebe informações originadas de diferentes sistemas utilizados pelas construtoras e SPEs.

Cada empresa possui seu próprio ERP financeiro/administrativo, gerando arquivos com estruturas diferentes.

Atualmente o processo depende de:

* exportação manual de planilhas;
* tratamento manual dos dados;
* conferência humana;
* comparação entre financeiro, banco e contabilidade;
* identificação manual das divergências.

Esse processo apresenta:

* alto consumo de horas;
* risco de erro humano;
* dificuldade de auditoria;
* baixa escalabilidade para novos clientes.

---

# 2. Solução Proposta

Construir uma plataforma intermediária capaz de:

## Receber dados de múltiplas origens

Exemplos:

* ERP da construtora;
* sistema financeiro;
* sistema contábil SCI;
* bancos;
* arquivos Excel;
* arquivos PDF convertidos.

---

## Realizar uma camada de normalização

Cada sistema possui seu próprio formato.

Exemplo:

ERP A:

```
Fornecedor
Data Pgto
Valor
Projeto
```

ERP B:

```
Favorecido
Liquidação
Valor Baixa
Obra
```

ERP C:

```
Cliente
Título
Pagamento
Centro Custo
```

O sistema não deve depender do formato original.

Ele deve converter tudo para um modelo interno:

```
Fornecedor
Data
Valor
Projeto
Documento
Conta
Natureza
Origem
```

---

# 3. Arquitetura Conceitual

A arquitetura inicial:

```
                 FONTES DE DADOS

        ERP Construtora A
                |
        ERP Construtora B
                |
        SCI Contábil
                |
        Banco / Extrato
                |
        Excel / PDF


                 ↓


        CAMADA DE INGESTÃO

        Importadores
        Parsers
        Validadores


                 ↓


        MODELO CANÔNICO

        Banco de Dados


                 ↓


        MOTOR DE CONCILIAÇÃO


                 ↓


        RELATÓRIOS

        - Conciliados
        - Divergências
        - Auditoria
        - Indicadores

```

---

# 4. Decisão Técnica Importante

Aqui está um ponto estratégico para negociação com seu cliente:

A solução não deve competir com a SCI.

Ela deve ser apresentada como uma **camada de integração e inteligência acima dos sistemas existentes**.

Porque o problema dele não é "falta de sistema contábil".

O problema é:

> "Tenho vários clientes usando sistemas diferentes e preciso transformar informações heterogêneas em um padrão único para minha operação contábil."

Então o produto é um:

## Middleware Contábil / Financeiro

---

# 5. Modelo de Dados Canônico Inicial

Esse é o coração do projeto.

Tudo entra diferente.

Tudo sai igual.

---

## Entidade Empresa

Representa a construtora/SPE.

```
Empresa

id
razao_social
cnpj
sistema_origem
ativo
```

---

## Entidade Projeto / Obra

Muito importante para construção civil.

```
Projeto

id
codigo
nome
cliente
empresa_id
```

Exemplo:

```
PROJ02
Casa Bioma
```

---

## Entidade Fornecedor

```
Fornecedor

id
nome_original
nome_normalizado
documento
tipo_pessoa
```

---

## Entidade Despesa

Representa o compromisso financeiro.

```
Despesa

id_origem
fornecedor_id
projeto_id
categoria
valor
data_competencia
status
origem
```

---

## Entidade Pagamento

Representa o caixa.

```
Pagamento

id

despesa_id

data_pagamento

valor

forma_pagamento

conta_bancaria
```

---

## Entidade Movimento Bancário

Vem do extrato.

```
MovimentoBanco

id

data

historico

valor

tipo_operacao

contraparte

arquivo_origem
```

---

## Entidade Lançamento Contábil

Vem do SCI.

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

# 6. Motor de Conciliação

A inteligência principal.

Ele fará:

## Regra 1 — Valor

Exemplo:

Despesa:

```
UP ESQUADRIAS
R$ 33.500,00
```

Banco:

```
PIX enviado UP ESQUADRIAS
-R$ 33.500,00
```

Match:

100%

---

## Regra 2 — Data

Aceita:

```
Pagamento:
10/06

Banco:
11/06
```

Porque pode existir compensação.

---

## Regra 3 — Nome

Aplicar normalização:

Antes:

```
UP ESQUADRIAS LTDA
```

Banco:

```
UP ESQUADRIAS
```

Resultado:

Match provável.

---

## Regra 4 — Documento fiscal

Se existir:

```
NF 124139
```

vira uma chave forte.

---

# 7. Score de Conciliação

Eu recomendo não trabalhar somente com "bate/não bate".

Criar pontuação:

Exemplo:

| Critério    | Peso |
| ----------- | ---: |
| Valor       |  40% |
| Data        |  20% |
| Fornecedor  |  25% |
| Nota Fiscal |  15% |

Resultado:

```
95% = Conciliado automaticamente

70-94% = Revisão humana

<70% = Divergência
```

---

# 8. Stack Técnica Avaliada

Sobre sua escolha:

## Backend

Python:

✅ Excelente escolha.

Motivos:

* pandas;
* openpyxl;
* numpy;
* bibliotecas financeiras;
* processamento de arquivos.

Sugestão:

FastAPI

```
Python
FastAPI
SQLAlchemy
Pandas
Pydantic
```

---

## Frontend

React:

✅ Correto.

Sugestão:

```
React
TypeScript
Tailwind
Shadcn UI
```

---

## Banco

SQLite local:

Para protótipo:

✅ Sim.

Produção:

PostgreSQL:

✅ Correto.

---

## Container

Docker:

✅ Obrigatório.

Estrutura:

```
docker-compose

frontend
backend
database
worker
```

---

## Deploy

Railway:

Para MVP:

✅ Adequado.

Posteriormente:

AWS / Azure / GCP.

---

## CI/CD

GitHub Actions:

✅ Correto.

Pipeline:

```
Commit

↓

Testes

↓

Build Docker

↓

Deploy Railway

↓

Migração Banco

```

---

# 9. Próximo documento que devemos criar

Agora que temos o entendimento completo, o próximo artefato técnico deve ser:

# Documento UML — Versão 1

Com:

## 1. Diagrama de Caso de Uso

Atores:

* Analista Contábil
* Administrador
* Sistema ERP
* Banco
* SCI

Casos:

* Importar arquivo
* Validar estrutura
* Normalizar dados
* Executar conciliação
* Analisar divergências
* Exportar relatório

---

## 2. Diagrama de Componentes

Componentes:

```
Frontend React

        |

API FastAPI

        |

Serviço de Importação

        |

Motor de Conciliação

        |

PostgreSQL

```

---

## 3. Diagrama de Sequência

Fluxo:

Usuário envia Excel

↓

Sistema identifica arquivo

↓

Parser executa leitura

↓

Dados vão para staging

↓

Normalização

↓

Matching

↓

Relatório

---

Minha recomendação como Tech Lead:

Antes de criar código, vamos fechar esses três documentos:

1. **UML da solução**
2. **Modelo Entidade Relacionamento**
3. **Documento de Arquitetura**

Depois disso começamos o desenvolvimento do protótipo.

Pode seguir enviando os próximos detalhes ou podemos iniciar o **Documento UML completo do projeto**.
