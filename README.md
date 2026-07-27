# Ecomman Docker, Redis, Celery, and VPS Deployment

This file covers the Docker workflow for Ecomman on the shared VPS model used by Helix Studio and Bracket.

## What Runs Where

```text
Django web       handles HTTP requests
Celery worker    handles scraping and background jobs
Celery beat      schedules recurring scraping/materialized-view tasks
Redis            shared broker, result backend, channel layer, and cache
Nginx            public HTTPS reverse proxy on the VPS
Postgres         external database from DATABASE_URL
```

## Local Docker Development

Run commands from:

```powershell
cd C:\code\Ecomman
```

Start local Docker dev:

```powershell
docker compose -f docker-compose.dev.yml up --build
```

Reason: starts Django, Celery worker, Celery beat, and a local Redis container.

Open:

```text
http://localhost:8000/
```

Watch logs:

```powershell
docker compose -f docker-compose.dev.yml logs -f web celery_worker celery_beat redis
```

Reason: checks Django, worker, scheduler, and Redis together.

Stop local containers:

```powershell
docker compose -f docker-compose.dev.yml down
```

Reason: stops the dev stack.

## VPS Shared Redis Model

The VPS should keep one shared Redis for Helix Studio, Bracket, Ecomman, and future apps.

Shared Redis lives here:

```text
/opt/shared/redis
```

Ecomman app code should live here:

```text
/opt/apps/ecomman
```

Shared Docker network:

```bash
docker network create shared_backend_network
```

Reason: lets Ecomman containers reach shared Redis privately.

Ecomman uses these Redis DBs:

```yaml
REDIS_URL: "redis://redis:6379/20"
CHANNEL_REDIS_URL: "redis://redis:6379/20"
CELERY_BROKER_URL: "redis://redis:6379/21"
CELERY_RESULT_BACKEND: "redis://redis:6379/22"
DJANGO_CACHE_URL: "redis://redis:6379/23"
REDIS_KEY_PREFIX: "ecomman:prod"
```

Reason: keeps Ecomman separated from Helix Studio and Bracket inside the same Redis container.

## Production Compose

`docker-compose.prod.yml` is the live deployment file.

`docker-compose.yml` mirrors it so default Compose behaves the same if used later.

Production services:

```text
ecomman_backend_prod
ecomman_celery_prod
ecomman_celery_beat_prod
```

Production Ecomman listens on host port `8002` only on loopback:

```yaml
ports:
  - "127.0.0.1:8002:8000"
```

Reason: Nginx can proxy to Ecomman locally while Django is not exposed directly to the internet.

## Production Start

From the VPS app folder:

```bash
cd /opt/apps/ecomman
docker compose -f docker-compose.prod.yml up -d --build
```

Reason: builds and starts Django web, Celery worker, and Celery beat.

Check:

```bash
docker ps
docker compose -f docker-compose.prod.yml logs --tail=100 web celery_worker celery_beat
```

Reason: confirms migrations, collectstatic, Gunicorn, worker, and beat startup.

## Nginx Reverse Proxy

Create or update the Ecomman Nginx site:

```nginx
server {
    listen 80;
    server_name ecomman.up.railway.app;

    location /media/ {
        alias /opt/apps/ecomman/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8002;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Replace `ecomman.up.railway.app` with the real VPS domain when DNS is ready.

Verify and reload:

```bash
sudo nginx -t
sudo systemctl reload nginx
```

Reason: applies the proxy only after config validation passes.

## Production Update Flow

After pushing app changes to GitHub, run on VPS:

```bash
cd /opt/apps/ecomman
git pull
docker compose -f docker-compose.prod.yml up -d --build
docker ps
```

Reason: pulls code, rebuilds images, and restarts changed services.

If `project/.env` changed:

```bash
docker compose -f docker-compose.prod.yml up -d --build --force-recreate
```

Reason: containers must be recreated to load new env values.

## Verification

```bash
curl -I http://127.0.0.1:8002/
docker compose -f docker-compose.prod.yml logs --tail=80 web
docker compose -f docker-compose.prod.yml logs --tail=80 celery_worker
docker compose -f docker-compose.prod.yml logs --tail=80 celery_beat
docker exec redis redis-cli ping
```

Expected:

```text
web container: healthy
celery worker: healthy
celery beat: running
redis: PONG
```

## Railway Files

`Procfile` and `runtime.txt` were Railway-specific and are removed from the Docker VPS setup.
