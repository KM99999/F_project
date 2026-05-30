# Frontend image — multi-stage: build the Vite SPA, serve it with nginx.
FROM node:20-alpine AS build

WORKDIR /app
COPY frontend/package.json ./
# No lockfile committed yet; use install. Switch to `npm ci` once package-lock.json exists.
RUN npm install

COPY frontend/ ./
# In the composed stack the SPA talks to the API under /api (proxied by nginx).
ENV VITE_API_URL=/api
RUN npm run build

FROM nginx:1.27-alpine
COPY docker/nginx/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
