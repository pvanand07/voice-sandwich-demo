# syntax = docker/dockerfile:1

# Adjust NODE_VERSION as desired
ARG NODE_VERSION=20.18.0
FROM node:${NODE_VERSION}-slim AS base

LABEL fly_launch_runtime="NodeJS"

# Install pnpm
RUN corepack enable && corepack prepare pnpm@10.22.0 --activate

# NodeJS app lives here
WORKDIR /app

# Set production environment
ENV NODE_ENV=production

# Throw-away build stage to reduce size of final image
FROM base AS build

# Install packages needed to build node modules
RUN apt-get update -qq && \
    apt-get install -y python-is-python3 pkg-config build-essential git

# Copy package files for all workspaces
COPY --link package.json pnpm-lock.yaml pnpm-workspace.yaml ./
COPY --link packages/graphs/package.json ./packages/graphs/
COPY --link packages/web/package.json ./packages/web/
COPY --link packages/webrtc/package.json ./packages/webrtc/

# Install dependencies
RUN pnpm install --frozen-lockfile

# Copy application code
COPY --link . .

# Build application
RUN pnpm run build

# Final stage for app image
FROM base AS runner

# Install runtime dependencies for native modules
RUN apt-get update -qq && \
    apt-get install -y python-is-python3 pkg-config build-essential && \
    rm -rf /var/lib/apt/lists/*

# Copy package files
COPY --link package.json pnpm-lock.yaml pnpm-workspace.yaml ./
COPY --link packages/graphs/package.json ./packages/graphs/
COPY --link packages/web/package.json ./packages/web/
COPY --link packages/webrtc/package.json ./packages/webrtc/

# Install production dependencies
RUN pnpm install --frozen-lockfile

# Copy built application
COPY --from=build /app/packages ./packages

# Set working directory to webrtc package
WORKDIR /app/packages/webrtc

# Expose port
EXPOSE 3001

# Start the server
CMD [ "pnpm", "run", "server" ]
