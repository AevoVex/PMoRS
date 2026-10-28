FROM node:20-alpine AS build

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . ./
RUN npm run build

FROM alpine:3.20
COPY --from=build /app/build/ /frontend_static/
CMD ["sh", "-c", "test -f /frontend_static/index.html"]
