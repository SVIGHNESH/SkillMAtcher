# --- SkillMatcher UI (SvelteKit + adapter-node) ---
FROM node:22-alpine AS build

WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install
COPY . .
RUN npm run build

# --- runtime: only the built server + prod deps ---
FROM node:22-alpine AS runtime
WORKDIR /app
ENV NODE_ENV=production
COPY package.json package-lock.json* ./
RUN npm install --omit=dev
COPY --from=build /app/build ./build

# PUBLIC_API_BASE is read at runtime by adapter-node (see api.ts)
ENV PORT=3000
EXPOSE 3000
CMD ["node", "build"]
