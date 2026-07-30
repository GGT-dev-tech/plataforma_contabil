Perfeito. Vamos continuar com a próxima etapa do projeto.

Agora vamos iniciar o **Documento UML Inicial da Solução**, porque ele será a ponte entre o entendimento do negócio e o desenvolvimento do software.

Vou estruturar como um documento técnico que depois poderá fazer parte da documentação oficial do projeto.

---

# 11. DOCUMENTAÇÃO UML INICIAL

## 11.1 Objetivo da Modelagem

A modelagem UML tem como objetivo representar:

* atores envolvidos;
* processos principais;
* componentes do sistema;
* fluxo de dados;
* responsabilidades de cada módulo;
* integração entre os arquivos de origem e o motor de conciliação.

A arquitetura proposta deve permitir evolução futura para múltiplas construtoras, múltiplos ERPs e múltiplos padrões de arquivos.

---

# 11.2 Diagrama de Caso de Uso (Use Case Diagram)

## Atores do Sistema

### 1. Analista Financeiro / Contábil

Responsável por:

* importar arquivos;
* acompanhar processamento;
* analisar divergências;
* aprovar conciliações.

---

### 2. Administrador do Sistema

Responsável por:

* configurar usuários;
* cadastrar empresas;
* parametrizar regras;
* acompanhar integrações.

---

### 3. Sistema ERP Origem

Representa:

* sistema financeiro da construtora;
* ERP próprio;
* exportações Excel;
* APIs futuras.

Exemplos:

* sistema interno da construtora;
* SCI;
* Sienge;
* Mega;
* TOTVS.

---

### 4. Banco

Representa:

* extratos bancários;
* arquivos OFX;
* CSV;
* PDF convertido;
* APIs bancárias.

---

### 5. Sistema Contábil

Representa:

* SCI VISUAL Sucessor;
* outros sistemas contábeis.

---

# Casos de Uso Principais

## UC01 - Importar Arquivo Financeiro

Ator:

Analista Financeiro

Entrada:

```text
Despesas.xlsx
```

Processo:

* validar arquivo;
* identificar colunas;
* converter dados;
* armazenar staging.

Saída:

Dados financeiros normalizados.

---

## UC02 - Importar Extrato Bancário

Entrada:

```text
Extrato.xlsx/PDF
```

Processamento:

* identificar datas;
* extrair movimentações;
* interpretar históricos;
* converter valores.

Saída:

Movimentações bancárias estruturadas.

---

## UC03 - Importar Razão Contábil

Entrada:

```text
Razão SCI.xlsx
```

Processamento:

* remover cabeçalhos;
* identificar lançamentos;
* extrair chave SCI;
* normalizar débito/crédito.

Saída:

Lançamentos contábeis.

---

## UC04 - Executar Conciliação Automática

Responsável:

Motor de Matching.

Processo:

Recebe:

```
Parcela financeira

+

Movimentação bancária

+

Lançamento contábil
```

Executa:

* comparação de valores;
* comparação de datas;
* comparação de fornecedor;
* comparação de histórico;
* cálculo de score.

Resultado:

```
Conciliado

ou

Pendência
```

---

## UC05 - Revisar Divergências

Usuário analisa:

* pagamentos sem baixa;
* lançamentos sem origem;
* diferenças de valores;
* problemas de classificação.

---

## UC06 - Gerar Relatório de Conciliação

Saída:

Excel/PDF:

```
Relatório_Conciliacao_06_2026.xlsx
```

Com abas:

```
Resumo

Itens Conciliados

Pendências

Banco sem Financeiro

Financeiro sem Banco

Banco sem Contabilidade

Contabilidade sem Banco
```

---

# 11.3 Diagrama de Componentes da Arquitetura

Visão macro:

```
                 USUÁRIO
                    |
                    |
             Interface React
                    |
                    |
              API FastAPI
                    |
     --------------------------------
     |              |               |
     |              |               |
 Import Engine  Matching Engine  Reports
     |              |               |
     |              |               |
     --------------------------------
                    |
             Modelo Canônico
                    |
             PostgreSQL
                    |
        ----------------------
        |                    |
     Staging             Dados Finais
```

---

# 11.4 Componentes do Sistema

## Frontend React + TypeScript

Responsabilidade:

Interface do usuário.

Módulos:

```
Dashboard

Upload de Arquivos

Processamento

Conciliação

Divergências

Relatórios
```

---

# Backend API

Tecnologia:

Python + FastAPI

Responsabilidades:

* autenticação;
* upload;
* orquestração;
* regras de negócio;
* comunicação com banco.

---

# Serviço de Importação

Módulo:

```
import_engine
```

Responsável por entender formatos diferentes.

Estrutura:

```
import_engine

├── expense_parser.py

├── bank_parser.py

├── accounting_parser.py

└── validators.py
```

---

# Motor de Conciliação

Módulo mais estratégico.

```
matching_engine
```

Responsabilidades:

* regras exatas;
* fuzzy matching;
* score;
* criação de vínculos.

Estrutura:

```
matching_engine

├── value_matcher.py

├── date_matcher.py

├── supplier_matcher.py

├── scoring.py

└── rules.py
```

---

# 11.5 Diagrama de Sequência - Importação de Arquivo

Fluxo:

```
Usuário

 |

 | Upload Excel

 ↓

Frontend

 |

 | POST /upload

 ↓

API

 |

 | valida arquivo

 ↓

Parser

 |

 | transforma dados

 ↓

Staging Database

 |

 | valida

 ↓

Modelo Canônico

 |

 | sucesso

 ↓

Usuário recebe status
```

---

# 11.6 Diagrama de Sequência - Conciliação

```
Usuário

 |

Solicita conciliação

 |

API

 |

Busca:

Despesa

Extrato

Razão

 |

Motor Matching

 |

Calcula Score

 |

Classifica:

-----------------

>=90

Conciliado


70-89

Revisão


<70

Divergência

-----------------

 |

Banco salva resultado

 |

Dashboard atualiza
```

---

# 11.7 Modelo Entidade Relacionamento Inicial

Agora o núcleo do banco.

## Empresa

```
empresa
---------
id PK
razao_social
cnpj
```

Relacionamento:

1:N

Empresa possui vários projetos.

---

## Projeto

```
projeto
---------
id PK

codigo

nome

empresa_id FK
```

---

## Fornecedor

```
fornecedor
---------
id PK

nome_original

nome_normalizado

documento
```

---

## Despesa

```
despesa
---------
id PK

origem_id

fornecedor_id FK

projeto_id FK

valor_total

status
```

Relacionamento:

1:N

Despesa possui parcelas.

---

## Parcela

```
parcela_despesa
----------------

id PK

despesa_id FK

valor

data_pagamento

forma_pagamento

nota_fiscal
```

---

## Movimento Bancário

```
movimento_bancario
------------------

id PK

data

descricao

valor

contraparte

```

---

## Lançamento Contábil

```
lancamento_contabil
-------------------

id PK

chave_sci

data

historico

debito

credito

contra
```

---

## Conciliação

Essa tabela é fundamental.

Ela registra a inteligência do sistema.

```
conciliacao
------------

id

parcela_id

movimento_bancario_id

lancamento_contabil_id


score

status

motivo
```

Exemplo:

```
id: 1001

Despesa:
UP ESQUADRIAS

Banco:
PIX Cp60701190

Razão:
Compra Esquadrias

Score:
96

Status:
CONCILIADO
```

---

# 11.8 Decisão Arquitetural Importante

Aqui está um ponto que eu colocaria no relatório para o cliente:

> A solução não será construída como uma integração específica para um único ERP. Ela será desenvolvida utilizando um modelo de dados canônico, permitindo receber informações provenientes de diferentes sistemas utilizados pelas construtoras, mantendo regras únicas de validação e conciliação.

Esse é o diferencial contra simplesmente utilizar uma ferramenta pronta.

---

# 11.9 Próximo documento recomendado

Agora que temos o UML inicial, o próximo documento técnico é:

## 12. Documento de Arquitetura de Software

Ele vai definir:

* arquitetura em camadas;
* padrões utilizados;
* segurança;
* estrutura dos projetos;
* organização do código;
* banco de dados;
* ambientes;
* deploy Railway;
* Docker;
* CI/CD GitHub Actions;
* estratégia de escalabilidade.

Esse documento será praticamente o "projeto executivo" antes de começar a programar. Depois dele entramos na criação do protótipo usando sua stack.
