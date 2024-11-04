FROM node:22
WORKDIR /app
RUN npm install -g bun
COPY package.json package-lock.json ./
RUN bun install
COPY . .
RUN bun run build
ENV PORT=8080
ENV ORIGIN=https://new.babel-revolution.fr
EXPOSE 8080
CMD ["bun", "run", "start"]