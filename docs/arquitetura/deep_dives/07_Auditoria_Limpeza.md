# Auditoria de Manutenção e Limpeza (Garbage Collection Arquitetural) 🧹

Nesta auditoria, atuei como Senior Software Engineer investigando a "ferrugem" e o acúmulo de código morto no projeto após sucessivas refatorações. 

Abaixo encontra-se o mapeamento de arquivos órfãos, duplicados e legados perigosos, baseados em referências explícitas no código (grep/imports).

---

## 1. Relatório Completo de Auditoria

### 1.1 Frontend (React)

#### A. Página de Login Duplicada
* **Arquivo:** `frontend/src/pages/Login.tsx`
* **Tipo:** Componente React (Página).
* **Status:** 🔴 **Não utilizado / Abandonado**.
* **Evidência:** O React Router (`app/router.tsx`) aponta exclusivamente para `import { LoginPage } from '../pages/auth/LoginPage';`. O arquivo antigo não tem nenhum `import` em todo o projeto.
* **Risco da Remoção:** Baixo.
* **Ação Recomendada:** Remover com segurança.

#### B. Módulo de Autenticação Legado
* **Localização:** Pasta `frontend/src/auth/` (`authService.ts`, `AuthProvider.tsx`, `authTypes.ts`, `permissions.ts`).
* **Tipo:** Contexto e Helpers TypeScript.
* **Status:** 🟡 **Parcialmente utilizado (com alto grau de substituição)**.
* **Evidência:** O sistema hoje utiliza o arquivo `frontend/src/contexts/AuthContext.tsx` para prover estado. O `AuthProvider.tsx` legado só é importado dentro dessa mesma pasta morta. 
  * *Exceção:* O arquivo `ProtectedRoute.tsx` ainda mora aqui e é usado pelo `router.tsx`.
* **Risco da Remoção:** Médio (se apagar sem mover a exceção).
* **Ação Recomendada:** Refatorar antes da remoção. Mover `ProtectedRoute.tsx` para `components/layout/` e então apagar o restante da pasta `auth/`.

---

### 1.2 Backend (FastAPI / Serviços)

#### C. Parsers Clássicos Órfãos
* **Localização:** Pasta `backend/app/parsers/` inteira.
* **Tipo:** Lógica de Extração de Dados (Excel/PDF).
* **Status:** 🔴 **Substituído / Órfão**.
* **Evidência:** Durante a refatoração para Vertical Slice, esses parsers migraram para `backend/app/contexts/staging_ingestion/parsers/`. Ao varrer o código, nada fora de `app/parsers` importa qualquer função de lá. O fluxo ativo utiliza o `factory.py` no módulo de Staging.
* **Risco da Remoção:** Baixo.
* **Ação Recomendada:** Remover com segurança.

#### D. Endpoints de Execução Abandonados
* **Arquivo:** `backend/app/api/routers/executions.py`
* **Tipo:** FastAPI Router.
* **Status:** 🔴 **Abandonado / Duplicado**.
* **Evidência:** Não há referência desse arquivo no `main.py` (linha 79). A API consumida em produção é importada de `from app.contexts.staging_ingestion.api_executions import router as staging_executions_router`.
* **Risco da Remoção:** Baixo.
* **Ação Recomendada:** Remover com segurança.

#### E. O Pântano Legado (Modelos Conflitantes de Domínio)
* **Arquivo:** `backend/app/models/domain.py` (Modelos ORM de Financeiro e Contabilidade).
* **Status:** 🟠 **Parcialmente utilizado e Conflitante**.
* **Evidência:** Modelos incríveis e modernos foram criados (Ex: `ledger.py` [LancamentoCabecalho], `financeiro.py` [TituloFinanceiro], `tesouraria.py` [TesourariaConta]). No entanto, no antigo `domain.py`, ainda residem as tabelas antigas (`LancamentoContabil`, `ParcelaDespesa`, `MovimentacaoBancaria`, `DocumentoFiscal` V1).
  * *O Problema:* O motor de conciliação assíncrono (`contexts/matching_auditing/engine/core.py:L234`) **AINDA IMPORTA** e pesquisa ativamente no banco usando o legado `ParcelaDespesa`.
* **Risco da Remoção:** Crítico. Apagar esses models agora ou gerar migração de `DROP TABLE` fará a pipeline de auditoria crashear imediatamente na produção.
* **Ação Recomendada:** Manter temporariamente, mas sinalizar para Refatoração Profunda.

---

## 2. Plano de Remoção Segura (Checklist)

Se você aprovar esta faxina, executaremos o plano abaixo, camada por camada.

### Etapa 1: Arquivos que podem ser removidos imediatamente (Lixo Limpo)
- [ ] `rm frontend/src/pages/Login.tsx` (Página duplicada)
- [ ] `rm frontend/src/auth/permissions.ts` (Sem uso)
- [ ] `rm backend/app/api/routers/executions.py` (Rota não conectada)
- [ ] `rm -rf backend/app/parsers/` (Pasta obsoleta, substituída pela Staging)

### Etapa 2: Arquivos que precisam de substituição/movimentação (Baixo Risco)
- [ ] Mover `frontend/src/auth/ProtectedRoute.tsx` para `frontend/src/components/layout/`.
- [ ] Atualizar os imports no `app/router.tsx` para o novo caminho do ProtectedRoute.
- [ ] Apagar o resto da pasta `frontend/src/auth/` (`authService.ts`, `AuthProvider.tsx`).

### Etapa 3: Arquivos que precisam de refatoração pesada antes da exclusão (Alto Risco)
- O módulo de Auditoria (`matching_auditing/engine/rules.py` e `core.py`) precisa ser reescrito para consultar `TituloFinanceiro` (do `models/financeiro.py`) em vez de `ParcelaDespesa` (do legado).
- Só após todos os testes passarem nessa mudança, poderemos dropar `ParcelaDespesa`, `Despesa`, e `ExtratoBancario` do arquivo `domain.py` e gerar a respectiva *Alembic Migration*.

### Etapa 4: Testes Necessários Pós-Remoção
- **Frontend:** Executar compilação completa (`tsc --noEmit` / `npm run build`) para garantir que nenhuma dependência órfã quebrou o bundling do Vite. Acesso e bloqueio de rotas no Dashboard.
- **Backend:** Acionar inicialização do servidor e disparar teste de Ingestão de Planilha para confirmar que os `parsers` da etapa 1 realmente não fazem falta ao `StandardTemplateParser`.

### Etapa 5: Checklist para garantir sobrevivência da aplicação
- A API retorna 200 no endpoint `/health`?
- O login do frontend carrega a página `LoginPage.tsx` corretamente?
- A ingestão de um PDF joga o Job pra fila do Celery perfeitamente usando a fábrica nova?
- Migrations do banco rodam em bases limpas (verificando se imports foram apagados nas revisões históricas)?

---

## 3. Impactos Esperados
1. **Redução de tamanho do Repositório (KLOCs):** Menos ruído. Diminui a carga cognitiva necessária para novos desenvolvedores que entravam no projeto e ficavam confusos tentando descobrir qual "Login" ou qual "Parser" era o oficial.
2. **Tempo de build menor** no CI/CD.
3. **Consolidação de Rotas:** O arquivo `domain.py` deixará de ser um gargalo gigantesco com mais de 20 modelos aglutinados assim que passarmos da Etapa 3.

## 4. Arquivos que NÃO devem ser removidos (Falsos Positivos)
* `backend/app/models/__init__.py` -> Possui referências supostamente "legadas", mas necessárias para retrocompatibilidade no Alembic enquanto a transição de V1 para V2 do Documento Fiscal ocorre.
* `backend/app/contexts/AuthContext.tsx` -> É o contexto real e ativo (não deve ser confundido com a pasta apagada).
