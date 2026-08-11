Perfeito. Vamos seguir para o próximo documento da documentação do projeto.

Agora entra uma etapa fundamental antes de escrever código: **Documento de Requisitos Funcionais (RF)**.

Esse documento será a ponte entre a necessidade do cliente e o desenvolvimento. Ele evita que o projeto vire uma sequência de ajustes sem controle.

---

# DOCUMENTO DE REQUISITOS FUNCIONAIS (RF)

## Sistema de Automação de Conciliação Financeira e Contábil Multissistema

**Versão:** 1.0
**Objetivo:** Definir as funcionalidades necessárias para uma plataforma capaz de importar, padronizar, conciliar e apresentar informações financeiras e contábeis provenientes de diferentes sistemas.

---

# 1. Visão Geral

## 1.1 Objetivo do Sistema

O sistema deverá automatizar o processo de conciliação entre diferentes fontes de dados empresariais, reduzindo atividades manuais realizadas pela contabilidade.

A solução deverá permitir:

* importar dados financeiros;
* interpretar diferentes formatos de arquivos;
* padronizar informações;
* cruzar dados financeiros, bancários e contábeis;
* identificar divergências;
* gerar relatórios auditáveis.

---

# 2. Escopo Inicial (MVP)

A primeira versão deverá atender o seguinte cenário:

Entrada:

### Arquivo 1

**Despesas**

Origem:
Sistema financeiro/ERP da construtora

Representa:

> O que deveria ter sido pago.

---

### Arquivo 2

**Extrato Bancário**

Origem:
Banco

Representa:

> O que efetivamente movimentou o caixa.

---

### Arquivo 3

**Razão Contábil**

Origem:
SCI / Sistema contábil

Representa:

> O que foi contabilizado.

---

Saída:

Relatório de conciliação:

* itens conciliados;
* divergências;
* lançamentos ausentes;
* pagamentos não identificados;
* inconsistências contábeis.

---

# 3. Requisitos Funcionais

---

# RF001 — Cadastro de Empresas

## Descrição

O sistema deverá permitir cadastrar empresas participantes da operação.

## Dados mínimos

* Razão social;
* CNPJ;
* Nome fantasia;
* Sistema origem;
* Data cadastro.

## Exemplo

```
Empresa:

VNP Empreendimentos Imobiliários Ltda

Sistema Financeiro:

ERP Próprio

Sistema Contábil:

SCI Visual Sucessor
```

---

# RF002 — Upload de Arquivos

## Descrição

O usuário deverá conseguir enviar arquivos para processamento.

## Formatos suportados inicialmente

* XLSX
* CSV

Futuramente:

* PDF
* XML
* API

---

## Informações armazenadas

* Nome arquivo;
* Usuário responsável;
* Data envio;
* Empresa relacionada;
* Tipo arquivo.

Exemplo:

```
Arquivo:

Razao_06_2026.xlsx


Tipo:

Razão Contábil


Empresa:

VNP

```

---

# RF003 — Identificação Automática do Layout

## Descrição

O sistema deverá identificar qual modelo de arquivo foi recebido.

Exemplo:

Entrada:

```
Razão SUCESSOR.xlsx
```

Sistema identifica:

```
Tipo:

SCI Razão Contábil

Parser:

SCIParser
```

---

Possíveis identificações futuras:

* SCI;
* Sienge;
* Mega;
* TOTVS;
* Omie;
* ERPs próprios.

---

# RF004 — Processamento de Dados

## Descrição

O sistema deverá transformar arquivos brutos em dados estruturados.

Processos:

* remover cabeçalhos;
* eliminar linhas inválidas;
* converter datas;
* converter moedas;
* normalizar textos.

---

Exemplo:

Entrada:

```
R$ 13.250,00
```

Saída:

Banco:

```
13250.00
```

---

# RF005 — Armazenamento dos Dados Originais

## Descrição

O sistema deverá manter o arquivo original para auditoria.

Motivo:

Em processos contábeis, toda informação precisa ser rastreável.

Guardar:

* arquivo original;
* hash do arquivo;
* data processamento;
* usuário responsável.

---

# RF006 — Normalização de Fornecedores

## Descrição

O sistema deverá padronizar nomes para permitir cruzamento.

Exemplo:

Origem 1:

```
UP ESQUADRIAS LTDA
```

Origem 2:

```
Up Esquadrias
```

Modelo:

```
UP ESQUADRIAS
```

---

Processos:

* remover acentos;
* remover caracteres especiais;
* converter para maiúsculo;
* aplicar similaridade.

---

# RF007 — Motor de Conciliação Tripla

## Descrição

O sistema deverá realizar a conciliação entre:

```
DESPESA

     X

BANCO

     X

CONTABILIDADE

```

---

# RF008 — Conciliação Despesa x Banco

## Regras

Comparar:

### Valor

Exemplo:

Despesa:

```
-1392,20
```

Banco:

```
-1392,20
```

---

### Data

Aceitar:

```
Data pagamento

±1 dia útil
```

---

### Fornecedor

Comparação:

```
Fornecedor

versus

Histórico Pix

```

---

Resultado:

```
MATCH
95%
```

---

# RF009 — Conciliação Banco x Razão

Comparar:

* valor;
* data;
* histórico;
* conta contábil.

Exemplo:

Banco:

```
PIX UP ESQUADRIAS

-13.250
```

Razão:

```
Compra Esquadrias Bioma

Crédito:

13.250

```

Resultado:

```
Conciliado

```

---

# RF010 — Classificação de Resultado

Cada conciliação deverá possuir status.

## Conciliado

Quando:

Score >= 95%

---

## Possível Conciliação

Quando:

Score:

70% - 94%

---

## Divergente

Quando:

Score:

<70%

---

# RF011 — Relatório de Conciliação

O sistema deverá gerar relatório.

Formato inicial:

Excel.

---

Abas:

## 1. Resumo

Exemplo:

```
Total despesas:

R$ 850.000,00


Total banco:

R$ 848.000,00


Diferença:

R$ 2.000,00

```

---

## 2. Conciliados

Campos:

* fornecedor;
* valor;
* data;
* origem;
* score.

---

## 3. Pendências

Campos:

* item;
* motivo;
* origem;
* ação recomendada.

---

# RF012 — Histórico de Processamentos

O sistema deverá manter histórico.

Exemplo:

```
Processamento:

Julho/2026


Arquivo:

Despesas.xlsx


Status:

Finalizado


Usuário:

Administrador

```

---

# RF013 — Dashboard Gerencial

(Fase posterior)

Indicadores:

* percentual conciliado;
* valores divergentes;
* fornecedores sem identificação;
* despesas por projeto;
* custos por obra.

---

# RF014 — Configuração de Novos Layouts

Esse requisito é estratégico.

Como existem várias construtoras, o sistema deverá permitir adicionar novos formatos.

Exemplo:

Novo cliente:

Construtora ABC

ERP:

Sistema próprio

Criar:

```
ABCParser

```

Sem alterar o núcleo.

---

# 4. Requisitos Funcionais Prioritários do MVP

Vamos classificar:

## Alta prioridade

✅ Upload arquivos
✅ Parser dos três arquivos atuais
✅ Modelo canônico
✅ Banco PostgreSQL
✅ Motor de matching
✅ Relatório Excel

---

## Média prioridade

✅ Dashboard
✅ Usuários
✅ Permissões
✅ Configuração de regras

---

## Baixa prioridade

✅ Integrações via API
✅ Machine Learning
✅ Open Banking

---

# 5. Critérios de Aceite do MVP

O MVP será considerado aprovado quando:

1. Usuário conseguir importar os três arquivos.

2. Sistema conseguir interpretar os layouts.

3. Sistema gerar registros estruturados.

4. Sistema executar conciliação tripla.

5. Sistema gerar relatório de divergências.

6. Resultado puder ser auditado voltando ao arquivo original.

---

# Próximo documento da sequência

Agora precisamos criar:

# Documento de Requisitos Não Funcionais (RNF)

Esse é ainda mais importante para justificar decisões técnicas:

* segurança;
* performance;
* arquitetura;
* escalabilidade;
* logs;
* backup;
* LGPD;
* disponibilidade;
* padrões de desenvolvimento.

Depois dele vamos para:

1. Modelo de Dados Canônico Final
2. Especificação das APIs
3. Diagramas UML detalhados
4. Plano de desenvolvimento no Antigravity
5. Sprint 1 de implementação.
