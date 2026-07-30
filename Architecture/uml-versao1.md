Continuando como **Tech Lead**, vamos agora iniciar o **Documento UML – Versão 1** baseado no entendimento completo das três fontes:

* `Despesas 06-2026.xlsx` → visão financeira/operacional
* `Extrato-01-06-2026-a-30-06-2026-PDF.xlsx` → visão bancária
* `Razão SUCESSOR.xlsx` → visão contábil

A ideia aqui é criar uma base suficientemente profissional para posteriormente virar arquitetura de software, backlog de desenvolvimento e implementação.

---

# DOCUMENTO UML - VERSÃO 1

# 1. Visão Geral do Sistema

## Nome provisório do projeto

**Sistema Automatizado de Conciliação Financeira e Contábil Multissistema**

---

## Objetivo

Criar uma plataforma capaz de:

* Receber dados de diferentes ERPs utilizados por construtoras;
* Realizar a ingestão de arquivos heterogêneos;
* Padronizar os dados em um modelo único;
* Realizar conciliação financeira, bancária e contábil;
* Identificar divergências;
* Gerar relatórios auditáveis.

---

# 2. Atores do Sistema (UML Use Case)

## Usuários Humanos

### Analista Financeiro

Responsável por:

* Importar arquivos;
* Validar processamento;
* Analisar divergências;
* Aprovar conciliações.

---

### Contador

Responsável por:

* Validar lançamentos contábeis;
* Conferir divergências;
* Realizar auditoria.

---

### Gestor da Empresa / Construtora

Responsável por:

* Acompanhar custos;
* Visualizar indicadores;
* Avaliar obras/projetos.

---

### Administrador do Sistema

Responsável por:

* Configuração;
* Cadastro de empresas;
* Regras de matching;
* Usuários.

---

# 3. Diagrama de Caso de Uso

Representação:

```
                 +----------------+
                 | Analista       |
                 | Financeiro     |
                 +-------+--------+
                         |
                         |
                         v

              +---------------------+
              |                     |
              | Sistema Conciliação |
              |                     |
              +---------------------+

              /          |          \
             /           |           \

            v            v            v

     Importar       Executar      Gerar
     Arquivos       Matching      Relatório


```

---

# 4. Casos de Uso Principais

---

# UC001 - Importar Arquivos

## Ator

Analista Financeiro

## Entrada

Arquivos:

* Excel financeiro
* Extrato bancário
* Razão contábil

## Fluxo Principal

```
Usuário
  |
  |
Upload arquivos
  |
  |
Sistema valida extensão
  |
  |
Sistema identifica origem
  |
  |
Sistema envia para pipeline
  |
  |
Dados armazenados em staging

```

## Resultado

Arquivos disponíveis para processamento.

---

# UC002 - Processar Dados

## Objetivo

Transformar dados brutos em dados estruturados.

Fluxo:

```
Arquivo bruto

      |

Parser específico

      |

Normalização

      |

Modelo Canônico

      |

Banco de Dados


```

---

Exemplo:

Entrada:

```
Pix enviado:
Cp :60701190
AUTO POSTO VILA ROMANA

-R$ 1.392,20

```

Transformação:

```json
{
 "tipo_operacao":"PIX_ENVIADO",
 "codigo_cp":"60701190",
 "contraparte":"AUTO POSTO VILA ROMANA",
 "valor":1392.20,
 "natureza":"SAIDA"
}

```

---

# UC003 - Executar Conciliação

Esse é o núcleo do sistema.

Entrada:

```
ParcelaDespesa

+

MovimentoBanco

+

LancamentoContabil

```

Processamento:

```
              MOTOR MATCHING


      Valor

        +

      Data

        +

      Fornecedor

        +

      Histórico

        +

      Nota Fiscal


              |

              v


        Score de Similaridade


              |

              v


       CONCILIADO
       DIVERGENTE
       ANALISAR

```

---

# UC004 - Gerar Relatório

Saída:

## Resumo Executivo

Exemplo:

```
Período:
Junho/2026


Despesas:
R$ 850.000,00


Banco:
R$ 850.000,00


Razão:
R$ 850.000,00


Conciliação:

98,5% automática

```

---

# 5. Diagrama de Componentes

Agora pensando em arquitetura.

```

                    FRONTEND
                      
                 React + TS

                       |
                       |
                       v


                    API

                 FastAPI


                       |
      ---------------------------------

      |              |                |

      v              v                v


  Ingestão       Motor           Relatórios

  Arquivos       Matching        Dashboard


      |              |                |

      v              v                v


  Parser        Regras          Exportação


      |
      |
      v


Banco PostgreSQL


```

---

# 6. Componentes Técnicos

## Componente 1

# File Ingestion Service

Responsabilidade:

Receber arquivos.

Aceita:

```
.xlsx

.csv

.pdf (futuro)

API ERP (futuro)

```

---

## Componente 2

# Data Parser Engine

Responsabilidade:

Interpretar formatos diferentes.

Exemplo:

SCI:

```
Razão SUCESSOR

Layout impressão

```

Banco:

```
PDF convertido Excel

```

Financeiro:

```
Tabela limpa

```

Cada fonte terá um adaptador.

Arquitetura:

```
ParserBase

     |
     |
 -----------------
 |       |        |

SCI    Banco   Financeiro

Parser Parser Parser


```

---

# 7. Diagrama de Sequência - Importação

## Cenário

Usuário envia planilhas.

```
Usuário

 |
 |
 | Upload
 |
 v

Frontend

 |
 |
 v

API

 |
 |
 v

File Service

 |
 |
 v

Parser

 |
 |
 v

Normalizer

 |
 |
 v

Database


```

---

# 8. Diagrama de Sequência - Conciliação

```

Usuário

 |
 |
Solicita conciliação

 |
 v


API

 |
 |
 v


Motor Matching


 |
 |
Busca:

Despesas

Banco

Razão


 |
 |
Calcula Score


 |
 |
Classifica


 |
 |
Salva resultado


 |
 |
Retorna relatório



```

---

# 9. Modelo Entidade Relacionamento Inicial

Agora a parte mais importante para o desenvolvimento.

```
EMPRESA

 id
 razao_social


     |
     |
     | 1:N


PROJETO

 id
 codigo
 nome


     |
     |
     | 1:N


DESPESA

 id
 fornecedor
 valor


     |
     |
     | 1:N


PARCELA_DESPESA

 id
 valor
 pagamento


```

---

Banco:

```
CONTA_BANCARIA

       |
       |
       |1:N


MOVIMENTO_BANCARIO


```

---

Contábil:

```
CONTA_CONTABIL

       |
       |
       |1:N


LANCAMENTO_CONTABIL


```

---

Conciliação:

```
                 CONCILIACAO


id

parcela_id

movimento_id

lancamento_id


score

status

motivo



```

---

# 10. Nova Entidade Importante: Auditoria

Como estamos falando de contabilidade, essa entidade é obrigatória.

Tabela:

```
AUDITORIA_EVENTO


id

usuario

acao

data_hora

arquivo_origem

registro_afetado

valor_anterior

valor_novo


```

Exemplo:

```
Usuário João

Alterou regra:

Fornecedor X

Score mínimo:

80% -> 90%

```

---

# 11. Decisão Arquitetural Importante

Eu incluiria uma camada que ainda não tínhamos citado:

## Staging Database

Por segurança:

```

ARQUIVO ORIGINAL

       |

       v


STAGING


       |

       v


MODELO CANÔNICO


       |

       v


PRODUÇÃO


```

Motivo:

Em contabilidade você nunca deve perder o dado original.

Precisamos sempre responder:

> "De onde veio esse número?"

---

# 12. Próxima etapa técnica

Agora que temos UML inicial, os próximos documentos seriam:

## Documento 2

**Modelo de Dados Canônico Completo**

Com:

* Todas as tabelas;
* Campos;
* Tipos;
* Índices;
* Relacionamentos;
* Regras.

## Documento 3

**Arquitetura de Software**

Definindo:

* Backend;
* Frontend;
* Banco;
* Docker;
* Deploy Railway;
* CI/CD.

## Documento 4

**Plano de Desenvolvimento MVP**

Com:

Sprint 1
Sprint 2
Sprint 3

Minha recomendação como Tech Lead:

Antes de codificar, vamos fechar o **Modelo de Dados Canônico**, porque ele será o coração da solução. Depois disso, o desenvolvimento fica muito mais seguro e você consegue apresentar para o cliente uma arquitetura profissional.
