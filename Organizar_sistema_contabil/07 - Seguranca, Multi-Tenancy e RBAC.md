# 07 - Segurança, Multi-Tenancy e RBAC

## 1. O Desafio da Contabilidade Escalonável
Sistemas contábeis SaaS (Software as a Service) enfrentam um desafio crítico de segurança: processar os dados financeiros sigilosos de dezenas ou centenas de clientes (Construtoras) no mesmo banco de dados sem que ocorram vazamentos de informações cruzadas. Um relatório gerado para o cliente "A" jamais pode expor os lançamentos do cliente "B". 

Para mitigar este risco com garantia algorítmica, o módulo **Identity & Tenant** é responsável por enjaular toda e qualquer transação dentro do seu respectivo `workspace_id`.

## 2. Padrões Multi-Tenancy
A Plataforma utiliza a abordagem **Row-Level Tenancy (Pool Model)**, onde os dados de todos os clientes residem na mesma base, mas cada registro possui uma chave estrangeira (FK) apontando para o seu `Workspace` (Inquilino). 

### Proteção no Nível de Código (Filtro Global)
No FastAPI com SQLAlchemy, o acesso aos dados nunca é realizado de forma "livre" via repositório base. Os filtros de inquilino (Tenant) são injetados automaticamente pela Sessão da Requisição.
1. O usuário se autentica com e-mail/senha.
2. O sistema emite um token JWT que carrega o(s) `workspace_id` autorizados.
3. A requisição HTTP intercepta o Token.
4. Qualquer `SELECT` ou `UPDATE` feito pela aplicação automaticamente concatena um `.where(entity.workspace_id == id)`.

## 3. RBAC (Role-Based Access Control)
As permissões são hierárquicas e estritamente funcionais. Cada ação que modifica o banco de dados depende do escopo de atuação do usuário.

Os papéis padrão arquitetados:
- **Admin da Plataforma:** Acesso geral de configuração (não acessa balancetes dos clientes sem ser convidado).
- **Gestor Contábil:** Autoridade máxima em um Workspace. Pode criar, reverter conciliações, fechar períodos e convidar membros.
- **Analista Contábil:** Consegue rodar pipelines, auditar falhas de robôs e visualizar extratos. Não consegue aprovar fechamentos definitivos.
- **Auditor:** Possui acesso estritamente _Read-Only_ (somente leitura).

## 4. Auditoria Imutável 
Quaisquer alterações manuais de um fechamento financeiro, criação de provisão e correções (Ajustes a Débito/Crédito) deixam rastros imutáveis na tabela `AuditLog`.
A tabela armazena:
- `user_id`
- `action` (CREATE, UPDATE, CANCEL)
- `entity_type` (ex: LANCAMENTO)
- `entity_id`
- `old_state` (JSON)
- `new_state` (JSON)
- `timestamp`

Essas métricas são utilizadas no **Dashboard Operacional** para provar, caso necessário, quem reabriu o caixa de janeiro da construtora X.
