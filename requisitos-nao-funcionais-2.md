Perfeito. Vamos seguir para o próximo documento. Agora entramos na parte que vai transformar a arquitetura em **escopo executável de desenvolvimento**.

Esse documento será muito importante para a negociação com o cliente, porque evita que o projeto fique subjetivo. Ele deixa claro **o que será entregue, quais funcionalidades existem e quais regras serão implementadas**.

---

# 13. DOCUMENTO DE REQUISITOS FUNCIONAIS (RF)

## 13.1 Objetivo do Documento

Este documento descreve os requisitos funcionais da plataforma de automação de conciliação financeira e contábil.

O objetivo é definir as funcionalidades necessárias para que o sistema:

* receba dados de diferentes sistemas;
* faça a padronização das informações;
* execute a conciliação financeira e contábil;
* identifique inconsistências;
* gere relatórios auditáveis.

---

# 13.2 Visão Geral do Sistema

A solução será composta pelos seguintes módulos:

```
+------------------------------------------------+
| Plataforma de Conciliação Financeira Contábil  |
+------------------------------------------------+

                |
                |

1. Gestão de Arquivos

                |

2. Processamento e Normalização

                |

3. Modelo Canônico

                |

4. Motor de Conciliação

                |

5. Análise de Divergências

                |

6. Relatórios

                |

7. Auditoria
```

---

# 13.3 Requisitos Funcionais

---

# RF001 - Cadastro de Usuários

## Descrição

O sistema deverá permitir o cadastro de usuários autorizados.

## Usuários envolvidos

* Administrador
* Analista Financeiro
* Contador
* Auditor

## Dados mínimos

```
Nome

E-mail

Perfil

Status

Data de criação
```

---

## Regras

* Usuários inativos não podem acessar o sistema.
* Toda ação deve possuir identificação do usuário responsável.

---

# RF002 - Controle de Permissões

## Descrição

O sistema deverá controlar acesso baseado em perfil.

Exemplo:

### Administrador

Pode:

* cadastrar usuários;
* configurar regras;
* visualizar tudo.

### Financeiro

Pode:

* importar arquivos;
* executar conciliação;
* visualizar resultados.

### Auditor

Pode:

* consultar;
* gerar relatórios;
* visualizar histórico.

---

# RF003 - Upload de Arquivos

## Descrição

O sistema deverá permitir envio de arquivos financeiros, bancários e contábeis.

Tipos suportados inicialmente:

```
.xlsx

.xls

.csv

.pdf (futuro)
```

---

Arquivos previstos:

### Financeiro

Exemplo:

```
Despesas 06-2026.xlsx
```

---

### Banco

Exemplo:

```
Extrato Banco Inter.xlsx
```

---

### Contabilidade

Exemplo:

```
Razão SCI.xlsx
```

---

## Validações

O sistema deve verificar:

* extensão;
* tamanho;
* arquivo corrompido;
* estrutura esperada.

---

# RF004 - Armazenamento do Arquivo Original

## Descrição

Todos os arquivos enviados devem ser armazenados.

Informações:

```
Nome original

Usuário responsável

Data envio

Hash do arquivo

Tipo

Status processamento
```

---

Objetivo:

Garantir rastreabilidade.

---

# RF005 - Identificação Automática do Layout

## Descrição

O sistema deverá identificar automaticamente o tipo de arquivo recebido.

Exemplo:

Arquivo:

```
Razão SUCESSOR.xlsx
```

Sistema identifica:

```
Tipo:
Razão Contábil

Origem:
SCI VISUAL
```

---

Critérios:

* nome do arquivo;
* cabeçalhos;
* padrões internos;
* estrutura de colunas.

---

# RF006 - Processamento da Planilha de Despesas

## Descrição

O sistema deverá interpretar arquivos financeiros provenientes dos sistemas das construtoras.

Entrada:

```
Despesas.xlsx
```

---

Processamento:

Extrair:

```
Fornecedor

Projeto

Valor parcela

Data pagamento

Forma pagamento

Nota fiscal

Conta bancária
```

---

Transformação:

Antes:

```
UP ESQUADRIAS LTDA
```

Depois:

```
fornecedor_normalizado:

UP ESQUADRIAS
```

---

# RF007 - Processamento do Extrato Bancário

## Descrição

O sistema deverá interpretar extratos bancários mesmo quando não estiverem estruturados.

---

O parser deverá:

* identificar datas;
* identificar movimentações;
* identificar entradas e saídas;
* extrair beneficiários;
* converter valores.

---

Exemplo:

Origem:

```
Pix enviado:
Cp:60701190
UP ESQUADRIAS
-R$13.500,00
```

Resultado:

```
Data:
26/06/2026

Tipo:
PIX

Fornecedor:
UP ESQUADRIAS

Valor:
-13500.00
```

---

# RF008 - Processamento do Razão Contábil

## Descrição

O sistema deverá interpretar relatórios contábeis exportados do SCI.

---

Deverá extrair:

```
Data

Histórico

Chave SCI

Débito

Crédito

Conta Contra

Saldo
```

---

Exemplo:

Origem:

```
Compra a Vista de Esquadrias
Chave 40070
Crédito 13.500
```

Resultado:

```
Lançamento Contábil

Valor:
13500

Origem:
SCI

Chave:
40070
```

---

# RF009 - Modelo Canônico

## Descrição

Após o processamento, todos os dados devem seguir uma estrutura única.

Objetivo:

Permitir integração de diferentes ERPs.

Exemplo:

Sistemas diferentes:

```
ERP A

Fornecedor

Fornecedor Nome

Favorecido
```

Todos viram:

```
Fornecedor
```

---

# RF010 - Execução da Conciliação Tripla

## Descrição

O sistema deverá executar conciliação entre:

```
Despesa

     X

Banco

     X

Contabilidade
```

---

Processo:

Para cada parcela paga:

Buscar:

1. Movimento bancário correspondente.

2. Lançamento contábil correspondente.

---

# RF011 - Motor de Matching

## Descrição

O sistema deverá calcular compatibilidade entre registros.

Critérios:

## Valor

Peso:

40%

## Data

Peso:

20%

## Fornecedor

Peso:

30%

## Nota fiscal

Peso:

10%

---

Resultado:

```
90-100

Conciliado automaticamente


70-89

Revisão necessária


0-69

Divergência
```

---

# RF012 - Tela de Conciliações

## Descrição

O usuário deverá visualizar os resultados.

Informações:

```
Fornecedor

Valor

Data

Projeto

Banco

Razão

Score

Status
```

---

Exemplo:

| Fornecedor    | Valor  | Score | Status     |
| ------------- | ------ | ----- | ---------- |
| UP Esquadrias | 13.500 | 96    | Conciliado |
| Fornecedor X  | 5.000  | 65    | Revisar    |

---

# RF013 - Gestão de Divergências

O sistema deverá separar:

## Banco sem Financeiro

Exemplo:

Existe:

```
PIX - R$5.000
```

Mas não existe despesa.

---

## Financeiro sem Banco

Exemplo:

Existe:

```
Despesa fornecedor X
```

Mas não houve pagamento.

---

## Banco sem Contabilidade

Exemplo:

Existe:

```
Movimento bancário
```

Mas não existe razão.

---

## Contabilidade sem Banco

Exemplo:

Existe:

```
Lançamento SCI
```

Mas não existe extrato.

---

# RF014 - Aprovação Manual

## Descrição

O usuário poderá confirmar ou rejeitar uma sugestão automática.

Exemplo:

Sistema:

```
Score 85

Possível correspondência:
Fornecedor ABC
```

Usuário:

```
Confirmar Match
```

---

O sistema deverá registrar:

```
Usuário

Data

Decisão

Motivo
```

---

# RF015 - Geração de Relatórios

O sistema deverá gerar:

## Relatório Executivo

Resumo:

```
Total analisado

Quantidade conciliada

Quantidade divergente

Percentual de automação
```

---

## Relatório Operacional

Detalhamento:

```
Item

Fornecedor

Banco

Razão

Status

Motivo
```

---

## Relatório de Auditoria

Histórico:

```
Arquivo origem

Processamento

Usuário

Alterações
```

---

# RF016 - Exportação

Formatos:

Inicial:

```
Excel (.xlsx)
```

Futuro:

```
PDF

API

Integração ERP
```

---

# RF017 - Histórico de Processamentos

O sistema deverá armazenar:

```
Quando processou

Quem executou

Quantidade registros

Erros encontrados

Tempo processamento
```

---

# 13.4 Priorização das Funcionalidades

Agora pensando como Tech Lead, eu dividiria em fases:

---

# MVP - Primeira Entrega

Objetivo:
Validar valor para o cliente.

Implementar:

✅ Upload dos três arquivos
✅ Parser das três fontes
✅ Banco PostgreSQL
✅ Modelo canônico
✅ Conciliação básica
✅ Relatório Excel
✅ Tela simples de acompanhamento

---

# Fase 2

Evolução:

✅ Matching inteligente
✅ Aprovação manual
✅ Dashboard
✅ Usuários
✅ Auditoria

---

# Fase 3

Produto escalável:

✅ Integração API ERP
✅ Open Banking
✅ IA para classificação
✅ Multiempresa
✅ Multi construtoras

---

# Observação estratégica para negociação

Eu apresentaria ao cliente desta forma:

> "A primeira etapa não será substituir o sistema contábil ou financeiro existente. O objetivo inicial é criar uma camada inteligente de integração e conciliação, capaz de receber os dados dos sistemas atuais, independentemente do ERP utilizado pelas construtoras, reduzindo trabalho manual e aumentando a confiabilidade das informações."

Essa frase é importante porque posiciona você como **solução complementar**, não como concorrente dos sistemas que ele já conhece (como SCI).

---

Próxima etapa:

# 14. Documento de Requisitos Não Funcionais (RNF)

Nele vamos definir:

* segurança;
* desempenho;
* disponibilidade;
* LGPD;
* logs;
* backup;
* escalabilidade;
* padrões de desenvolvimento;
* qualidade de código;
* critérios para colocar em produção.
