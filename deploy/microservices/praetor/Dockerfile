# Dockerfile.lightweight

# ------------------------------------------------------------------------------
# Stage 1: Builder (Heavy)
# ------------------------------------------------------------------------------
FROM node:20-slim AS builder

# Install Build Tools for C++ Addon
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 make g++ cmake git \
    ca-certificates curl gnupg \
    libxml2-dev libomp-dev \
    libboost-all-dev \
    libjemalloc-dev \
    && update-ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app

# --- 1. Build scram-node ---
# Copy scram-node source
COPY scram-node ./scram-node

# Install and Build scram-node
WORKDIR /usr/src/app/scram-node
RUN npm install
RUN npm run install
# This produces ./build/Release/scram-node.node

# --- 2. Build NestJS App ---
WORKDIR /usr/src/app

# Copy App Source
COPY src ./src
COPY config ./config

# Copy Root Configs
COPY package.json ./package.json
COPY tsconfig.json ./tsconfig.json
COPY nest-cli.json ./nest-cli.json

# Install App Dependencies
# This will link scram-node via "file:./scram-node"
RUN npm install

# Patch TypeScript for Typia
RUN ./node_modules/.bin/ts-patch install -s

# Build the App
RUN npm run build

# Prune dev dependencies to reduce size
RUN npm prune --production

# ------------------------------------------------------------------------------
# Stage 2: Runner (Lightweight)
# ------------------------------------------------------------------------------
FROM node:20-slim

# Install ONLY Runtime Shared Libraries
# These are required by the C++ addon (scram-node)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libxml2 \
    libboost-filesystem1.74.0 \
    libboost-program-options1.74.0 \
    libjemalloc2 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app

# Copy built artifacts from builder
COPY --from=builder /usr/src/app/node_modules ./node_modules
COPY --from=builder /usr/src/app/dist ./dist
# Copy the built C++ addon source folder (because npm install likely symlinked it)
COPY --from=builder /usr/src/app/scram-node ./scram-node

# Set Env
ENV NODE_ENV=production

# Expose port (default NestJS port)
EXPOSE 3000

CMD ["node", "dist/src/main.js"]
