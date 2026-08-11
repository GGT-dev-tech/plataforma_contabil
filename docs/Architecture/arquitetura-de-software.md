Perfeito. Vamos avançar para o próximo documento. A partir daqui entramos numa etapa que eu considero crítica: **transformar a ideia em uma arquitetura que um time de desenvolvimento conseguiria executar com segurança**.

Vou estruturar como um documento técnico oficial.

---

# 12. DOCUMENTO DE ARQUITETURA DE SOFTWARE

## 12.1 Identificação do Projeto

**Nome provisório:**

Sistema Inteligente de Conciliação Financeira e Contábil para Empresas do Segmento de Construção Civil

**Objetivo:**

Construir uma plataforma capaz de importar dados financeiros, bancários e contábeis provenientes de diferentes sistemas, realizar padronização dos dados e executar uma conciliação automática de três fontes:

* Financeiro/ERP da construtora;
* Extrato bancário;
* Sistema contábil.

---

# 12.2 Princípios Arquiteturais

A arquitetura será baseada nos seguintes princípios:

## 1. Independência do sistema de origem

O sistema não deve depender de um ERP específico.

Exemplo:

Hoje:

```
Sistema Financeiro Cliente A
        |
        ↓
Conciliação
        |
        ↓
SCI
```

Amanhã:

```
Sienge
Mega
TOTVS
Sistema próprio

        |
        ↓

Modelo Canônico

        |
        ↓

Motor de Conciliação
```

---

## 2. Separação entre dados brutos e dados tratados

O sistema deve preservar a informação original.

Fluxo:

```
Arquivo Original
       |
       ↓
STAGING
       |
       ↓
NORMALIZAÇÃO
       |
       ↓
MODELO CANÔNICO
       |
       ↓
PROCESSAMENTO
```

Motivo:

* auditoria;
* rastreabilidade;
* reprocessamento;
* conformidade contábil.

---

## 3. Arquitetura orientada a serviços

Mesmo inicialmente sendo uma aplicação única, a estrutura deve permitir evolução futura.

Modelo:

```
Frontend
   |
API
   |
Serviços internos

- Importação
- Normalização
- Matching
- Relatórios
```

---

# 12.3 Arquitetura Geral da Solução

```
                 USUÁRIO
                    |
                    |
             React + TypeScript
                    |
                    |
             API Gateway
                    |
             FastAPI Backend
                    |
 ------------------------------------------------
 |                    |                         |
 |                    |                         |
Import Service   Matching Engine        Report Service
 |                    |                         |
 |                    |                         |
 ------------------------------------------------
                    |
             PostgreSQL Database
                    |
        ----------------------------
        |                          |
     STAGING                  CANONICAL
```

---

# 12.4 Stack Tecnológica Proposta

## Frontend

### React + TypeScript

Responsabilidade:

* interface;
* dashboards;
* acompanhamento dos processos;
* revisão manual de divergências.

Bibliotecas recomendadas:

### React Router

Controle de navegação.

### TanStack Query

Gerenciamento de comunicação API.

### React Hook Form

Formulários.

### Zod

Validação de dados.

### Tailwind CSS

Padronização visual.

---

# Backend

## Python + FastAPI

Escolha adequada para esse projeto porque:

* excelente manipulação de dados;
* ecossistema financeiro;
* processamento de Excel;
* inteligência artificial futura;
* APIs rápidas.

Bibliotecas:

## Pandas

Responsável por:

* leitura;
* transformação;
* limpeza;
* análise.

---

## Openpyxl

Responsável por:

* leitura avançada Excel;
* tratamento de planilhas complexas.

---

## Pydantic

Responsável por:

* validação dos modelos;
* contratos da API.

---

## SQLAlchemy

ORM do banco.

---

## Alembic

Controle de versões do banco.

---

# Banco de Dados

## PostgreSQL

Escolha recomendada para produção.

Motivos:

* robustez;
* transações;
* relacionamentos complexos;
* auditoria;
* crescimento futuro.

---

Estrutura:

```
PostgreSQL

schemas:

├── staging
│
├── core
│
├── reconciliation
│
└── audit
```

---

# 12.5 Organização do Banco de Dados

## Schema staging

Mantém dados importados.

Exemplo:

```
stg_despesas_raw

stg_extrato_raw

stg_razao_raw
```

Aqui nada é alterado.

---

## Schema core

Modelo limpo.

Exemplo:

```
empresa

projeto

fornecedor

despesa

parcela

movimento_bancario

lancamento_contabil
```

---

## Schema reconciliation

Resultado da inteligência:

```
conciliacao

match_rule

match_score

divergencia
```

---

## Schema audit

Controle:

```
arquivo_importado

processamento

usuario

log_execucao
```

---

# 12.6 Estrutura do Projeto Backend

Sugestão:

```
backend/

├── app/

│
├── api/

│   ├── routes/

│   └── controllers/

│
├── domain/

│   ├── entities/

│   └── services/

│
├── infrastructure/

│   ├── database/

│   ├── repositories/

│   └── storage/

│
├── processors/

│   ├── expense_parser/

│   ├── bank_parser/

│   └── accounting_parser/

│
├── reconciliation/

│   ├── matcher.py

│   ├── scoring.py

│   └── rules.py

│
├── tests/

│
└── main.py
```

---

# 12.7 Arquitetura de Processamento dos Arquivos

## Exemplo: Extrato Bancário

Entrada:

```
Extrato-01-06-2026-a-30-06-2026-PDF.xlsx
```

Processamento:

```
Upload

 ↓

Identificação do banco

 ↓

Parser Banco Inter

 ↓

Extração:

Data

Histórico

Valor

Saldo

Contraparte


 ↓

Validação

 ↓

Modelo Canônico

 ↓

Banco
```

---

# 12.8 Estratégia de Parser Multi ERP

Esse ponto é fundamental para sua negociação.

Nós não vamos criar "um importador de Excel".

Vamos criar adaptadores.

Arquitetura:

```
              Modelo Canônico


                    ↑


 --------------------------------

 |              |               |

Adapter ERP A Adapter ERP B Adapter SCI


 --------------------------------


```

Exemplo:

Hoje:

```
SCIAdapter
BancoInterAdapter
FinanceiroClienteAdapter
```

Futuro:

```
SiengeAdapter
MegaAdapter
TotvsAdapter
```

---

# 12.9 Motor de Conciliação

Será dividido em camadas:

## Regra determinística

Primeiro tenta:

```
valor igual

+

data igual

+

fornecedor igual
```

---

## Regra aproximada

Caso não encontre:

```
similaridade texto

+

diferença data

+

valor próximo
```

---

## Score final

Modelo:

```
Score =
(valor * 40)
+
(data * 20)
+
(fornecedor * 30)
+
(nota fiscal * 10)
```

---

# 12.10 Segurança da Aplicação

Mesmo sendo um sistema interno, devemos prever:

## Controle de acesso

Perfis:

```
Administrador

Contador

Financeiro

Auditor
```

---

## Auditoria

Toda ação gera registro:

Exemplo:

```
Usuário João

Importou:

Despesas_06_2026.xlsx

Data:

30/07/2026

Resultado:

174 registros processados
```

---

## Proteção dos arquivos

Arquivos enviados:

* não ficam expostos;
* recebem identificação;
* possuem hash;
* podem ser recuperados.

---

# 12.11 Containerização

Docker:

Estrutura:

```
docker-compose.yml


services:


frontend

backend

postgres

redis (futuro)
```

---

# 12.12 CI/CD

GitHub Actions:

Fluxo:

```
Developer

   |

git push

   |

GitHub Actions

   |

Executa testes

   |

Build Docker

   |

Deploy Railway

   |

Produção
```

---

# 12.13 Deploy Inicial

Ambiente:

## Railway

Serviços:

```
Frontend Container

Backend Container

PostgreSQL Database
```

Configurações:

```
ENVIRONMENT

DATABASE_URL

SECRET_KEY

STORAGE_PATH

API_KEYS
```

---

# 12.14 Decisão Técnica Sobre SQLite

Minha recomendação como Tech Lead:

Para protótipo:

✅ SQLite permitido

Para produção:

❌ Não recomendado

Motivo:

O sistema terá:

* múltiplos usuários;
* histórico;
* processos concorrentes;
* arquivos grandes;
* auditoria.

Então:

```
Desenvolvimento local:

SQLite


Homologação:

PostgreSQL


Produção:

PostgreSQL Railway
```

---

# 12.15 Próxima Etapa do Projeto

Agora a documentação técnica está chegando no ponto de desenvolvimento.

O próximo documento deve ser:

# 13. Documento de Requisitos Funcionais (RF)

Ele vai definir exatamente:

* o que o sistema deve fazer;
* telas necessárias;
* comportamento esperado;
* regras de negócio;
* validações;
* permissões.

Depois dele:

# 14. Documento de Requisitos Não Funcionais (RNF)

Definindo:

* desempenho;
* segurança;
* disponibilidade;
* escalabilidade;
* logs;
* backups.

Depois desses dois documentos, teremos base suficiente para começar a criar o protótipo na sua stack.
