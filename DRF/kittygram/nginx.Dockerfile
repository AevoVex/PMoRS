FROM node:20-alpine AS frontend
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM nginx:1.27-alpine
RUN rm /etc/nginx/conf.d/default.conf
COPY kittygram/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=frontend /frontend/build/ /srv/frontend/
