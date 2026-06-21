FROM node:20-alpine AS build

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

ARG VITE_API_BASE_URL
ARG VITE_GOOGLE_SHEET_ID
ARG VITE_GOOGLE_SHEET_GID

ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
ENV VITE_GOOGLE_SHEET_ID=$VITE_GOOGLE_SHEET_ID
ENV VITE_GOOGLE_SHEET_GID=$VITE_GOOGLE_SHEET_GID

RUN npm run build

FROM node:20-alpine

WORKDIR /app

RUN npm install -g serve@14.2.4

COPY --from=build /app/dist ./dist

EXPOSE 3000

CMD serve -s dist -l ${PORT:-3000}
