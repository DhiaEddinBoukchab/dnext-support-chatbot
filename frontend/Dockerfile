# Frontend build for development and production

# Stage 1: Build
FROM node:18-alpine as builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Stage 2: Development (with hot reload)
FROM node:18-alpine as dev

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Expose port
EXPOSE 3000 5173

# Start dev server with Vite
CMD ["npm", "run", "dev", "--", "--host"]

# Stage 3: Production
FROM node:18-alpine as prod

WORKDIR /app

# Copy built assets from builder
COPY --from=builder /app/dist ./dist

# Install http-server for static serving
RUN npm install -g http-server

# Expose port
EXPOSE 3000

# Serve the built application
CMD ["http-server", "dist", "-p", "3000", "-g"]
