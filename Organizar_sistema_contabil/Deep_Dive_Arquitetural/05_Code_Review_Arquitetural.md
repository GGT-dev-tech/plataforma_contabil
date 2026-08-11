# Code Review Arquitetural (Auditoria Principal Engineer)

Abaixo está o relatório de revisão arquitetural da **Plataforma Contábil**, focado em Escalabilidade, Segurança, Manutenibilidade e Princípios de Software (SOLID, Clean Arch, DDD). O sistema foi examinado na íntegra em busca de *anti-patterns*, vazamentos, concorrência e ineficiências.

---

## 🔴 CRITICAL

### 1. Vazamento de Dados Multi-Tenant por Design (Segurança / Autorização)
* **Onde está:** Em mais de 12 lugares diferentes, notavelmente em `api_obras.py`, `api_documentos_fiscais.py`, `api/routers/financeiro.py` (Ex: `financeiro.py:L117`).
* **Por que ocorre:** O isolamento de dados entre empresas (Tenants) não está ocorrendo a nível de Banco de Dados (Row-Level Security) ou no Repositório Base. A validação é feita *manualmente na camada de Controller (Router)*:
  ```python
  if current_user.role != Role.ADMIN and str(titulo.empresa_id) != str(current_user.empresa_id):
      raise HTTPException(status_code=403)
  ```
* **Impacto:** Altíssimo risco de vazamento de dados corporativos sigilosos. Se um novo desenvolvedor criar um endpoint e esquecer de fazer esse `if`, qualquer usuário autenticado poderá acessar ou modificar o faturamento de outra construtora (Inseguro por Padrão).
* **Como corrigir:** Implementar Row-Level Security (RLS) no PostgreSQL ou criar um `BaseRepository` que intercepte todas as consultas e force a injeção do filtro `.filter(Model.empresa_id == context.get_tenant_id())`.
* **Ganho esperado:** "Security by Default". Eliminação do risco humano de vazamento de dados entre inquilinos.

### 2. Vazamento de Memória (OOM) e Gargalo Massivo (Queries Ilimitadas)
* **Onde está:** `backend/app/contexts/matching_auditing/pipeline/runner.py` (L92-L93) e `api/routers/financeiro.py` (L176).
* **Por que ocorre:** Uso indiscriminado do método `.all()` do SQLAlchemy em tabelas sem filtros restritivos. No `runner.py`, temos as linhas:
  ```python
  parcelas = db.query(ParcelaDespesa).all()
  fornecedores = {f.id: f for f in db.query(Fornecedor).all()}
  ```
* **Impacto:** À medida que o banco de dados crescer, essa linha tentará carregar milhões de registros na RAM da aplicação (Heap). O worker vai estourar o limite de memória e ser morto pelo orquestrador (Out Of Memory - OOM Killed), paralisando o processamento do pipeline.
* **Como corrigir:** O filtro do `execucao_id` ou `empresa_id` foi esquecido nessas consultas. Além disso, consultas massivas em background devem usar paginação em lotes (`yield_per()` do SQLAlchemy).
* **Ganho esperado:** Estabilidade e escalabilidade horizontal. A aplicação não cairá aleatoriamente.

---

## 🟠 HIGH

### 3. Falta de Controle de Concorrência (Race Conditions)
* **Onde está:** `api_obras.py` (Endpoint: `PATCH /{obra_id}/avanco`).
* **Por que ocorre:** O sistema carrega o objeto do banco (`obra = db.query...`), o altera em memória e salva (`db.commit()`), sem utilizar controle de concorrência.
* **Impacto:** Concorrência Suja (Lost Update). Se o "Engenheiro A" e o "Engenheiro B" atualizarem o percentual de avanço físico de uma obra ao mesmo tempo (na fração do milissegundo), a atualização de um deles vai sobrescrever a do outro sem aviso, gerando divergência na receita reconhecida.
* **Como corrigir:** Implementar **Optimistic Locking** (Lock Otimista). Adicionar um campo `version_id` na entidade `Obra` e no schema. O SQLAlchemy incrementa e valida esse ID em cada update (ex: `__mapper_args__ = {"version_id_col": version_id}`).
* **Ganho esperado:** Integridade rígida dos dados em ambientes colaborativos.

### 4. Violações Severas de Clean Architecture e DDD (Controladores "Gordos")
* **Onde está:** `api_documentos_fiscais.py` (Endpoint: `POST /{doc_id}/calcular-retencoes`, Linha 145+).
* **Por que ocorre:** O Controller FastAPI gerencia o banco de dados, cria objetos de domínio explicitamente, comanda o commit e aciona side-effects, tudo em um método.
  ```python
  # O controlador faz a transação no banco
  titulo = TituloFinanceiro(empresa_id=doc.empresa_id, valor_nominal=resultado.valor_liquido_pagar, ...)
  db.add(titulo)
  db.commit()
  ```
* **Impacto:** O controlador conhece o banco, entende de Títulos Financeiros e orquestra a persistência. Isso torna o código impossível de ser reutilizado em outro contexto (ex: CLI ou gRPC) e difícil de testar via Testes Unitários puros (sem subir banco).
* **Como corrigir:** Criar um **Application Service** (ex: `DocumentoFiscalAppService`) ou **Use Case** (`CalcularRetencoesUseCase`) que receba o payload, e usar o padrão Unit of Work (UoW) + Repositório em vez da `Session` crua.
* **Ganho esperado:** Separação de conceitos (SoC). O controller vira um simples adaptador HTTP/JSON.

---

## 🟡 MEDIUM

### 5. Violação do Princípio da Inversão de Dependência (DIP - SOLID)
* **Onde está:** Em todo lugar que os Services são criados. Por exemplo: `api_documentos_fiscais.py:L246`
  ```python
  gerador = GeradorLancamentos(db)
  ```
  Ou no `api_documentos_fiscais.py:L34`:
  ```python
  motor_fiscal = MotorFiscal()
  ```
* **Por que ocorre:** Acoplamento excessivo (Hardcoded). Os controladores instanciam concretamente os serviços em vez de recebê-los.
* **Impacto:** Impossível realizar testes unitários usando "Mocks" (Test Doubles), pois o framework de teste não consegue substituir o `GeradorLancamentos` ou o `MotorFiscal` real.
* **Como corrigir:** Injetar as dependências pela assinatura da rota usando o framework do FastAPI (ou Dependency Injector library):
  ```python
  def gerar_lancamentos(doc_id: str, gerador: GeradorLancamentos = Depends(get_gerador_lancamentos)):
  ```
* **Ganho esperado:** Sistema 100% testável (Unit Testing friendly) e aderente ao "D" do SOLID.

### 6. Consultas de Agregação Ineficientes no Backend
* **Onde está:** `api/routers/financeiro.py` (Endpoint: `GET /dre-gerencial`, Linha 178).
* **Por que ocorre:** O controlador busca **todas** as faturas liquidadas de um ano inteiro do banco para o Python e itera a soma:
  ```python
  titulos = query.all()
  receitas = sum(t.valor_pago for t in titulos if t.tipo == TipoTitulo.RECEBER)
  ```
* **Impacto:** Alto tráfego de rede (I/O) trazendo dados desnecessários do PostgreSQL, e aumento do uso de CPU pelo Python.
* **Como corrigir:** Delegar a agregação (GROUP BY) ao SGBD, que é mil vezes mais rápido para isso:
  ```python
  receitas = db.query(func.sum(TituloFinanceiro.valor_pago)).filter(...).scalar()
  ```
* **Ganho esperado:** Relatórios (DRE) abrindo instantaneamente mesmo para clientes com centenas de milhares de lançamentos.

---

## 🟢 LOW

### 7. Falta de Paginação Real
* **Onde está:** Em todas as listagens (`api_obras.py`, `financeiro.py`).
* **Por que ocorre:** Retorna arrays usando `.limit(100)` ou `.limit(500)`.
* **Impacto:** O Front-End ou Cliente de API não consegue visualizar registros mais antigos que o limite 100. A UI sofrerá se não tiver as páginas 2, 3, etc.
* **Como corrigir:** Implementar Paginação baseada em Cursor (Limit / Offset ou Next_Token).
* **Ganho esperado:** Previsibilidade da API.

### 8. Responsabilidades Misturadas na Infraestrutura (Regras Fiscais)
* **Onde está:** No `TaxEngine` e `MotorFiscal`.
* **Por que ocorre:** As regras tributárias estão fortemente acopladas ao código atual, sendo que a legislação brasileira (ICMS, INSS, RET) sofre mudanças drásticas todos os anos.
* **Como corrigir:** Embora usem padrões como *Strategy*, as alíquotas deveriam estar isoladas num arquivo de configuração puro (YAML) ou tabela paramétrica de banco de dados para evitar "deploys" por cada pequena alteração de INSS no diário oficial.
* **Ganho esperado:** Manutenibilidade e resposta ágil à Receita Federal.
