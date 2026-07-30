Vamos continuar então. Vou avançar para o próximo artefato técnico: **Documento UML — Versão 1 (Visão Arquitetural e Funcional)**.

A ideia aqui é transformar tudo que levantamos em uma documentação que posteriormente pode ser utilizada para desenvolvimento, apresentação ao cliente e também como base para trabalhar com outros desenvolvedores.

---

# DOCUMENTO UML — SISTEMA DE CONCILIAÇÃO FINANCEIRA E CONTÁBIL MULTISSISTEMA

## 1. Objetivo do Documento

Este documento tem como objetivo representar a estrutura inicial do sistema de automação de conciliação financeira e contábil, contemplando:

* integração com múltiplas fontes de dados;
* processamento e padronização das informações;
* armazenamento em modelo canônico;
* execução de regras inteligentes de conciliação;
* apresentação das divergências;
* rastreabilidade dos dados.

---

# 2. Visão Geral do Sistema

## Nome do sistema

**Plataforma de Integração e Conciliação Financeira Contábil**

Sigla:

**PICFC**

---

# 3. Atores do Sistema

## 3.1 Analista Contábil

Responsável por:

* importar arquivos;
* acompanhar processamento;
* analisar divergências;
* aprovar conciliações;
* gerar relatórios.

---

## 3.2 Administrador do Sistema

Responsável por:

* cadastrar empresas;
* configurar integrações;
* gerenciar usuários;
* parametrizar regras.

---

## 3.3 ERP Financeiro da Construtora

Sistema externo responsável por fornecer:

* despesas;
* fornecedores;
* projetos;
* pagamentos.

---

## 3.4 Sistema Bancário

Fonte externa:

* extratos;
* movimentações financeiras.

---

## 3.5 Sistema Contábil SCI

Fonte externa:

* razão contábil;
* lançamentos;
* contas contábeis.

---

# 4. Diagrama de Caso de Uso

Representação textual inicial:

```
                  +----------------+
                  | Analista       |
                  | Contábil       |
                  +-------+--------+
                          |
                          |
        +--------------------------------+
        | Sistema de Conciliação          |
        |                                |
        |  Importar Arquivos             |
        |                                |
        |  Validar Estrutura             |
        |                                |
        |  Processar Dados               |
        |                                |
        |  Executar Matching             |
        |                                |
        |  Revisar Divergências          |
        |                                |
        |  Gerar Relatórios              |
        +--------------------------------+

             ^
             |
             |

 ERP --------+
             |
 Banco ------+
             |
 SCI --------+

```

---

# 5. Casos de Uso Detalhados

---

# UC001 — Importação de Arquivo

## Objetivo

Permitir que o usuário envie arquivos provenientes de diferentes sistemas.

---

## Entrada

Arquivos:

* XLSX
* CSV
* PDF convertido
* futuramente API

---

## Fluxo Principal

1. Usuário seleciona arquivo.
2. Sistema identifica origem.
3. Sistema valida extensão.
4. Sistema armazena arquivo bruto.
5. Sistema envia para processamento.

---

## Resultado

Arquivo disponível para pipeline.

---

# UC002 — Identificação de Layout

Esse é um ponto muito importante.

Como cada construtora pode usar um ERP diferente, não podemos criar um importador fixo.

O sistema precisa identificar:

Exemplo:

Arquivo recebido:

```
Despesas.xlsx
```

Sistema identifica:

```
Fornecedor
Valor parcela
Data pagamento
Projeto
```

Classifica:

```
Tipo:
Financeiro - Contas a Pagar
Origem:
ERP Genérico
```

---

# UC003 — Normalização dos Dados

Responsável por transformar:

Dado original:

```
UP ESQUADRIAS LTDA
-33500
30/06/2026
```

Em:

Modelo interno:

```
Fornecedor:
UP ESQUADRIAS

Valor:
33500.00

Natureza:
SAIDA

Data:
2026-06-30
```

---

# UC004 — Conciliação Tripla

O coração do sistema.

---

## Entrada

### Financeiro

```
Despesa
Fornecedor
Valor
Data
Projeto
```

---

### Banco

```
Movimento
Histórico
Valor
Data
```

---

### Contabilidade

```
Lançamento
Débito
Crédito
Conta
```

---

## Processo

```
Financeiro

    |
    |
    v

Banco

    |
    |
    v

Contabilidade

```

---

## Resultado

Exemplo:

```
Despesa:
UP ESQUADRIAS
R$ 33.500,00

Banco:
PIX UP ESQUADRIAS
-R$ 33.500,00

Razão:
Compra Esquadrias
Crédito Banco
R$ 33.500,00


STATUS:

CONCILIADO

Score:
98%

```

---

# 6. Diagrama de Componentes

Agora pensando como software.

```
+--------------------------------+

          Frontend

      React + TypeScript

+--------------------------------+

               |

               |

+--------------------------------+

          API Backend

             FastAPI

+--------------------------------+

               |

       ----------------

       |              |

       |              |

+-------------+   +-------------+

| Importador  |   | Motor       |
| Arquivos    |   | Matching    |

+-------------+   +-------------+

       |

       |

+--------------------------------+

       Modelo Canônico

        PostgreSQL

+--------------------------------+

       |

       |

+--------------------------------+

       Relatórios

       Excel/PDF

+--------------------------------+

```

---

# 7. Arquitetura Interna Recomendada

Eu mudaria um ponto da arquitetura inicial.

Não criaria somente:

```
Upload
↓
Banco
```

Criaria três camadas.

---

## Camada 1 — Raw Data

Dados exatamente como chegaram.

Exemplo:

```
arquivo_original

extrato_inter_06_2026.xlsx

linha 45:
"Pix enviado..."
```

Objetivo:

Auditoria.

---

## Camada 2 — Staging

Dados parcialmente tratados.

Exemplo:

```
movimento_banco_temp

data encontrada
valor convertido
histórico separado

```

---

## Camada 3 — Canonical Model

Dados oficiais internos.

Exemplo:

```
movimento_bancario

id
data
valor
fornecedor
origem
```

---

Essa arquitetura é fundamental para um projeto contábil porque você consegue responder:

"De onde veio esse número?"

E mostrar:

Arquivo → Linha → Tratamento → Resultado.

---

# 8. Próximo documento UML

O próximo passo agora será criar:

# UML 02 — Modelo Entidade Relacionamento (MER)

Com:

* tabelas;
* campos;
* chaves primárias;
* relacionamentos;
* cardinalidades.

Ele será a base direta para criar:

* PostgreSQL;
* migrations;
* APIs;
* classes Python.

---

Depois dele faremos:

1. **Diagrama de Sequência do Pipeline de Importação**
2. **Diagrama de Sequência da Conciliação**
3. **Arquitetura de APIs**
4. **Backlog técnico do MVP**
5. **Estrutura inicial do projeto no GitHub**

Continuando como Tech Lead, o próximo artefato será o **Modelo Entidade-Relacionamento completo do sistema**.
