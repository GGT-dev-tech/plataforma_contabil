---
tags: [core, arquitetura, multi-tenant, rbac, plataforma-contabil, fastapi]
aliases: ["Arquitetura Base", "Core do Sistema", "Visão Geral"]
created: 2026-08-11
status: detalhado
---

# 🏛️ 01 - Visão Arquitetural e Core (Base do ERP)

## 1. Contexto e Escopo
O módulo **Core e Fundação** é a espinha dorsal de segurança e orquestração do ERP. Ele garante que um escritório de contabilidade possa gerenciar centenas de empresas sem o risco de contaminação cruzada de dados. Baseado em **FastAPI, PostgreSQL e SQLAlchemy**, este módulo implementa Multi-tenancy (por isolamento de linha - Row Level Security lógico) e Controle de Acesso Baseado em Atributos e Papéis (RBAC).

---

## 2. Diagrama de Classes e Entidades Core (PlantUML)

O modelo abaixo detalha as entidades fundamentais do sistema. A separação entre `EscritorioContabil` (Super Tenant) e `EmpresaCliente` (Tenant) é vital para o B2B2B.

```plantuml
@startuml
!theme plain
skinparam roundcorner 10
skinparam classAttributeIconSize 0

class AuditableBase {
  + uuid id
  + datetime created_at
  + datetime updated_at
  + string criado_por_usuario_id
}

class EscritorioContabil {
  + string cnpj
  + string razao_social
  + string plano_assinatura
}

class EmpresaCliente {
  + uuid escritorio_id
  + string cnpj
  + string razao_social
  + string regime_tributario
  + boolean ativo
}

class Usuario {
  + string email
  + string hashed_password
  + boolean mfa_enabled
}

class WorkspaceMember {
  + uuid usuario_id
  + uuid empresa_id
  + enum role (ADMIN, ANALISTA, CLIENTE)
}

class Permission {
  + string modulo (FISCAL, CONTABIL, FINANC)
  + string acao (CREATE, READ, UPDATE, DELETE)
}

AuditableBase <|-- EscritorioContabil
AuditableBase <|-- EmpresaCliente
AuditableBase <|-- Usuario
EscritorioContabil "1" *-- "N" EmpresaCliente : gerencia >
Usuario "1" -- "N" WorkspaceMember : possui >
EmpresaCliente "1" -- "N" WorkspaceMember : acessada por >
WorkspaceMember "N" -- "N" Permission : detém >

@enduml
```

---

## 3. Dinâmica de Autenticação e Roteamento Seguro

Para garantir o isolamento de dados sem onerar a performance, a arquitetura injeta a validação do `tenant_id` via Middleware e Dependências do FastAPI.

### Fluxo de Validação de Acesso (API Request)
```plantuml
@startuml
!theme plain
autonumber

participant "App (React)" as App
participant "FastAPI (Gateway)" as API
participant "Auth Middleware" as Auth
participant "Context Variables\n(ContextVars)" as Context
database "PostgreSQL" as DB

App -> API: GET /api/v1/financeiro/titulos\nHeaders: [Authorization: Bearer JWT, X-Tenant-ID: uuid-empresa]
API -> Auth: Intercepta Request
Auth -> Auth: Valida assinatura JWT
Auth -> DB: Valida se User.id possui WorkspaceMember para X-Tenant-ID
DB --> Auth: Retorna Role e Permissions

alt Acesso Negado
    Auth --> App: 403 Forbidden (Missing permissions)
else Acesso Permitido
    Auth -> Context: Seta `current_tenant_id` no ContextVar global do request
    Auth -> API: Libera Rota
    API -> DB: SELECT * FROM titulos WHERE tenant_id = get_current_tenant()
    DB --> API: Retorna Dados Isolados
    API --> App: 200 OK (Apenas dados da empresa)
end

@enduml
```

---

## 4. Regras de Negócio e Segurança (Robustez)

1. **ContextVars do Python:** O `tenant_id` extraído do header não é passado manualmente de função em função. Ele é salvo no `contextvars` do Python. Qualquer consulta SQLAlchemy dentro dessa thread injetará o `WHERE tenant_id = context.get()` automaticamente (usando SQLAlchemy events ou base classes).
2. **Rotação de Tokens e MFA:** O módulo Core exige suporte a Multi-Factor Authentication (MFA) obrigatório para papéis de `ADMIN` e `CONTADOR`.
3. **Audit Trail (Log de Auditoria):** Todo acesso POST, PUT ou DELETE gera um registro em uma tabela paralela de logs (ElasticSearch ou PostgreSQL JSON) anotando `usuario_id`, `tenant_id`, `endpoint`, e `payload_modificado`.

---

## 5. Especificação Técnica para Codificação

> [!tip] Estrutura de Diretórios Proposta
> ```text
> backend/app/
> ├── core/
> │   ├── auth.py          # Lógica de JWT, Hash de senha
> │   ├── security.py      # Middlewares de Tenant e validação RBAC
> │   └── database.py      # Configuração do SQLAlchemy com ContextVar injetado
> ├── models/
> │   └── base_tenant.py   # Classe abstrata TenantModelBase herdando AuditableBase
> └── api/routers/
>     └── workspaces.py    # CRUD de Empresas e Associação de Usuários
> ```

### Tabela de Permissões Básicas Iniciais
| Role | Leitura | Escrita | Deleção | Fechamento Contábil |
|---|---|---|---|---|
| **ADMIN (Escritório)** | Tudo | Tudo | Tudo | Permitido |
| **ANALISTA (Escritório)**| Tudo | Módulos Atribuídos | Proibido | Somente Leitura |
| **CLIENTE (Empresa)** | Apenas DRE Gerencial | Apenas Upload Documentos | Proibido | Proibido |

---
*Módulo detalhado para início de implementação de código.*
