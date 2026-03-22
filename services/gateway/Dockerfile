# syntax=docker/dockerfile:1
FROM node:24-bookworm-slim AS builder

# Security patch for the build environment
RUN apt-get update && apt-get upgrade -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY package.json package-lock.json ./

# Total installation (includes build/test tools if needed)
RUN npm ci

COPY . .

# [Optional]  "npm run build" when having TypeScript

# Remove devDependencies after the build
# We gain weight here
RUN npm prune --production && npm cache clean --force


# ---- Production ----
FROM node:24-bookworm-slim AS production

ENV NODE_ENV=production \
    npm_config_update_notifier=false

# Security patch for the final image (Critical for production)
RUN apt-get update && apt-get upgrade -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Update npm to avoid security alerts (CVE)
RUN npm install -g npm@latest && npm cache clean --force

WORKDIR /app

# Transfer the cleaned bits: we use --chown to make the 'node' user the direct owner
COPY --from=builder --chown=node:node /app/package.json ./
COPY --from=builder --chown=node:node /app/node_modules ./node_modules
COPY --from=builder --chown=node:node /app/src ./src

# If you have a dist/ folder (JS compiled), you would copy it here also
# COPY --from=builder --chown=node:node /app/dist ./dist

USER node

EXPOSE 3000

CMD ["node", "src/index.js"]