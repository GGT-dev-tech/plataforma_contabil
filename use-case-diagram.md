Perfeito. Vamos avançar para o próximo documento: **Modelo UML Inicial do Projeto**.

A ideia aqui é transformar tudo que levantamos em uma visão que um desenvolvedor, arquiteto ou futuro parceiro consiga entender.

Neste momento ainda não vamos codificar. Vamos definir o **mapa do sistema**.

---

# DOCUMENTO UML INICIAL

## Sistema de Automação de Conciliação Financeira e Contábil Multissistema

---

# 1. Diagrama de Caso de Uso (Use Case Diagram)

## Atores do Sistema

### Usuário Contábil

Responsável por:

* importar arquivos;
* acompanhar conciliações;
* validar divergências;
* gerar relatórios.

---

### Administrador do Sistema

Responsável por:

* cadastrar empresas;
* configurar layouts;
* gerenciar usuários;
* parametrizar regras.

---

### Sistemas Externos

Representam:

* ERP das construtoras;
* SCI;
* bancos;
* sistemas financeiros.

---

# Caso de Uso Geral

```text
                 +----------------------+
                 | Usuário Contábil     |
                 +----------+-----------+
                            |
                            |
                            v

                 +----------------------+
                 | Importar Arquivos   |
                 +----------------------+

                            |
                            v

                 +----------------------+
                 | Processar Dados     |
                 +----------------------+

                            |
                            v

                 +----------------------+
                 | Normalizar Dados    |
                 +----------------------+

                            |
                            v

                 +----------------------+
                 | Executar             |
                 | Conciliação          |
                 +----------------------+

                            |
                            v

                 +----------------------+
                 | Analisar Divergências|
                 +----------------------+

                            |
                            v

                 +----------------------+
                 | Emitir Relatórios    |
                 +----------------------+

```

---

# 2. Diagrama de Componentes

Agora vamos pensar como software.

A arquitetura será dividida em módulos.

```text

                  FRONTEND
              React + TypeScript

                     |
                     |

                  API REST

                     |
        +------------+-------------+

        |                          |

 Serviço de              Serviço de
 Importação              Conciliação


        |                          |

        |                          |

 Parser                   Motor de Matching

        |

        |

 Modelo Canônico

        |

        |

 PostgreSQL


```

---

# 3. Componentes do Sistema

## 3.1 Módulo de Importação

Responsabilidade:

Receber arquivos externos.

Entradas:

* XLSX
* CSV
* PDF
* XML

Processo:

```
Arquivo bruto

      ↓

Validação

      ↓

Identificação do layout

      ↓

Parser específico

      ↓

Dados estruturados

```

---

# 3.2 Módulo de Parser

Aqui está uma parte crítica.

Como cada construtora pode ter um ERP diferente, não podemos criar um código gigante cheio de regras.

O correto é criar adaptadores.

Exemplo:

```
/parsers


   sci_parser.py

   banco_inter_parser.py

   financeiro_empresa_a.py

   financeiro_empresa_b.py


```

Cada parser transforma o formato original no modelo padrão.

---

# 3.3 Modelo Canônico

Este é o coração.

Tudo passa por ele.

Exemplo:

Antes:

ERP A:

```
Fornecedor
Valor Pago
Dt Pagamento

```

ERP B:

```
Favorecido
Total
Data Baixa

```

Depois:

Sistema:

```
Fornecedor

Valor

DataPagamento

```

---

# 4. Diagrama de Sequência

## Processo: Importação de uma nova empresa

```text

Usuário

 |

 | Upload arquivo

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


ImportService

 |

 |

 v


Parser específico

 |

 |

 v


Validação

 |

 |

 v


Modelo Canônico

 |

 |

 v


Banco de Dados


```

---

# 5. Diagrama de Sequência

## Processo: Conciliação Financeira

```text

Usuário

 |

 |

Solicita conciliação

 |

 v


Motor Conciliador

 |

 |

Busca:

- Despesas

- Banco

- Razão


 |

 |

Calcula Score


 |

 |

Resultado


 |

 |

Salvar:

MATCH

DIVERGÊNCIA

PENDENTE


```

---

# 6. Modelo Entidade Relacionamento Inicial

Agora vamos para banco de dados.

## Entidade Empresa

```
EMPRESA

id

razao_social

cnpj

created_at

```

Relacionamento:

Uma empresa possui:

* projetos
* despesas
* contas

---

## Projeto

```
PROJETO

id

codigo

nome

empresa_id

```

---

## Fornecedor

```
FORNECEDOR

id

nome_original

nome_normalizado

documento

```

---

## Despesa

```
DESPESA

id_origem

nome

fornecedor_id

projeto_id

valor_total

status

data_competencia

```

---

## Parcela

```
PARCELA_DESPESA

id_origem

despesa_id

valor

data_pagamento

forma_pagamento

```

---

## Movimento Bancário

```
MOVIMENTO_BANCARIO

id

data

historico_original

tipo_operacao

valor

contraparte

```

---

## Lançamento Contábil

```
LANCAMENTO_CONTABIL

id

chave_origem

data

historico

debito

credito

contra

```

---

## Conciliação

Essa é a entidade mais importante.

```
CONCILIACAO


id


despesa_id


movimento_bancario_id


lancamento_contabil_id


score


status


motivo


data_processamento

```

---

# 7. Regra importante de arquitetura

Eu faria uma escolha técnica aqui:

Não gravaríamos somente o dado tratado.

Guardaríamos também o dado original.

Por quê?

Porque em contabilidade existe uma palavra muito importante:

**Rastreabilidade.**

Então:

## Tabela Staging

Recebe o arquivo bruto.

Exemplo:

```
arquivo_importado

id

nome_arquivo

hash

data_upload

conteudo_original

```

Depois:

```
STAGING

        ↓

PROCESSAMENTO

        ↓

MODELO CANÔNICO

```

Isso protege contra auditoria.

---

# 8. Segurança

Mesmo sendo uma primeira versão, precisamos pensar nisso.

Obrigatório:

## Controle de acesso

Perfis:

* Administrador
* Contador
* Analista
* Auditor

---

## Logs

Registrar:

Quem importou?

Quando?

Qual arquivo?

Qual alteração?

---

## Backup

Banco PostgreSQL:

* backup diário
* retenção
* recuperação

---

# 9. Próxima decisão antes do desenvolvimento

Agora temos duas frentes possíveis:

## Caminho A — MVP rápido

Criar somente:

* upload das 3 planilhas;
* processamento;
* conciliação;
* relatório Excel.

Tempo menor.

Serve para validar comercialmente.

---

## Caminho B — Plataforma completa

Criar:

* usuários;
* múltiplas empresas;
* múltiplos ERPs;
* dashboards;
* APIs;
* regras configuráveis.

Maior investimento.

---

Minha recomendação como arquitetura:

Fazer **MVP com arquitetura preparada para evolução**.

Ou seja:

Não construir uma gambiarra descartável.

Construir o primeiro módulo já usando:

* modelo canônico;
* banco PostgreSQL;
* serviços separados;
* parsers independentes.

Assim esse protótipo pode virar produto.

---

Próximo documento que eu sugiro criar:

# Documento de Requisitos Funcionais (RF)

Ele vai definir exatamente:

* o que o sistema deve fazer;
* telas;
* processos;
* regras;
* entradas;
* saídas;
* comportamento esperado.

Depois dele fazemos:

1. Requisitos Não Funcionais
2. Modelo de Dados Final
3. APIs
4. Plano de Desenvolvimento no Antigravity
5. Primeira Sprint de implementação.
