FROM node:20 AS build

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

# Pass in env variables at build time if they need to be baked into static files (Vite does this).
# For Railway, these can be set as ARG, but we'll let Vite handle dynamic proxying or we'll just build it 
# assuming VITE_API_URL is provided during docker build
ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL

RUN npm run build

FROM nginx:alpine

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
