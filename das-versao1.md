Vou estruturar o **Documento de Arquitetura de Software (DAS)** em um formato profissional, como seria apresentado em uma reunião técnica com cliente, equipe de desenvolvimento e stakeholders. Este documento será a base para os próximos artefatos: UML, DER, requisitos funcionais/não funcionais, APIs e plano de desenvolvimento.

# Documento de Arquitetura de Software (DAS)

## Sistema de Automação de Conciliação Financeira e Contábil para Empresas do Segmento de Construção Civil

**Versão:** 1.0
**Documento:** Documento de Arquitetura de Software (DAS)
**Status:** Proposta Arquitetural Inicial
**Responsável Técnico:** Arquitetura de Software / Desenvolvimento de Sistemas
**Data:** 2026

---

# 1. Introdução

## 1.1 Objetivo do Documento

Este documento apresenta a arquitetura proposta para desenvolvimento de uma plataforma de automação de processos financeiros e contábeis voltada inicialmente para escritórios de contabilidade que atendem empresas do segmento de construção civil.

A solução tem como objetivo automatizar o processo atualmente realizado de forma manual envolvendo:

* Extração de dados provenientes de diferentes ERPs utilizados pelas construtoras;
* Padronização das informações financeiras e contábeis;
* Conciliação entre dados financeiros, bancários e contábeis;
* Identificação automática de divergências;
* Geração de relatórios gerenciais e operacionais.

---

# 2. Contexto do Negócio

## 2.1 Cenário Atual

Empresas de construção civil utilizam diferentes sistemas de gestão financeira e administrativa.

Cada construtora possui características próprias:

* ERP próprio;
* Estrutura de cadastro diferente;
* Layouts de exportação distintos;
* Diferentes padrões de fornecedores;
* Diferentes formas de controle financeiro.

O escritório contábil recebe essas informações e precisa realizar manualmente:

* Importação dos dados;
* Ajustes de formato;
* Conferência com extratos bancários;
* Comparação com lançamentos contábeis;
* Identificação de inconsistências.

Esse processo gera:

* Alto consumo de horas operacionais;
* Dependência de conhecimento manual;
* Risco de erros;
* Baixa escalabilidade.

---

# 3. Objetivo da Solução

Criar uma plataforma intermediária capaz de atuar como uma camada de integração entre diferentes sistemas de origem e o ambiente contábil.

A solução deverá:

1. Receber arquivos financeiros e contábeis;
2. Interpretar diferentes layouts;
3. Converter os dados para um modelo único;
4. Aplicar regras de validação;
5. Realizar conciliações automáticas;
6. Apresentar divergências para análise humana;
7. Gerar relatórios auditáveis.

---

# 4. Visão Arquitetural Geral

A arquitetura será baseada no modelo:

## ETL + Modelo Canônico + Motor de Regras + Aplicação Web

Fluxo macro:

```
Sistemas Originais

ERP Construtora A
ERP Construtora B
ERP Construtora C
Sistema Contábil SCI
Extratos Bancários

          |
          v

Camada de Ingestão

Upload/API
Validação
Identificação do Layout

          |
          v

Camada Staging

Dados originais preservados

          |
          v

Camada de Normalização

Limpeza
Conversão
Padronização

          |
          v

Modelo Canônico

Dados estruturados

          |
          v

Motor de Conciliação

Matching
Score
Regras

          |
          v

Aplicação Web

Dashboard
Relatórios
Auditoria
Aprovação Manual
```

---

# 5. Princípios Arquiteturais

## 5.1 Independência dos Sistemas de Origem

A solução não deverá depender de um único ERP.

Cada sistema externo deverá possuir um adaptador específico responsável pela conversão dos dados.

Exemplo:

```
ERP Construtora A
        |
        v
   Parser ERP A
        |
        v
Modelo Canônico


ERP Construtora B
        |
        v
   Parser ERP B
        |
        v
Modelo Canônico
```

---

## 5.2 Separação entre Dados Originais e Dados Tratados

A arquitetura deverá preservar os dados originais para auditoria.

Camadas:

### Raw Layer

Dados exatamente como recebidos.

Exemplo:

```
arquivo_original.xlsx
arquivo_original.pdf
```

---

### Staging Layer

Dados extraídos e parcialmente estruturados.

---

### Canonical Layer

Dados prontos para utilização pelo sistema.

---

# 6. Arquitetura de Aplicação

## 6.1 Modelo Arquitetural

Arquitetura baseada em serviços:

```
Frontend React

       |

API Backend FastAPI

       |

Serviços de Domínio

       |

Banco PostgreSQL
```

---

# 7. Componentes do Sistema

# 7.1 Frontend Web

## Tecnologia

* React
* TypeScript
* Vite
* Tailwind CSS

## Responsabilidades

* Login;
* Upload de arquivos;
* Visualização dos processos;
* Dashboard;
* Relatórios;
* Aprovação de divergências.

---

# 7.2 Backend API

## Tecnologia

Python + FastAPI

Responsável por:

* Expor APIs;
* Controlar regras;
* Gerenciar autenticação;
* Orquestrar processos.

---

# 7.3 Serviço de Processamento de Arquivos

Responsável por:

* Ler Excel;
* Ler PDF;
* Validar estruturas;
* Executar parsers.

Bibliotecas:

* pandas;
* openpyxl;
* pdfplumber;
* pypdf.

---

# 7.4 Motor de Conciliação

Componente principal da solução.

Responsabilidades:

* Comparação de registros;
* Aplicação de regras;
* Cálculo de score;
* Identificação de divergências.

Exemplo:

```
Fornecedor compatível      +25 pontos
Valor compatível           +40 pontos
Data compatível             +20 pontos
Nota fiscal compatível      +10 pontos
Projeto compatível          +5 pontos

Resultado:

>=90%
Match automático

70%-89%
Revisão manual

<70%
Divergência
```

---

# 7.5 Banco de Dados

## Ambiente Desenvolvimento

SQLite

## Ambiente Produção

PostgreSQL

Motivos:

* Segurança;
* Escalabilidade;
* Controle transacional;
* Auditoria.

---

# 8. Modelo Inicial de Domínio

Principais entidades:

## Empresa

Representa:

* Escritório contábil;
* Cliente;
* SPE.

---

## Projeto

Representa:

* Obra;
* Empreendimento.

---

## Fornecedor

Representa:

* Prestadores;
* Empresas;
* Pessoas físicas.

---

## Despesa

Representa o compromisso financeiro.

Origem:

Sistema financeiro.

---

## Parcela

Representa a liquidação financeira.

---

## Movimentação Bancária

Representa o ocorrido no banco.

Origem:

Extrato.

---

## Lançamento Contábil

Representa o registro oficial.

Origem:

SCI ou outro ERP.

---

# 9. Fluxo de Processamento

## 9.1 Importação

Usuário envia:

```
Despesas.xlsx

Extrato.xlsx

Razão.xlsx
```

Sistema:

1. Identifica arquivo;
2. Valida formato;
3. Executa parser;
4. Armazena dados originais.

---

# 9.2 Normalização

Exemplo:

Fornecedor:

Antes:

```
Bh Materiais de Construcao LTDA
```

Depois:

```
BH MATERIAIS CONSTRUCAO
```

---

Valor:

Antes:

```
-R$ 33.500,00
```

Depois:

```
-33500.00
```

---

# 9.3 Conciliação

Processos:

## Financeiro x Banco

Verifica:

* Pagamentos realizados;
* Valores;
* Datas;
* Fornecedores.

---

## Banco x Contabilidade

Verifica:

* Existência do lançamento;
* Valores;
* Histórico.

---

## Financeiro x Contabilidade

Verifica:

* Classificação;
* Projeto;
* Categoria.

---

# 10. Segurança

## Autenticação

Implementação prevista:

* JWT;
* Controle de sessão;
* Perfis de acesso.

---

## Controle de acesso

Perfis:

Administrador

Analista Contábil

Cliente Construtora

Auditor

---

## Auditoria

Registrar:

* Usuário;
* Data;
* Arquivo;
* Alteração;
* Aprovação.

---

# 11. Infraestrutura

## Containerização

Docker.

Ambiente:

```
Frontend Container

Backend Container

Database Container
```

---

## Deploy

Infraestrutura inicial:

Railway.

Pipeline:

```
GitHub

   |

GitHub Actions

   |

Docker Build

   |

Deploy Railway
```

---

# 12. Observabilidade

Implementação futura:

* Logs estruturados;
* Monitoramento de erros;
* Métricas;
* Histórico de processamento.

---

# 13. Escalabilidade Futura

A arquitetura permite evolução para:

* Integração via API com ERPs;
* Open Banking;
* Inteligência Artificial para classificação;
* Machine Learning para matching;
* Dashboard executivo;
* Multiempresa/multicontabilidade.

---

# 14. Decisões Técnicas

| Item                  | Decisão                    |
| --------------------- | -------------------------- |
| Backend               | Python + FastAPI           |
| Frontend              | React + TypeScript         |
| Banco Produção        | PostgreSQL                 |
| Desenvolvimento Local | SQLite                     |
| Container             | Docker                     |
| CI/CD                 | GitHub Actions             |
| Deploy Inicial        | Railway                    |
| Arquitetura           | Serviços + Modelo Canônico |
| Integração            | Adaptadores por ERP        |

---

# 15. Próximos Documentos Técnicos

Após aprovação deste DAS deverão ser elaborados:

1. Documento de Requisitos Funcionais;
2. Documento de Requisitos Não Funcionais;
3. Modelo Entidade-Relacionamento;
4. Modelo de Dados Canônico;
5. Diagramas UML;
6. Especificação das APIs;
7. Plano de Testes;
8. Plano de Implantação;
9. Estratégia de Monitoramento;
10. Manual Operacional.

---

# Conclusão

A arquitetura proposta foi desenhada para resolver o problema imediato de conciliação financeira e contábil da operação analisada, mas mantendo uma estrutura escalável capaz de atender diferentes construtoras, ERPs e escritórios contábeis.

O principal diferencial arquitetural é a criação de uma camada intermediária independente dos sistemas de origem, permitindo padronizar informações heterogêneas em um único modelo confiável para automação, auditoria e tomada de decisão.

Esse DAS agora passa a ser o **documento base do projeto**. O próximo passo técnico recomendado é criar o **Modelo de Dados Canônico + DER (Modelo Entidade-Relacionamento)**, porque ele vai definir exatamente como o PostgreSQL será construído e como os três mundos (Despesas, Banco e Razão) vão se relacionar.
