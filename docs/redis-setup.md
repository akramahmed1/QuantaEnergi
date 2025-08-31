# Redis Setup Guide for QuantaEnergi

## Quick Start (Development)

### Option 1: Docker (Recommended)
```bash
# Start Redis server
docker run -d --name quantaenergi-redis -p 6379:6379 redis:7-alpine

# Check if running
docker ps | grep redis

# Stop Redis
docker stop quantaenergi-redis
```

### Option 2: Local Installation

#### Windows
1. Download Redis from: https://github.com/microsoftarchive/redis/releases
2. Extract and run `redis-server.exe`
3. Or use WSL2 and follow Linux instructions

#### macOS
```bash
# Using Homebrew
brew install redis
brew services start redis

# Check status
brew services list | grep redis
```

#### Linux (Ubuntu/Debian)
```bash
# Install Redis
sudo apt update
sudo apt install redis-server

# Start Redis service
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Check status
sudo systemctl status redis-server
```

## Production Setup

### Redis Cluster (6 nodes)
```bash
# Use the provided docker-compose.prod.yml
docker-compose -f docker-compose.prod.yml up -d

# This will start:
# - 6 Redis nodes (ports 6379-6384)
# - Redis cluster initialization
# - Redis Commander for management (port 8081)
```

### Health Check
```bash
# Test Redis connection
redis-cli ping
# Should return: PONG

# Test cluster status
redis-cli -p 6379 cluster info
```

## Configuration

### Environment Variables
```bash
# Single Redis instance
REDIS_URL=redis://localhost:6379

# Redis Cluster
REDIS_CLUSTER_NODES=localhost:6379,localhost:6380,localhost:6381,localhost:6382,localhost:6383,localhost:6384
```

### Redis Configuration
The Redis configuration is handled automatically by the Docker setup.
For custom configurations, modify the docker-compose.prod.yml file.

## Troubleshooting

### Common Issues

1. **Connection Refused (Error 10061)**
   - Redis server not running
   - Wrong port number
   - Firewall blocking connection

2. **Redis Cluster Not Initialized**
   - Wait for redis-cluster-init service to complete
   - Check logs: `docker logs quantaenergi-redis-cluster-init`

3. **Memory Issues**
   - Redis default memory limit: 2GB
   - Adjust in docker-compose.prod.yml if needed

### Logs
```bash
# View Redis logs
docker logs quantaenergi-redis-node-1

# View cluster initialization logs
docker logs quantaenergi-redis-cluster-init
```

## Performance Tuning

### Memory Configuration
```yaml
# In docker-compose.prod.yml
redis-node-1:
  command: redis-server --maxmemory 1gb --maxmemory-policy allkeys-lru
```

### Persistence
```yaml
# Data persistence is enabled by default
volumes:
  - redis-data-1:/data
```

## Security

### Network Isolation
- Redis nodes are isolated in the `quantaenergi-network` Docker network
- External access only through Redis Commander (port 8081)

### Authentication
- Redis authentication can be enabled by setting `requirepass` in Redis configuration
- Update environment variables accordingly
