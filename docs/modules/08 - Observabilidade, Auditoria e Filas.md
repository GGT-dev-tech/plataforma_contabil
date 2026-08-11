# 08 - Observabilidade, Auditoria e Filas

## 1. Operando em Larga Escala
Quando a plataforma assumir múltiplos relatórios diários de dezenas de clientes integrando com o Sienge (ERP) ou Dominio Sistemas (Contábil), é provável que ocorram picos intermitentes de concorrência ou paralisações de serviços terceiros (Down-time das APIs dos ERPs).

Para não colapsar sob carga e garantir rastreabilidade, o sistema delega as integrações para **Filas Assíncronas (Queues)** baseadas em `RabbitMQ` / `Redis` + `Celery`.

## 2. A Pipeline de Integração (Integration & Routing)
O fluxo não funciona de forma síncrona aguardando o processamento:
1. **Requisição:** Usuário aperta "Iniciar Fechamento".
2. **Accept:** A API responde imediatamente com `202 ACCEPTED` e fornece um `execution_id`.
3. **Queue:** O Motor Contábil empacota as ordens e envia para a fila `integrations_queue`.
4. **Workers:** Nos bastidores, robôs (Workers) pegam as tarefas, fazem as chamadas lentas ao ERP destino e monitoram o sucesso de cada lote.

## 3. Resiliência de Robôs (Retry & Dead-Letter)
Caso a integração falhe no momento do POST (ERP fora do ar, erro HTTP 500, Rate Limit excedido 429), o Worker não descarta o processamento:
- **Exponential Backoff:** O trabalhador dorme e tenta o lote em 10 segundos. Se falhar, tenta em 30s. Se falhar, em 5 minutos.
- **Dead-Letter Queue (DLQ):** Após atingir o limite máximo de retentativas (ex: 5 vezes), a mensagem é enviada para a fila de "Mensagens Mortas". Um painel do administrador (Insights Module) piscará em vermelho informando que há conciliações paradas permanentemente, que requerem intervenção humana para "Replay".

## 4. O Módulo de Insights (Painel de Monitoramento)
O Frontend consome estatísticas globais via WebSockets e APIs para prover os painéis de saúde (Health Dashboards):
- Contagem total de integrações diárias.
- Gráfico de pizza de Sucesso vs Falha.
- Monitor de volume das filas ativas e tempo médio de conclusão (Lead time de ingestão).

Essa transparência é vital para que os Analistas Contábeis saibam **exatamente o que está acontecendo sem precisarem acionar a equipe de TI**.
