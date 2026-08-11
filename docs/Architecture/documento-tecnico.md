Continuando. Agora vamos para o documento que transforma a arquitetura em **plano real de construção do software**.

A partir daqui vou assumir o papel de **Tech Lead responsável pela condução técnica do desenvolvimento**, considerando sua stack:

* Backend: Python
* API: FastAPI
* Frontend: React + TypeScript
* Banco local inicial: SQLite
* Banco produção: PostgreSQL
* Containers: Docker
* Deploy: Railway
* CI/CD: GitHub Actions
* Ambiente de desenvolvimento assistido: Antigravity

---

# DOCUMENTO TÉCNICO 3

# Arquitetura de Software e Plano de Desenvolvimento MVP

## 1. Visão Arquitetural

O sistema será desenvolvido seguindo uma arquitetura modular, preparada para crescimento.

A recomendação é utilizar uma arquitetura baseada em:

## Modular Monolith inicialmente

Motivo:

Não devemos iniciar com microsserviços.

Para um projeto desse tamanho, microsserviços aumentariam:

* custo de desenvolvimento;
* complexidade;
* dificuldade de manutenção;
* necessidade de infraestrutura.

A arquitetura ideal inicialmente:

```
                    FRONTEND

              React + TypeScript

                       |
                       |
                       v


                    BACKEND API

                    FastAPI


                       |
       ----------------------------------

       |                |               |

       v                v               v


  Ingestão        Processamento     Relatórios

  Arquivos        Conciliação       Exportação


       |
       |
       v


       BANCO DE DADOS

       PostgreSQL

```

---

# 2. Estrutura de Projeto Backend

Sugestão:

```
backend/

├── app/

│   ├── main.py

│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│
│   ├── database/
│   │   ├── connection.py
│   │   ├── models.py
│
│   ├── modules/

│   │
│   │── importacao/
│   │     ├── routes.py
│   │     ├── services.py
│   │     ├── parsers/
│   │
│   │
│   │── financeiro/
│   │     ├── models.py
│   │     ├── services.py
│   │
│   │
│   │── bancario/
│   │
│   │
│   │── contabil/
│   │
│   │── conciliacao/
│   │     ├── engine.py
│   │     ├── rules.py
│   │
│   │── relatorios/
│
│   ├── tests/
│
├── Dockerfile
├── requirements.txt

```

---

# 3. Responsabilidade dos Módulos

## 3.1 Módulo Importação

Responsável por receber arquivos.

Exemplo:

```
POST /importacoes/upload

```

Entrada:

```
Despesas.xlsx

Extrato.xlsx

Razão.xlsx

```

Processo:

1. Receber arquivo;
2. Armazenar original;
3. Identificar origem;
4. Encaminhar para parser correto.

---

# 3.2 Camada Parser

Esse é um ponto crítico.

Não devemos criar:

```
parser_excel.py

```

genérico demais.

O correto:

```
parsers/

├── banco_inter_parser.py

├── sci_razao_parser.py

├── financeiro_parser.py

```

Porque cada fornecedor possui sua "assinatura".

---

Exemplo:

Banco Inter:

Recebe:

```
1 de Junho de 2026
Pix enviado
-R$ 1.392,20

```

Entrega:

```json
{
 "data":"2026-06-01",
 "tipo":"PIX_ENVIADO",
 "valor":1392.20
}

```

---

SCI:

Recebe:

```
Chave 40070

Crédito 132.500,00

```

Entrega:

```json
{
 "chave":"40070",
 "credito":132500.00
}

```

---

# 4. Camada de Normalização

Essa camada é fundamental.

Ela transforma:

"mundos diferentes"

em:

"modelo único".

---

Exemplo:

Banco:

```
PIX enviado UP ESQUADRIAS

```

Financeiro:

```
Fornecedor:
UP ESQUADRIAS

```

Contabilidade:

```
Compra a Vista UP ESQUADRIAS

```

Normalização:

```
Fornecedor Canonico:

UP ESQUADRIAS


```

---

# 5. Motor de Conciliação

Esse é o diferencial da solução.

Estrutura:

```
conciliacao/

├── engine.py

├── scorer.py

├── rules.py

├── validators.py

```

---

Fluxo:

```
Parcela Despesa

        |
        |
        v


Busca movimentos candidatos


        |
        |
        v


Calcula score


        |
        |
        v


Decisão


```

---

# 6. Algoritmo Inicial de Matching

Versão MVP:

## Regra 1 - Valor

Peso:

40 pontos

Exemplo:

Despesa:

```
R$ 1.392,20

```

Banco:

```
R$ 1.392,20

```

Resultado:

+40

---

## Regra 2 - Data

Peso:

20 pontos

Aceitar:

```
Data pagamento

até ±1 dia útil

```

Motivo:

Compensações bancárias.

---

## Regra 3 - Fornecedor

Peso:

30 pontos

Biblioteca:

```
RapidFuzz

```

Exemplo:

Banco:

```
UP ESQUADRIA

```

Financeiro:

```
UP ESQUADRIAS LTDA

```

Similaridade:

95%

---

## Regra 4 - Forma Pagamento

Peso:

10 pontos

PIX:

PIX

Boleto:

Boleto

---

Resultado:

```
Score >= 90

CONCILIADO


70-89

REVISÃO


<70

DIVERGENTE

```

---

# 7. Frontend React

Estrutura:

```
frontend/


src/

├── pages/

│
├── Dashboard/

├── Importacao/

├── Conciliacao/

├── Divergencias/


├── components/

├── services/

├── hooks/

```

---

# 8. Telas MVP

## Tela 1 - Dashboard

Mostrar:

```
Período:

Junho/2026


Arquivos processados:

3


Movimentos:

523


Conciliados:

487


Pendentes:

36

```

---

## Tela 2 - Importação

Fluxo:

```
Selecionar arquivo

        |

Validar

        |

Processar

        |

Resultado

```

---

## Tela 3 - Conciliação

Tabela:

| Fornecedor    | Valor      | Status   |
| ------------- | ---------- | -------- |
| UP ESQUADRIAS | R$ 132.500 | OK       |
| BH MATERIAIS  | R$ 3.690   | OK       |
| Fornecedor X  | R$ 850     | Pendente |

---

## Tela 4 - Divergências

Exemplo:

```
Tipo:

Banco sem Financeiro


Valor:

R$ 2.500


Histórico:

PIX recebido


Ação:

Analisar

```

---

# 9. Banco de Dados Inicial

Durante desenvolvimento:

SQLite

Arquivo:

```
database.sqlite

```

Vantagens:

* rápido;
* simples;
* sem configuração.

Produção:

PostgreSQL Railway.

Migração:

SQLAlchemy + Alembic.

---

# 10. Docker

Estrutura:

```
docker-compose.yml


services:


 api:

   build:

   ports:

     8000:8000



 frontend:

   build:

   ports:

     3000:3000



 postgres:

   image:

     postgres

```

---

# 11. CI/CD

GitHub Actions:

Arquivo:

```
.github/workflows/deploy.yml

```

Pipeline:

```
Commit

 |

Testes

 |

Build Docker

 |

Deploy Railway

 |

Produção

```

---

# 12. Desenvolvimento em Antigravity

Estratégia recomendada:

Não pedir:

"crie o sistema inteiro".

Isso gera código inconsistente.

O correto:

Dividir por entregáveis.

Exemplo:

## Sprint 1

Prompt:

"Crie estrutura FastAPI seguindo arquitetura modular com módulo importação."

Depois:

"Crie parser Banco Inter seguindo documentação."

Depois:

"Crie testes unitários."

---

# 13. Roadmap MVP

## Sprint 1 - Fundação

Prazo estimado:

5 dias

Entrega:

✅ Repositório Git
✅ Docker
✅ FastAPI funcionando
✅ Banco configurado
✅ Modelo inicial

---

## Sprint 2 - Importação

5 a 7 dias

Entrega:

✅ Upload Excel
✅ Armazenamento original
✅ Parser Despesas

---

## Sprint 3 - Parsers Bancário e Contábil

7 a 10 dias

Entrega:

✅ Banco Inter
✅ SCI
✅ Modelo canônico

---

## Sprint 4 - Motor Conciliação

10 dias

Entrega:

✅ Matching
✅ Score
✅ Regras

---

## Sprint 5 - Interface

10 dias

Entrega:

✅ Dashboard
✅ Relatórios
✅ Divergências

---

# 14. Ponto Comercial Importante para o Cliente

A proposta não deve ser vendida como:

"um sistema que importa planilhas".

Isso é pequeno.

A proposta correta:

> "Uma camada inteligente de integração financeira e contábil capaz de conectar diferentes ERPs de construtoras, padronizar informações e automatizar a conciliação entre financeiro, banco e contabilidade."

Essa frase posiciona o projeto como uma solução estratégica.

---

# 15. Próximo Documento

Agora a próxima etapa técnica é criar:

# DOCUMENTO 4

## Plano de Implementação e Backlog Técnico

Onde vamos definir:

* Ordem exata de desenvolvimento;
* User Stories;
* Tasks para Antigravity;
* Estrutura inicial do GitHub;
* Primeiros prompts de programação;
* Critérios de aceite;
* Testes necessários.

Esse será o documento que vai transformar a arquitetura em código.
