# Multi-stage build for QuantaEnergi Frontend
FROM node:18-alpine as builder

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production stage with Nginx
FROM nginx:alpine

# Install curl for health checks
RUN apk add --no-cache curl

# Copy built application from builder stage
COPY --from=builder /app/.next /usr/share/nginx/html

# Copy custom Nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Create non-root user
RUN addgroup -g 1001 -S quantaenergi && \
    adduser -S quantaenergi -u 1001

# Set proper permissions
RUN chown -R quantaenergi:quantaenergi /usr/share/nginx/html && \
    chown -R quantaenergi:quantaenergi /var/cache/nginx && \
    chown -R quantaenergi:quantaenergi /var/log/nginx && \
    chown -R quantaenergi:quantaenergi /etc/nginx/conf.d && \
    touch /var/run/nginx.pid && \
    chown -R quantaenergi:quantaenergi /var/run/nginx.pid

# Switch to non-root user
USER quantaenergi

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:3000/ || exit 1

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]
