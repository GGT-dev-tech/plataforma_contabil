# Stage 1: Build
FROM node:20-alpine AS build

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build

# Stage 2: Serve
FROM nginx:alpine

# Remove default nginx static assets
RUN rm -rf /usr/share/nginx/html/*

# Copy build assets from builder
COPY --from=build /app/dist /usr/share/nginx/html

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Railway injects the PORT environment variable
# We need to replace the default 80 port in nginx.conf with the Railway PORT dynamically
CMD sed -i -e 's/listen 80;/listen '"$PORT"';/g' /etc/nginx/conf.d/default.conf && nginx -g 'daemon off;'
