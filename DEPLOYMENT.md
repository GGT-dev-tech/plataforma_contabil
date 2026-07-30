# Guia de Deploy - Railway

Este documento descreve os passos necessários para realizar o deploy da Plataforma Contábil no Railway.

## Serviços Railway
A infraestrutura será composta pelos seguintes serviços no Railway:
- `plataforma-backend`
- `plataforma-frontend`
- `PostgreSQL`
- `Redis`

## Variáveis de Ambiente

### Backend (`plataforma-backend`)
Configure as seguintes variáveis no serviço do backend:
- `DATABASE_URL`: `${{Postgres.DATABASE_URL}}` (Injetada automaticamente se linkado ao serviço Postgres)
- `JWT_SECRET_KEY`: Sua chave secreta para JWT
- `CORS_ORIGINS`: `["https://seu-frontend.up.railway.app"]` (Adicione a URL do frontend gerada pelo Railway)
- `REDIS_URL`: `${{Redis.REDIS_URL}}` (Injetada automaticamente se linkado ao serviço Redis)
- `APP_ENV`: `staging` ou `production`
- `UPLOAD_PATH`: `/app/uploads`

### Frontend (`plataforma-frontend`)
Configure as seguintes variáveis no serviço do frontend:
- `VITE_API_URL`: `https://seu-backend.up.railway.app/api/v1` (A URL pública gerada pelo Railway para o backend)

## Ordem de Deploy

Siga exatamente a ordem abaixo para evitar indisponibilidade:

1. **Criar Postgres**: Crie o banco de dados PostgreSQL.
2. **Criar Redis**: Crie o banco de dados Redis.
3. **Configurar backend**: Crie o serviço backend a partir do repositório GitHub. Configure as variáveis de ambiente acima.
4. **Rodar migrations**: O Railway geralmente vai construir e rodar o backend. Certifique-se de executar as migrations do Alembic no backend (`alembic upgrade head`) via Railway CLI ou executando o comando no container. (Você pode configurar um *Start Command* personalizado se necessário).
5. **Subir frontend**: Crie o serviço frontend a partir do repositório GitHub e adicione as variáveis.
6. **Validar healthcheck**: Acesse `https://seu-backend.up.railway.app/health` e confirme se o status retorna `{ "status": "ok", "database": "connected" }`.

## Observação Arquitetural

**Uploads e Armazenamento**
Atualmente a plataforma utiliza `LocalStorageProvider` para manipular o upload de arquivos. 

- **MVP/Staging**: `LocalStorageProvider` (arquivos salvos no filesystem efêmero do container).
- **Produção**: **OBRIGATÓRIO** utilizar S3 ou outro Cloud Storage Provider. Arquivos contábeis (extratos, notas fiscais, planilhas) são parte do histórico auditável e não podem ser perdidos a cada deploy ou reinicialização do container. Planeje a integração com S3 antes do Go-Live.
