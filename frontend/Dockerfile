# Stage 1: Build
FROM node:20-alpine AS build

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm install

COPY . .

# Build with a placeholder - the real URL is injected at runtime
RUN npm run build

# Stage 2: Serve
FROM nginx:alpine

# Remove default nginx static assets
RUN rm -rf /usr/share/nginx/html/*

# Copy build assets from builder
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy entrypoint that injects runtime config
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Railway injects PORT at runtime - entrypoint handles everything
CMD ["/docker-entrypoint.sh"]
