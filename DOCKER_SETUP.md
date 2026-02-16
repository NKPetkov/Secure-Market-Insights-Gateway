# SMIG Docker Setup Guide

## Architecture Overview

The Docker environment consists of three services connected via two internal networks:

```
┌─────────────────────────────────────────────────────────────┐
│                        Internet                              │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            │ Port 8001 (exposed)
                            │
                   ┌────────▼────────┐
                   │    Gateway      │
                   │   (Port 8001)   │
                   └────┬───────┬────┘
                        │       │
      ┌─────────────────┘       └─────────────────┐
      │                                            │
      │ redis_gateway_network    fetcher_gateway_network
      │                                            │
┌─────▼──────┐                            ┌───────▼──────┐
│   Redis    │                            │   Fetcher    │
│ (Port 5665)│                            │ (Port 8000)  │
└────────────┘                            └──────────────┘
```

### Services

1. **Fetcher Service** (`fetcher`)
   - Port: 8000 (internal) / 8000 (exposed for development)
   - Function: Fetches cryptocurrency data from CoinMarketCap API
   - Network: `fetcher_gateway_network`

2. **Gateway Service** (`gateway`)
   - Port: 8001 (exposed to internet)
   - Function: API Gateway with caching, rate limiting, and authentication
   - Networks: `redis_gateway_network`, `fetcher_gateway_network`

3. **Redis** (`redis`)
   - Port: 5665 (internal) / 5665 (exposed for development)
   - Function: Caching and rate limiting storage
   - Network: `redis_gateway_network`

### Networks

- **`redis_gateway_network`**: Internal network for Redis ↔ Gateway communication
- **`fetcher_gateway_network`**: Internal network for Fetcher ↔ Gateway communication

## Quick Start

### Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+

### Setup Steps

1. **Clone the repository** (if not already done)
   ```bash
   cd C:\Users\User\Desktop\PROJECTS\SMIG_raw
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   ```

3. **Edit `.env` file with your credentials**
   ```bash
   # Required: Update these values
   API_TOKEN=your-actual-secret-token
   COINMARKETCAP_API_KEY=your-actual-coinmarketcap-api-key
   ```

4. **Build and start services**
   ```bash
   docker-compose up --build
   ```

   Or run in detached mode:
   ```bash
   docker-compose up --build -d
   ```

5. **Verify services are running**
   ```bash
   docker-compose ps
   ```

   Expected output:
   ```
   NAME            SERVICE    STATUS       PORTS
   smig_fetcher    fetcher    Up (healthy) 0.0.0.0:8000->8000/tcp
   smig_gateway    gateway    Up (healthy) 0.0.0.0:8001->8001/tcp
   smig_redis      redis      Up (healthy) 0.0.0.0:5665->5665/tcp
   ```

## Usage

### Access the Services

- **Gateway API**: http://localhost:8001
- **Gateway Docs**: http://localhost:8001/docs
- **Fetcher API**: http://localhost:8000
- **Fetcher Docs**: http://localhost:8000/docs

### Health Check Endpoints

```bash
# Gateway health
curl http://localhost:8001/health

# Fetcher health
curl http://localhost:8000/health
```

### Example API Request

```bash
# Get insights for Bitcoin (requires authentication)
curl -H "Authorization: Bearer your-actual-secret-token" \
     http://localhost:8001/insights/BTC
```

## Docker Compose Commands

### Start services
```bash
docker-compose up
```

### Start in background
```bash
docker-compose up -d
```

### Stop services
```bash
docker-compose down
```

### Stop and remove volumes (clears Redis data)
```bash
docker-compose down -v
```

### Rebuild services
```bash
docker-compose up --build
```

### View logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f gateway
docker-compose logs -f fetcher
docker-compose logs -f redis
```

### Restart a service
```bash
docker-compose restart gateway
```

### Execute command in container
```bash
# Access Redis CLI
docker-compose exec redis redis-cli -p 5665

# Access gateway shell
docker-compose exec gateway /bin/bash

# Access fetcher shell
docker-compose exec fetcher /bin/bash
```

## Configuration

### Environment Variables

All configuration is done through environment variables in the `.env` file:

#### Gateway Service
- `API_TOKEN`: Bearer token for API authentication
- `FETCHER_TIMEOUT`: Timeout for fetcher requests (default: 10s)
- `CACHE_TTL_SECONDS`: Cache expiration time (default: 600s)
- `RATE_LIMIT_REQUESTS`: Number of requests allowed (default: 10)
- `RATE_LIMIT_WINDOW_SECONDS`: Rate limit window (default: 60s)
- `REDIS_DB`: Redis database number (default: 0)
- `REDIS_PASSWORD`: Redis password (optional)

#### Fetcher Service
- `COINMARKETCAP_API_KEY`: Your CoinMarketCap API key
- `COINMARKETCAP_BASE_URL`: CoinMarketCap API base URL
- `OUTSIDE_REQUEST_TIMEOUT`: External API timeout (default: 10s)

#### General
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

## Production Deployment

For production, consider these modifications:

1. **Set networks to internal**:
   ```yaml
   networks:
     redis_gateway_network:
       internal: true
     fetcher_gateway_network:
       internal: true
   ```

2. **Remove exposed ports** for fetcher and redis (only expose gateway):
   ```yaml
   fetcher:
     # Remove or comment out ports section
     # ports:
     #   - "8000:8000"

   redis:
     # Remove or comment out ports section
     # ports:
     #   - "5665:5665"
   ```

3. **Add Redis password**:
   ```bash
   REDIS_PASSWORD=strong-random-password
   ```

4. **Use secrets management** instead of `.env` file

5. **Add resource limits**:
   ```yaml
   services:
     gateway:
       deploy:
         resources:
           limits:
             cpus: '1'
             memory: 512M
   ```

6. **Enable TLS/SSL** with a reverse proxy (nginx, traefik)

## Troubleshooting

### Service won't start
```bash
# Check logs
docker-compose logs service_name

# Check if ports are already in use
netstat -ano | findstr "8000"
netstat -ano | findstr "8001"
netstat -ano | findstr "5665"
```

### Redis connection failed
```bash
# Test Redis connection
docker-compose exec redis redis-cli -p 5665 ping

# Check Redis logs
docker-compose logs redis
```

### Gateway can't reach fetcher
```bash
# Check network connectivity
docker-compose exec gateway ping fetcher

# Verify fetcher is healthy
docker-compose ps fetcher
```

### Clear everything and start fresh
```bash
docker-compose down -v
docker-compose build --no-cache
docker-compose up
```

## Development Tips

### Hot Reload

To enable hot reload during development, mount source code as volumes:

```yaml
services:
  gateway:
    volumes:
      - ./gateway/app:/app/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

### Debug Mode

Set `LOG_LEVEL=DEBUG` in `.env` file for verbose logging.

### Testing

Run tests inside containers:
```bash
# Run gateway tests
docker-compose exec gateway pytest

# Run fetcher tests
docker-compose exec fetcher pytest
```
