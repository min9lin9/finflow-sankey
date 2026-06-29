FROM oven/bun:1

WORKDIR /app
COPY package.json tsconfig.json vite.config.ts index.html ./
COPY src ./src
RUN bun install --frozen-lockfile || bun install
EXPOSE 5173
CMD ["bun", "run", "dev", "--host", "0.0.0.0"]
