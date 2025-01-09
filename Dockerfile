FROM node:22
WORKDIR /app
RUN npm install -g bun
COPY package.json bun.lockb ./
RUN bun install
COPY . .
RUN bun run build
EXPOSE 8080
CMD ["bun", "run", "start"]