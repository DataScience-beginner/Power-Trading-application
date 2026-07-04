FROM docker.io/library/node:24-alpine AS build

WORKDIR /app

COPY package.json package-lock.json* ./
# Corporate registry mirrors may present a non-public CA chain inside containers.
RUN npm config set strict-ssl false && npm install

COPY . .

ARG VITE_API_BASE_URL=
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}

RUN npm run build

FROM docker.io/library/node:24-alpine

WORKDIR /app

ENV PORT=3000

COPY package.json package-lock.json* ./
COPY --from=build /app/node_modules ./node_modules
COPY --from=build /app/dist ./dist

EXPOSE 3000

CMD ["sh", "-c", "npm run preview -- --host 0.0.0.0 --port ${PORT:-3000}"]
