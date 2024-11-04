# Stage 1: Build
FROM oven/bun:1 AS builder
WORKDIR /app
COPY bun.lock* ./
COPY package.json ./
COPY . .
RUN bun i
ENV ADAPTER=bun
RUN bun run build

# Stage 2: Run
FROM oven/bun:1 AS runner
WORKDIR /app
COPY --from=builder /app/build ./build
COPY --from=builder /app/bun.lock* ./
COPY --from=builder /app/package.json ./
RUN bun i 
# Can't use --production flag because of bun bug ?
ENV PORT=8080
ENV ORIGIN=https://new.babel-revolution.fr
EXPOSE 8080
CMD ["bun", "run", "start"]