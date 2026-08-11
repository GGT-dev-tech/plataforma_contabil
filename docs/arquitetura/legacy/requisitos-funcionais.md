Continuando a documentação do projeto como **Tech Lead**, agora vamos transformar a arquitetura em uma especificação que pode orientar o desenvolvimento.

# DOCUMENTO DE REQUISITOS FUNCIONAIS (RF) — VERSÃO 1.0

## Projeto

**Plataforma Inteligente de Integração e Conciliação Financeira/Contábil para Empresas de Construção Civil**

---

# 1. Introdução

## 1.1 Objetivo deste documento

Este documento descreve os requisitos funcionais necessários para construção do sistema.

O objetivo é definir **o que o sistema deve fazer**, independentemente da tecnologia utilizada.

A implementação deverá atender:

* contabilidades que recebem dados de múltiplas construtoras;
* empresas que utilizam ERPs distintos;
* necessidade de padronização;
* conciliação financeira e contábil automatizada.

---

# 2. Escopo Funcional

O sistema deverá permitir:

1. Cadastro de empresas;
2. Cadastro de usuários;
3. Importação de arquivos financeiros;
4. Identificação automática de origem dos dados;
5. Processamento e normalização;
6. Armazenamento em modelo padrão;
7. Execução de conciliação;
8. Análise de divergências;
9. Aprovação manual;
10. Geração de relatórios.

---

# 3. Módulos Funcionais

Arquiteturalmente o sistema será dividido nos seguintes módulos:

```text
MÓDULO 1
Gestão de Usuários


MÓDULO 2
Gestão de Empresas


MÓDULO 3
Importação de Dados


MÓDULO 4
Processamento ETL


MÓDULO 5
Modelo Canônico


MÓDULO 6
Motor de Conciliação


MÓDULO 7
Relatórios


MÓDULO 8
Auditoria
```

---

# MÓDULO 1 — Gestão de Usuários

---

# RF001 — Cadastro de Usuário

## Descrição

O sistema deve permitir cadastro de usuários responsáveis pela operação.

## Dados mínimos

* Nome;
* E-mail;
* Senha;
* Perfil de acesso;
* Empresa vinculada.

---

## Perfis previstos

### Administrador

Permissões:

* gerenciar usuários;
* configurar empresas;
* visualizar todos os dados.

---

### Analista Contábil

Permissões:

* importar arquivos;
* executar conciliação;
* analisar divergências.

---

### Auditor

Permissões:

* visualizar;
* consultar histórico;
* exportar relatórios.

---

# RF002 — Autenticação

O sistema deve permitir acesso através de autenticação segura.

Fluxo:

```text
Usuário

↓

Login

↓

Validação

↓

Token JWT

↓

Acesso ao sistema
```

---

# MÓDULO 2 — Gestão de Empresas

---

# RF003 — Cadastro de Empresa

O sistema deve permitir cadastrar empresas clientes.

Exemplo:

```text
Empresa:

VNP SPE Empreendimentos Imobiliários Ltda

CNPJ:

59.120.530/0001-16
```

---

Campos:

* razão social;
* CNPJ;
* sistema origem;
* configurações específicas.

---

# RF004 — Multiempresa

O sistema deve permitir que uma contabilidade controle diversas empresas.

Exemplo:

```text
Contabilidade

 |
 |-- Construtora A
 |
 |-- Construtora B
 |
 |-- Construtora C
```

Cada empresa terá:

* seus arquivos;
* seus usuários;
* suas conciliações.

---

# MÓDULO 3 — Importação de Dados

Esse é um dos módulos principais.

---

# RF005 — Upload de Arquivos

O sistema deve permitir envio de:

* Excel (.xlsx);
* CSV;
* PDF;
* arquivos exportados de ERP.

---

Tipos identificados:

```text
DESPESA

EXTRATO_BANCARIO

RAZAO_CONTABIL

OUTROS
```

---

Exemplo:

Usuário envia:

```
Despesas 06-2026.xlsx
```

Sistema registra:

```
Tipo:
DESPESA

Período:
06/2026

Empresa:
VNP
```

---

# RF006 — Armazenamento do Arquivo Original

O sistema deve preservar o arquivo original enviado.

Motivo:

Auditoria.

Estrutura:

```
storage/

empresa/

2026/

06/

arquivo_original.xlsx
```

---

# RF007 — Identificação Automática do Layout

O sistema deve tentar identificar automaticamente a origem.

Exemplo:

Arquivo:

```
Razão SUCESSOR.xlsx
```

Sistema identifica:

```
Origem:
SCI VISUAL Sucessor

Tipo:
RAZÃO CONTÁBIL
```

---

Critérios:

* nome de colunas;
* padrões internos;
* palavras-chave;
* estrutura do arquivo.

---

# MÓDULO 4 — Processamento ETL

---

# RF008 — Extração de Dados

O sistema deve extrair informações dos arquivos.

Exemplo:

Entrada:

```
Pix enviado:
Cp :60701190-UP ESQUADRIAS

-R$132500
```

Saída:

```json
{
"tipo":"PIX",
"fornecedor":"UP ESQUADRIAS",
"valor":132500
}
```

---

# RF009 — Limpeza e Padronização

O sistema deve:

* remover caracteres inválidos;
* normalizar datas;
* converter moedas;
* padronizar textos.

---

Exemplo:

Antes:

```
UP ESQUADRIAS LTDA.
```

Depois:

```
UP ESQUADRIAS
```

---

# RF010 — Controle de Erros

Caso um arquivo apresente problemas:

Exemplo:

```
Valor inválido

Data ausente

Coluna inexistente
```

O sistema deve:

* interromper processamento;
* registrar erro;
* informar usuário.

---

# MÓDULO 5 — Modelo Canônico

---

# RF011 — Conversão para Modelo Padrão

Todos os dados importados devem ser convertidos para uma estrutura única.

---

Exemplo:

Origem:

```
ERP Construtora A

Fornecedor
Valor Parcela
Data Pagamento
```

Origem:

```
SCI

Histórico
Débito
Crédito
```

Destino:

```
Movimento Financeiro Padrão
```

---

# RF012 — Rastreabilidade

Todo dado normalizado deve manter:

* arquivo origem;
* linha origem;
* sistema origem.

Exemplo:

```
Movimento ID 500

Origem:

Razão SUCESSOR.xlsx

Linha:

87
```

---

# MÓDULO 6 — Motor de Conciliação

Aqui está o principal valor agregado.

---

# RF013 — Executar Conciliação Tripla

O sistema deve comparar:

```text
DESPESAS

     ↓

BANCO

     ↓

CONTABILIDADE
```

---

# RF014 — Conciliação Financeira

Comparar:

Despesa:

```
Fornecedor:
BH MATERIAIS

Valor:
R$5.000

Data:
05/06/2026
```

Banco:

```
PIX BH MATERIAIS

Valor:
R$5.000

Data:
05/06/2026
```

Resultado:

```
CONCILIADO
```

---

# RF015 — Conciliação Contábil

Comparar:

Banco:

```
Saída R$5.000
```

Razão:

```
Crédito R$5.000
```

Resultado:

```
LANÇAMENTO CONTÁBIL ENCONTRADO
```

---

# RF016 — Cálculo de Score

Cada conciliação deve possuir um índice de confiança.

Exemplo:

```
Valor:
40 pontos

Data:
20 pontos

Fornecedor:
30 pontos

Nota fiscal:
10 pontos
```

Total:

```
100 pontos
```

---

Regra:

```
>=95

Conciliação automática


70-94

Revisão manual


<70

Divergência
```

---

# RF017 — Aprovação Manual

Usuário deve poder:

* aceitar sugestão;
* rejeitar;
* informar motivo.

---

Exemplo:

Sistema:

```
Possível correspondência encontrada:

95%

Aceitar?
```

Usuário:

```
SIM
```

---

# MÓDULO 7 — Relatórios

---

# RF018 — Relatório Executivo

Deve apresentar:

* total movimentado;
* total conciliado;
* total pendente;
* percentual de sucesso.

---

Exemplo:

```
Período Junho/2026

Total despesas:
R$500.000

Conciliado:
R$470.000

Pendências:
R$30.000

Eficiência:
94%
```

---

# RF019 — Relatório de Divergências

Separar:

## Despesas sem banco

```
Existe pagamento previsto,
mas não existe saída bancária.
```

---

## Banco sem despesa

```
Existe saída bancária,
mas não existe origem financeira.
```

---

## Banco sem contabilidade

```
Existe movimento,
mas não existe lançamento contábil.
```

---

# RF020 — Exportação

Permitir:

* Excel;
* PDF;
* CSV.

---

# MÓDULO 8 — Auditoria

---

# RF021 — Histórico de Operações

Registrar:

* usuário;
* data;
* arquivo;
* ação realizada.

---

Exemplo:

```
30/07/2026 14:32

Usuário João

Importou:

Razão SUCESSOR.xlsx
```

---

# RF022 — Versionamento de Processamento

Cada execução deve gerar uma versão.

Exemplo:

```
Conciliação Junho/2026

Versão 01

Processada em:
30/07/2026
```

---

# Resumo dos Requisitos Funcionais

| Código | Descrição          |
| ------ | ------------------ |
| RF001  | Cadastro usuário   |
| RF002  | Autenticação       |
| RF003  | Cadastro empresa   |
| RF004  | Multiempresa       |
| RF005  | Upload arquivos    |
| RF006  | Guardar original   |
| RF007  | Identificar layout |
| RF008  | Extrair dados      |
| RF009  | Normalizar dados   |
| RF010  | Controle erros     |
| RF011  | Modelo canônico    |
| RF012  | Rastreabilidade    |
| RF013  | Conciliação tripla |
| RF014  | Banco x Despesa    |
| RF015  | Banco x Razão      |
| RF016  | Score              |
| RF017  | Aprovação          |
| RF018  | Dashboard          |
| RF019  | Divergências       |
| RF020  | Exportação         |
| RF021  | Auditoria          |
| RF022  | Versionamento      |

---

## Próxima etapa técnica

Agora devemos criar o:

# DOCUMENTO DE REQUISITOS NÃO FUNCIONAIS (RNF)

Ele vai definir os critérios de qualidade:

* segurança;
* performance;
* escalabilidade;
* disponibilidade;
* LGPD;
* logs;
* backup;
* arquitetura multiempresa;
* padrões de desenvolvimento.

Depois disso teremos base suficiente para criar:

1. **Modelo de Dados Canônico definitivo**
2. **Diagrama UML de Classes**
3. **Diagrama de Sequência detalhado**
4. **Backlog de desenvolvimento no padrão Scrum**
5. **Plano de implementação no Antigravity + stack definida**.
