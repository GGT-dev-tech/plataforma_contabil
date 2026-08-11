# 04 - Banco de Dados e Modelagem (SQLAlchemy)

Este documento documenta o esquema relacional atualizado do sistema Plataforma Contábil, incluindo entidades legadas e as novas introduzidas na refatoração da Arquitetura V2.

## 1. Stack e Ferramentas

* **SGBD:** PostgreSQL 16
* **ORM:** SQLAlchemy 2.0 (Estilo Declarativo)
* **Controle de Migrações:** Alembic
* **Padrões de Design:**
  * UUID4 como chave primária para todas as entidades (segurança e distribuição).
  * Timestamps automáticos (`created_at`, `updated_at`).
  * `tenant_id` (Empresa) em quase todas as entidades transacionais (para suportar Multi-Tenancy nativo).

## 2. Divisão Lógica do Domínio (Módulos)

O banco está particionado logicamente através de arquivos Python em `backend/app/models/`, refletindo bounded contexts distintos.

### Domínio de Identidade e Sistema
* **Usuario:** Credenciais e Controle de Acesso (Role: ADMIN, etc.).
* **Empresa / EmpresaFiscal:** O Tenant raiz. EmpresaFiscal herda configurações de Regime Tributário (Lucro Real, Presumido, Simples).
* **ExecucaoPipeline / StagingRegistro:** Controle de jobs de importação (extratos, relatórios).

### Domínio Fiscal e Obras
* **Obra / Subempreiteiro:** Centros de custo isolados com tributação própria (ex: RET - Regime Especial de Tributação).
* **DocumentoFiscalV2:** Notas Fiscais, Faturas. Substitui o legado `DocumentoFiscal`.
* **ParcelaDocumentoFiscal:** Desdobramento de NFs.
* **ApuracaoFiscal / DetalheImposto:** Registro de impostos calculados (PIS, COFINS, ISS, INSS).

### Domínio Financeiro (Tesouraria)
* **TituloFinanceiro:** Títulos a pagar / a receber.
* **MovimentacaoFinanceira:** Extratos bancários reais (conciliados).
* **ConciliacaoFinanceira:** Relacionamento NxM entre Títulos, Documentos e Movimentações.

### Domínio Contábil (Ledger)
* **PlanoDeContas:** Árvore hierárquica contábil.
* **PeriodoContabil:** Controle de fechamento de competências (Aberto/Fechado).
* **LancamentoCabecalho:** O diário contábil principal.
* **PartidaItem:** Partidas dobradas (Débito e Crédito associadas a um Lançamento).

## 3. Diagrama de Entidade-Relacionamento (ER / UML)

Abaixo o diagrama de relacionamento das entidades **foco da Arquitetura V2**, excluindo o legado transiente para melhor visibilidade do core business atual:

```plantuml
@startuml
!theme plain
skinparam roundcorner 5
skinparam classAttributeIconSize 0
skinparam linetype ortho

hide methods

entity "EmpresaFiscal (Tenant)" as Empresa {
  * id : UUID <<PK>>
  --
  cnpj : String
  regime_tributario : Enum
}

entity "Usuario" as Usuario {
  * id : UUID <<PK>>
  --
  email : String
  role : Enum
}

entity "Obra" as Obra {
  * id : UUID <<PK>>
  * tenant_id : UUID <<FK>>
  --
  cei_cno : String
  status : Enum
}

entity "PlanoDeContas" as Conta {
  * id : UUID <<PK>>
  * tenant_id : UUID <<FK>>
  --
  codigo : String
  natureza : Enum
}

entity "DocumentoFiscalV2" as DocFiscal {
  * id : UUID <<PK>>
  * tenant_id : UUID <<FK>>
  * obra_id : UUID <<FK>>
  --
  numero : String
  valor_total : Decimal
  data_emissao : Date
}

entity "ApuracaoFiscal" as Imposto {
  * id : UUID <<PK>>
  * documento_id : UUID <<FK>>
  --
  tipo_imposto : Enum
  valor : Decimal
}

entity "TituloFinanceiro" as Titulo {
  * id : UUID <<PK>>
  * tenant_id : UUID <<FK>>
  * documento_id : UUID <<FK>>
  --
  status : Enum
  valor_liquido : Decimal
  data_vencimento : Date
}

entity "LancamentoCabecalho" as Lancamento {
  * id : UUID <<PK>>
  * tenant_id : UUID <<FK>>
  * documento_id : UUID <<FK>> (opcional)
  --
  data_lancamento : Date
  origem : Enum
}

entity "PartidaItem" as Partida {
  * id : UUID <<PK>>
  * lancamento_id : UUID <<FK>>
  * conta_id : UUID <<FK>>
  --
  tipo : Enum (DEBITO/CREDITO)
  valor : Decimal
}

Empresa "1" -- "0..*" Obra : possui
Empresa "1" -- "0..*" DocFiscal : registra
Obra "1" -- "0..*" DocFiscal : agrupa

DocFiscal "1" -- "0..*" Imposto : gera
DocFiscal "1" -- "0..*" Titulo : desdobra em

DocFiscal "1" -- "0..1" Lancamento : origina
Lancamento "1" -- "2..*" Partida : contem
Conta "1" -- "0..*" Partida : recebe

@enduml
```

## 4. Fluxo de Migrações (Alembic)

A evolução do schema é tratada *exclusivamente* via Alembic:

1. Modela-se a classe herdeira de `Base` em `backend/app/models/`.
2. O desenvolvedor gera o script: `alembic revision --autogenerate -m "nome"`.
3. O script (`backend/alembic/versions/`) contém funções `upgrade()` e `downgrade()`.
4. Em ambiente produtivo, o deploy do Railway dispara `alembic upgrade head` como primeira etapa. Nenhuma modificação DDL direta no banco é permitida.
