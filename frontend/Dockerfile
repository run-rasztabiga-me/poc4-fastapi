# Etap 1: Budowanie aplikacji
FROM node:20-alpine as build

WORKDIR /app

# Kopiowanie plików zależności
COPY package*.json ./

# Instalacja zależności
RUN npm install

# Kopiowanie kodu źródłowego
COPY . .

# Zmienne środowiskowe
ARG VITE_API_URL
ENV VITE_API_URL=${VITE_API_URL}

# Budowanie aplikacji
RUN npm run build

# Etap 2: Serwowanie aplikacji
FROM nginx:alpine

# Kopiowanie zbudowanej aplikacji
COPY --from=build /app/dist /usr/share/nginx/html

# Kopiowanie konfiguracji nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Eksponowanie portu
EXPOSE 80

# Uruchomienie nginx
CMD ["nginx", "-g", "daemon off;"]
