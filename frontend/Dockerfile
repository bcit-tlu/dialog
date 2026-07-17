# --- Stage 1: build the static SPA ---
FROM node:20-alpine AS build

WORKDIR /app

# Install deps first for layer caching
COPY package.json package-lock.json ./
RUN npm ci

# Build
COPY . .
RUN npm run build

# --- Stage 2: serve with nginx ---
FROM nginx:alpine

# SPA fallback + /api proxy config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Static assets from the build stage
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
