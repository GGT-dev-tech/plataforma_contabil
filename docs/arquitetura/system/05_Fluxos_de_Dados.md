# 05 - Fluxos de Dados e Ciclo de Vida

Este documento detalha o ciclo de vida das requisições na Plataforma Contábil através de 8 cenários-chave e diagramas PlantUML.

## 1. Fluxo Completo Arquitetural (Caminho Feliz)

Demonstra a jornada de ponta a ponta desde a interface até o banco de dados.

```plantuml
@startuml
!theme plain
autonumber

actor "Usuário" as User
participant "React Component" as UI
participant "Axios API Client" as Axios
participant "FastAPI (Router)" as Router
participant "Service / Use Case" as Service
participant "Repository" as Repo
database "PostgreSQL (SQLAlchemy)" as DB

User -> UI: Clica em "Salvar Empresa"
activate UI
UI -> Axios: POST /api/v1/workspaces {data}
activate Axios
Axios -> Router: HTTP POST (com Bearer Token e X-Tenant-ID)
activate Router
Router -> Service: create_workspace(DTO)
activate Service
Service -> Repo: save(EmpresaModel)
activate Repo
Repo -> DB: INSERT INTO empresa (...)
activate DB
DB --> Repo: Rows affected
deactivate DB
Repo --> Service: EmpresaModel (com ID)
deactivate Repo
Service --> Router: Domain DTO
deactivate Service
Router --> Axios: HTTP 201 Created (JSON)
deactivate Router
Axios --> UI: Response Data
deactivate Axios
UI --> User: "Empresa salva com sucesso"
deactivate UI

@enduml
```

## 2. Fluxo de Autenticação (OAuth2)

```plantuml
@startuml
!theme plain
autonumber

actor "Usuário" as User
participant "React (LoginPage)" as UI
participant "FastAPI (/login)" as API
database "PostgreSQL" as DB

User -> UI: Insere Email / Senha
UI -> API: POST /api/v1/auth/login
API -> DB: SELECT * FROM usuario WHERE email = ?
DB --> API: Record
API -> API: Valida hash bcrypt(senha)
alt Senha Incorreta
    API --> UI: HTTP 401 Unauthorized
    UI --> User: Exibe Erro
else Senha Correta
    API -> API: Gera JWT Token (com roles e sub)
    API --> UI: HTTP 200 OK { token }
    UI -> UI: localStorage.setItem('@App:token')
    UI -> UI: AuthContext atualiza estado
    UI -> User: Redireciona para /dashboard
end
@enduml
```

## 3. Fluxo de Inicialização da Aplicação

```plantuml
@startuml
!theme plain
autonumber

participant "Docker Compose / Railway" as Infra
participant "Container Backend" as API
database "PostgreSQL" as DB
participant "Uvicorn (FastAPI)" as Server

Infra -> API: Inicia Container
activate API
API -> API: Executa scripts de inicialização
API -> DB: alembic upgrade head
activate DB
DB --> API: Migrations Aplicadas
deactivate DB
API -> API: python scripts/create_first_user.py (Seed inicial)
API -> Server: Inicia Uvicorn (0.0.0.0:8000)
activate Server
Server --> Infra: Aplicação Pronta
@enduml
```

## 4. Fluxo de Tratamento de Exceções

A aplicação usa *Exception Handlers* globais no FastAPI para interceptar erros da camada de domínio.

```plantuml
@startuml
!theme plain
autonumber

participant "Service" as Service
participant "FastAPI" as API
participant "GlobalExceptionHandler" as ErrorHandler
participant "Axios (Frontend)" as Axios
participant "React UI" as UI

Service -> Service: Detecta violação de regra (ex: Saldo Negativo)
Service -> API: raise DomainException("Saldo Inválido")
API -> ErrorHandler: Captura DomainException
ErrorHandler -> API: Converte para HTTP 400 ou 422 { "detail": "Saldo Inválido" }
API --> Axios: HTTP 400 Bad Request
Axios -> Axios: Intercepta Erro
Axios --> UI: Rejeita Promise(Error)
UI -> UI: setState({ error: "Saldo Inválido" })
UI --> User: Toast: "Erro: Saldo Inválido"
@enduml
```

## 5. Fluxos de CRUD (Create, Update, Delete, Query)

### Criação (Create)
O POST valida o Pydantic DTO → Repository instancia `Model(...)` → `session.add(model)` → `session.commit()` → `session.refresh(model)`.

### Atualização (Update)
O PUT/PATCH/POST valida DTO → Repository busca a entidade `session.get(id)` → Altera propriedades do modelo retornado → `session.commit()`.

### Exclusão (Delete)
O DELETE (ou Soft Delete) → Repository busca `session.get(id)` → `session.delete(model)` (ou `model.deleted = True`) → `session.commit()`. 

### Consultas (Queries / Read)
O GET → Repository executa `session.query().filter().all()` → Lista de models é mapeada automaticamente para List[Pydantic_Schema] pelo FastAPI (graças a `from_attributes=True` ou `orm_mode`).

*Fim da Documentação Arquitetural.*
