FROM node:23

WORKDIR /app

RUN npm install -g pnpm

COPY package.json pnpm.* ./
RUN pnpm i

COPY . .
RUN pnpm build

EXPOSE 8080
CMD ["pnpm", "start:remote"]