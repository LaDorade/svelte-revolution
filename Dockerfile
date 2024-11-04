# Stage 1: Build
FROM node:18 AS builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm install --force
COPY . .
ENV PROTOCOL_HEADER=x-forwarded-proto
ENV HOST_HEADER=x-forwarded-host
RUN npm run build

# Stage 2: Run
FROM node:18 AS runner
WORKDIR /app
COPY --from=builder /app/build ./build
COPY --from=builder /app/package.json /app/package-lock.json ./
RUN npm install --force
ENV PORT=8080
ENV ORIGIN=https://new.babel-revolution.fr
EXPOSE 8080
CMD ["npm", "start"]