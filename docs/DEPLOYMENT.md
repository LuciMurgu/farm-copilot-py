# Farm Copilot — Deployment Guide for iagricultura.ro

## Architecture

```
Farmer's browser
      │ HTTPS
      ▼
Cloudflare (SSL termination, DNS proxy)
      │ HTTP (to origin)
      ▼
VPS (iagricultura.ro)
  ├── nginx (port 80 → proxy to 8000)
  └── docker compose
        ├── app (FastAPI, port 8000)
        └── db (PostgreSQL 16, port 5432)
```

Cloudflare handles HTTPS. Nginx on the VPS handles proxying.
Docker Compose runs the app + database.

---

## Step 1 — VPS Setup

You need a VPS with:
- Ubuntu 22.04+ or Debian 12+
- 2GB+ RAM (PostgreSQL + Python app)
- Docker + Docker Compose installed
- nginx installed

If Docker isn't installed:
```bash
# Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
# Log out and back in

# nginx
sudo apt update && sudo apt install -y nginx
```

---

## Step 2 — DNS (Cloudflare)

In Cloudflare dashboard for iagricultura.ro:

1. Go to **DNS > Records**
2. Add an **A record**:
   - Name: `@` (or `iagricultura.ro`)
   - IPv4: `YOUR_VPS_IP`
   - Proxy: **Proxied** (orange cloud ON)
   - TTL: Auto

3. Optional — add a `www` CNAME:
   - Name: `www`
   - Target: `iagricultura.ro`
   - Proxy: Proxied

4. Go to **SSL/TLS > Overview**
   - Set mode to **Full** (not Full Strict — we don't have a cert on origin)
   - This means: Cloudflare encrypts browser→CF, and CF connects to your server on port 80

5. Go to **SSL/TLS > Edge Certificates**
   - Enable "Always Use HTTPS" → ON
   - Minimum TLS Version → TLS 1.2

---

## Step 3 — Clone and Configure on VPS

```bash
ssh your-vps

# Clone the repo
git clone https://github.com/LuciMurgu/farm-copilot-py.git
cd farm-copilot-py

# Create production env file
cp .env.production.example .env.production
```

Edit `.env.production` with real values:
```bash
nano .env.production
```

```bash
# ── Database ──────────────────────────────────────
DB_PASSWORD=USE_A_STRONG_RANDOM_PASSWORD_HERE

# ── ANAF OAuth ────────────────────────────────────
# Generate encryption key:
# python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
ANAF_ENCRYPTION_KEY=PASTE_GENERATED_KEY_HERE
ANAF_CLIENT_ID=your_anaf_oauth_client_id
ANAF_CLIENT_SECRET=your_anaf_oauth_client_secret
ANAF_REDIRECT_URI=https://iagricultura.ro/anaf/callback
ANAF_TEST_MODE=false

# ── Auto-Sync ────────────────────────────────────
ANAF_SYNC_ENABLED=true
ANAF_SYNC_INTERVAL_SECONDS=14400

# ── Session ───────────────────────────────────────
# Generate: python3 -c "import secrets; print(secrets.token_hex(32))"
SESSION_SECRET_KEY=PASTE_GENERATED_KEY_HERE

# ── Application ──────────────────────────────────
ENV=production
```

Generate the secrets:
```bash
# Encryption key
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Session key
python3 -c "import secrets; print(secrets.token_hex(32))"

# DB password
python3 -c "import secrets; print(secrets.token_hex(16))"
```

---

## Step 4 — nginx Configuration

```bash
sudo nano /etc/nginx/sites-available/iagricultura.ro
```

Paste:
```nginx
server {
    listen 80;
    server_name iagricultura.ro www.iagricultura.ro;

    # File upload size (XML invoices)
    client_max_body_size 10M;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts for sync operations
        proxy_read_timeout 120s;
        proxy_connect_timeout 10s;
    }
}
```

Enable and restart:
```bash
sudo ln -s /etc/nginx/sites-available/iagricultura.ro /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

Note: We listen on port 80 only (HTTP). Cloudflare handles HTTPS
at the edge and forwards to our port 80. The "Full" SSL mode means
Cloudflare encrypts the browser→CF connection.

---

## Step 5 — Deploy

```bash
cd ~/farm-copilot-py

# Build and start
docker compose --env-file .env.production up -d --build

# Watch logs
docker compose logs -f app

# You should see:
# "Running database migrations..."
# "Migrations complete"
# "ANAF auto-sync scheduler started"
# "Uvicorn running on http://0.0.0.0:8000"
```

---

## Step 6 — Verify

```bash
# Health check (from VPS)
curl http://localhost:8000/health

# From your local machine
curl https://iagricultura.ro/health

# Open in browser
# https://iagricultura.ro → should show login page
```

Register your account, upload the test XML, verify everything works.

---

## Step 7 — Firewall

Lock down the VPS — only allow HTTP, HTTPS, and SSH:

```bash
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw deny 5432/tcp   # PostgreSQL — never exposed
sudo ufw deny 8000/tcp   # App — nginx proxies, not direct access
sudo ufw enable
```

Note: Port 443 is allowed in case you want direct HTTPS later,
but Cloudflare connects to port 80 in "Full" mode.

---

## Maintenance Commands

```bash
# View logs
docker compose logs -f app
docker compose logs -f db

# Restart app (after code update)
cd ~/farm-copilot-py
git pull
docker compose --env-file .env.production up -d --build

# Database backup
docker compose exec db pg_dump -U farm_copilot farm_copilot > backup_$(date +%Y%m%d).sql

# Restore from backup
cat backup_20260405.sql | docker compose exec -T db psql -U farm_copilot farm_copilot

# Check disk usage
docker system df

# View running containers
docker compose ps
```

---

## Troubleshooting

**App won't start — migration error:**
```bash
docker compose logs app | grep -i "migration\|error"
# Usually means DB isn't ready yet — restart app:
docker compose restart app
```

**502 Bad Gateway in browser:**
```bash
# Check if app is running
docker compose ps
# Check if nginx can reach the app
curl -v http://localhost:8000/health
```

**Cloudflare shows "Origin DNS error":**
- Verify A record points to correct VPS IP
- Wait 5 minutes for DNS propagation
- Check: `dig iagricultura.ro` shows your VPS IP

**ANAF OAuth callback fails:**
- Verify `ANAF_REDIRECT_URI=https://iagricultura.ro/anaf/callback`
- Must be HTTPS (Cloudflare provides this)
- Must match exactly what's registered with ANAF

**Scheduler not running:**
- Check logs: `docker compose logs app | grep scheduler`
- Verify `ANAF_SYNC_ENABLED=true` in .env.production
- Only works with `workers=1` (default in production.py)
