# Redis Setup Guide for Windows

## Option 1: Native Windows Installation (Recommended)
1. Download Redis for Windows from: https://github.com/tporadowski/redis/releases
2. Download the latest `.msi` file
3. Install Redis
4. Start Redis server: `redis-server.exe`
5. Test connection: `redis-cli ping`

## Option 2: WSL2 (Windows Subsystem for Linux)
1. Install WSL2: `wsl --install`
2. Install Redis in WSL: `sudo apt update && sudo apt install redis-server`
3. Start Redis: `sudo service redis-server start`
4. Configure Windows to connect to WSL Redis

## Option 3: Docker (if available)
```bash
docker run -d -p 6379:6379 --name redis redis:alpine
```

## Option 4: Redis Cloud (Free Tier)
1. Sign up at https://redis.com/try-free/
2. Get connection string
3. Update .env: `REDIS_URL=your_redis_cloud_url`

## Option 5: Skip Redis for Development
If you can't get Redis running, the app will work with caching disabled.
Update .env: `ENABLE_CACHING=false`
