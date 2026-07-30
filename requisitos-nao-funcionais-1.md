Perfeito. Vamos continuar com o próximo documento da arquitetura do projeto.

Agora entramos em uma parte que normalmente diferencia um projeto profissional de um desenvolvimento apenas funcional: os **Requisitos Não Funcionais (RNF)**.

Enquanto os requisitos funcionais respondem **"o que o sistema faz"**, os não funcionais respondem:

> "Como o sistema deve funcionar para ser seguro, confiável, escalável e sustentável."

---

# DOCUMENTO DE REQUISITOS NÃO FUNCIONAIS (RNF)

## Sistema de Automação de Conciliação Financeira e Contábil Multissistema

**Versão:** 1.0

---

# 1. Objetivo

Definir os requisitos técnicos, operacionais e de qualidade necessários para garantir que o sistema tenha:

* segurança;
* confiabilidade;
* rastreabilidade;
* desempenho adequado;
* possibilidade de crescimento;
* facilidade de manutenção.

---

# 2. Arquitetura Tecnológica Base

A solução será desenvolvida seguindo arquitetura moderna baseada em serviços.

## Stack definida inicialmente

### Backend

**Python + FastAPI**

Responsabilidades:

* API;
* processamento;
* regras de negócio;
* motor de conciliação.

---

### Frontend

**React + TypeScript**

Responsabilidades:

* interface;
* dashboards;
* upload;
* acompanhamento.

---

### Banco de Dados

Desenvolvimento:

**SQLite**

Produção:

**PostgreSQL**

---

### Infraestrutura

* Docker;
* Railway;
* GitHub Actions;
* CI/CD automatizado.

---

# RNF001 — Segurança de Dados

## Descrição

O sistema deverá garantir proteção das informações financeiras e contábeis processadas.

Como serão tratados dados de:

* empresas;
* fornecedores;
* valores financeiros;
* documentos fiscais;
* informações bancárias.

---

## Requisitos

O sistema deverá:

* utilizar comunicação HTTPS;
* armazenar senhas criptografadas;
* evitar armazenamento de dados sensíveis sem necessidade;
* controlar acesso por usuário.

---

# RNF002 — Controle de Acesso

## Perfis previstos

## Administrador

Permissões:

* cadastrar empresas;
* gerenciar usuários;
* configurar layouts.

---

## Analista Contábil

Permissões:

* importar arquivos;
* executar conciliações;
* visualizar relatórios.

---

## Auditor

Permissões:

* somente leitura;
* acesso aos históricos.

---

Modelo:

```text
Usuário

   |
   |
   +---- Perfil

             |
             |
             +---- Permissões

```

---

# RNF003 — Auditoria e Rastreabilidade

Esse é um requisito crítico.

Em sistemas contábeis, não basta apresentar o resultado.

É necessário provar:

"De onde veio esse dado?"

---

Cada registro deverá manter:

* arquivo origem;
* data de importação;
* usuário responsável;
* linha original;
* sistema de origem;
* transformação aplicada.

---

Exemplo:

Resultado:

```
Pagamento conciliado:
UP ESQUADRIAS

Valor:
R$ 13.250,00

```

O usuário deve conseguir consultar:

```
Arquivo:
Extrato-01-06-2026.xlsx

Linha:
58

Origem:
Banco Inter

Processado:
30/07/2026 10:32

Regra aplicada:
Valor + Data + Fornecedor

Score:
98%

```

---

# RNF004 — Integridade dos Dados

O sistema não poderá alterar dados originais.

Arquitetura:

```
Arquivo Original

       ↓

Dados Brutos (STAGING)

       ↓

Dados Normalizados

       ↓

Modelo Canônico

       ↓

Conciliação

```

---

Motivo:

Separar:

* dado recebido;
* dado tratado;
* resultado.

---

# RNF005 — Performance

O sistema deverá processar arquivos financeiros sem degradação significativa.

Meta inicial:

Arquivos:

* até 50.000 registros

Tempo esperado:

* processamento inferior a 5 minutos.

---

Estratégia:

* processamento em lote;
* índices no banco;
* processamento assíncrono futuro.

---

# RNF006 — Escalabilidade

A arquitetura deverá permitir evolução.

Hoje:

```
1 contabilidade

3 arquivos

1 empresa

```

Futuro:

```
100 construtoras

100 ERPs

milhões de lançamentos

```

---

Por isso:

Não criar regras fixas.

Criar:

```
Parser

       +

Modelo Canônico

       +

Motor de Regras

```

---

# RNF007 — Disponibilidade

Sistema deverá possuir disponibilidade adequada para ambiente empresarial.

Objetivo inicial:

99% de disponibilidade.

---

Ações:

* monitoramento;
* logs;
* tratamento de erros;
* backup.

---

# RNF008 — Backup e Recuperação

Banco PostgreSQL deverá possuir:

* backup periódico;
* retenção histórica;
* possibilidade de restauração.

---

Estratégia:

Backup:

diário

Retenção:

mínimo 30 dias

---

# RNF009 — Logs do Sistema

Todas operações relevantes deverão gerar logs.

Exemplo:

```
2026-07-30

Usuário:
João

Ação:
Importou Despesas_06_2026.xlsx

Resultado:
174 registros processados

Status:
Sucesso

```

---

Eventos registrados:

* login;
* upload;
* processamento;
* erro;
* alteração de configuração;
* geração de relatório.

---

# RNF010 — Tratamento de Erros

O sistema nunca deve simplesmente falhar.

Exemplo:

Arquivo:

```
Razão SCI.xlsx
```

Problema:

layout alterado.

Sistema:

Não quebrar.

Retornar:

```
Processamento interrompido

Motivo:

Layout não identificado

Ação:

Cadastrar novo parser

```

---

# RNF011 — Manutenibilidade

O código deverá seguir padrões profissionais.

Obrigatório:

* separação por módulos;
* documentação;
* testes automatizados;
* controle de versão.

---

Estrutura:

```
backend

 ├── api

 ├── domain

 ├── services

 ├── parsers

 ├── repositories

 ├── tests

```

---

# RNF012 — Testabilidade

Cada módulo crítico deverá possuir testes.

Exemplo:

Parser Extrato Banco Inter.

Entrada:

```
Extrato.xlsx
```

Resultado esperado:

```
179 linhas

35 movimentações

Saldo final correto

```

---

# RNF013 — LGPD

O sistema deverá respeitar princípios da Lei Geral de Proteção de Dados.

Aplicações:

* limitar acesso;
* evitar exposição;
* registrar uso;
* permitir exclusão quando aplicável.

---

# RNF014 — Compatibilidade

O sistema deverá permitir evolução para:

## Bancos

* Banco Inter;
* Itaú;
* Santander;
* Caixa;
* APIs bancárias.

## ERPs

* SCI;
* Sienge;
* Mega;
* TOTVS;
* sistemas proprietários.

---

# RNF015 — Implantação

A aplicação deverá ser preparada para execução em containers.

Arquitetura:

```
Docker

   |
   |

Backend Container

   |

Frontend Container

   |

Database Container

```

---

Pipeline:

```
Desenvolvedor

      ↓

GitHub

      ↓

GitHub Actions

      ↓

Testes

      ↓

Docker Build

      ↓

Railway

      ↓

Produção

```

---

# RNF016 — Observabilidade

Futuro:

Implementar:

* métricas;
* acompanhamento de erros;
* tempo de processamento;
* quantidade de registros.

Exemplo:

Dashboard técnico:

```
Arquivos processados:
245

Tempo médio:
2min 15s

Falhas:
3

Conciliações:
98%

```

---

# 17. Decisão Arquitetural Importante

Como Tech Lead, eu deixaria registrado:

## Não construir uma automação baseada em planilhas

Construir:

> Uma plataforma de integração financeira e contábil orientada a dados.

A planilha é apenas uma das entradas.

Essa decisão protege o projeto comercialmente.

---

# Próxima etapa

Agora temos:

✅ Visão do projeto
✅ Arquitetura
✅ UML inicial
✅ Requisitos Funcionais
✅ Requisitos Não Funcionais

O próximo documento será:

# MODELO DE DADOS CANÔNICO

Esse será um dos documentos mais importantes, porque vai definir:

* tabelas;
* campos;
* relacionamentos;
* chaves;
* regras de persistência.

Depois dele partiremos para:

1. Especificação das APIs
2. Diagramas UML detalhados
3. Plano de implantação
4. Plano de testes
5. Estratégia de desenvolvimento no Antigravity
6. Primeira Sprint de código.
