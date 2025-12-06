# Deployment Guide: Exposing Your On-Premise Cluster to the Internet

This guide shows you how to deploy your RAPTOR application on your university cluster and make it accessible from the public internet - without needing DNS knowledge, SSL certificates, or a public IP address.

## Prerequisites

- Docker Swarm cluster running on university network
- Internet connection from cluster nodes
- No public IP or domain required

---

## Step 1: Sign Up for Cloudflare (FREE)

1. Go to https://dash.cloudflare.com/sign-up
2. Create a free account (no credit card needed)
3. Verify your email

---

## Step 2: Create a Cloudflare Tunnel

### Using the Dashboard (Recommended)

1. Log into your Cloudflare dashboard
2. Navigate to **Zero Trust** (left sidebar)
3. Go to **Networks** → **Connectors**
4. Click **"Create a tunnel"**
5. Select **"Cloudflared"** as the connector
6. Name your tunnel: `raptor-cluster`
7. Follow the instructions provided on the `Install and run connectors` tab.

```
# Add cloudflare gpg key
sudo mkdir -p --mode=0755 /usr/share/keyrings
curl -fsSL https://pkg.cloudflare.com/cloudflare-public-v2.gpg | sudo tee /usr/share/keyrings/cloudflare-public-v2.gpg >/dev/null

# Add this repo to your apt repositories
echo 'deb [signed-by=/usr/share/keyrings/cloudflare-public-v2.gpg] https://pkg.cloudflare.com/cloudflared any main' | sudo tee /etc/apt/sources.list.d/cloudflared.list

# install cloudflared
sudo apt-get update && sudo apt-get install cloudflared

sudo cloudflared service install eyJhIjoiMWIzZTkwZTRkMGEzNDBkZGUwNWJiOGE4MDZlMzNiNzgiLCJ0IjoiNGJhYjhhNTMtYTY5Yy00YmRmLTk4MWMtYTE4NDNmNTZlODg3IiwicyI6IlpqVXhOalF5TnpZdE4yVm1OQzAwTURoa0xXSTRaRE10WTJJd1ltSTJabVppWm1NNSJ9
```

8. **Copy the tunnel token** - and keep this safe!
---

## Step 3: Configure Public Routes

In the tunnel configuration page:

1. Click **"Public Hostname"** tab
2. Add the following routes:

### Route 1: API Service
- **Subdomain**: `raptor-api`
- **Domain**: openpra.org
- **Service Type**: `HTTP`
- **URL**: `raptor-manager:3000`

### Route 2: RabbitMQ Management
- **Subdomain**: `raptor-rmq`
- **Domain**: Same as above
- **Service Type**: `HTTP`
- **URL**: `rabbitmq:15672`

### Route 3: MinIO Console
- **Subdomain**: `raptor-minio`
- **Domain**: Same as above
- **Service Type**: `HTTP`
- **URL**: `minio:9001`

### Route 4: MinIO API
- **Subdomain**: `raptor-minio-api`
- **Domain**: Same as above
- **Service Type**: `HTTP`
- **URL**: `minio:9000`

4. Click **"Save tunnel"**

## Step 4: Add Tunnel Token to GitHub Actions Secrets.

## Step 5: Deploy Your Application via CD Pipeline

Now that everything is configured, deploy using GitHub Actions:

### 5.1: Commit and Push Your Changes

```bash
# Stage your changes
git add .

# Commit
git commit -m "Add Cloudflare Tunnel integration for public access"

# Push to your branch
git push origin 02-cd-pipeline
```

### 5.2: Create a Release

```bash
# Create and push a version tag
git tag -a v1.0.0 -m "First production release with Cloudflare Tunnel"
git push origin v1.0.0
```

### 5.3: Publish Release on GitHub

1. Go to: `https://github.com/ncsu-ne-prag/RAPTOR/releases/new`
2. Select your tag: `v1.0.0`
3. Release title: `v1.0.0 - Production Release`
4. Add description:
   ```
   First production deployment with Cloudflare Tunnel integration
   
   Features:
   - Public HTTPS access to API, RabbitMQ, and MinIO
   - Automatic SSL certificates via Cloudflare
   - Secure tunnel from university cluster to internet
   ```
5. Click **"Publish release"**

### 5.4: Monitor the Deployment

The CD pipeline will automatically:

1. **Build Phase** (runs on GitHub-hosted runner):
   - Checkout code with submodules
   - Build Docker image
   - Push to GitHub Container Registry
   - Tag as `v1.0.0`, `v1`, and `latest`

2. **Deploy Phase** (runs on your self-hosted runner):
   - Pull the new image
   - Create configuration files from secrets
   - Create Cloudflare Tunnel Docker secret
   - Deploy all services to Docker Swarm
   - Verify tunnel connection

Watch the deployment progress:
```bash
# On your cluster, monitor the GitHub Actions runner logs
# Or watch on GitHub: https://github.com/ncsu-ne-prag/RAPTOR/actions
```

### 5.5: Verify Services are Deploying

On your cluster, check the deployment:

```bash
# Watch services come up
watch docker stack services raptor

# Check logs for each service
docker service logs raptor_cloudflared --follow
docker service logs raptor_raptor-manager --follow
```

You should see the Cloudflare tunnel connecting:
```
INF Connection registered connIndex=0
INF Connection registered connIndex=1
INF Registered tunnel connection
```

---

## Step 6: Verify Deployment

### Check service status:

```bash
# List all services (should see 5 services)
docker stack services raptor

# Expected output:
# raptor_cloudflared       1/1
# raptor_raptor-manager    1/1
# raptor_raptor-engine     4/4
# raptor_rabbitmq          1/1
# raptor_minio             1/1
```

### Check tunnel status in Cloudflare:

1. Go back to Cloudflare Dashboard → Zero Trust → Networks → Tunnels
2. Your `raptor-cluster` tunnel should show as **"Healthy"** with green status
3. Click on the tunnel to see active connections (should show 4 connections)

### Verify logs:

```bash
# Cloudflare tunnel logs
docker service logs raptor_cloudflared --tail 50

# API service logs
docker service logs raptor_raptor-manager --tail 50

# Worker logs
docker service logs raptor_raptor-engine --tail 50
```

---

## Step 7: Test Your Public Endpoints

Your application is now accessible from anywhere:

### Test the API:
```bash
curl https://raptor-api.openpra.org/q/job-types
```

### Access RabbitMQ Management:
Open in browser: `https://raptor-rmq.openpra.org`
- Default credentials: `guest` / `guest` (change these!)

### Access MinIO Console:
Open in browser: `https://raptor-minio.openpra.org`
- Default credentials: `minioadmin` / `minioadmin` (change these!)

### Test MinIO API:
```bash
curl https://raptor-minio-api.openpra.org/minio/health/live
```

---

## Step 8: Secure Your Services (Important!)

Since your services are now public, secure them:

### Change Default Passwords

Update `docker/configs/cd.stack.env`:

```bash
# RabbitMQ
RABBITMQ_DEFAULT_USER=admin
RABBITMQ_DEFAULT_PASS=your-secure-password-here

# MinIO
MINIO_ROOT_USER=admin
MINIO_ROOT_PASSWORD=your-secure-password-here
```

Then redeploy:
```bash
docker stack deploy -c docker/cd-stack.yml raptor
```

### Add Authentication with Cloudflare Access (Optional but Recommended)

1. In Cloudflare Dashboard → Zero Trust → Access → Applications
2. Click **"Add an application"**
3. Choose **"Self-hosted"**
4. Configure for RabbitMQ:
   - **Name**: RabbitMQ Management
   - **Subdomain**: `raptor-rmq`
   - **Domain**: Your domain
   - **Policy**: Add allowed emails or email domains (e.g., `@ncsu.edu`)
5. Repeat for MinIO

Now only authorized users can access these services!

---

## Step 9: Using Your Application

### From any computer with internet:

```bash
# Submit a quantification job
curl -X POST https://raptor-api.openpra.org/q/quantify/job \
  -H "Content-Type: application/json" \
  -d '{"model": "your-model-data"}'

# Check job status
curl https://raptor-api.openpra.org/q/quantify/job/{job-id}

# Access RabbitMQ to monitor queues
# Browser: https://raptor-rmq.openpra.org

# Access MinIO to view stored results
# Browser: https://raptor-minio.openpra.org
```

---

## Troubleshooting

### Tunnel shows as "Disconnected"

```bash
# Check tunnel logs
docker service logs raptor_cloudflared --follow

# Verify secret exists
docker secret ls | grep CLOUDFLARE

# Restart tunnel service
docker service update --force raptor_cloudflared
```

### Cannot access services

1. Verify services are running:
   ```bash
   docker stack ps raptor --no-trunc
   ```

2. Check if tunnel can reach services:
   ```bash
   # From cluster node
   curl http://localhost:3000/q/job-types
   curl http://localhost:15672
   ```

3. Verify Cloudflare routes match your service names exactly

### "Connection timeout" errors

- Ensure `traefik-public` and `rmq_net` networks exist and are external
- Check firewall allows outbound connections to Cloudflare (port 7844)
- Verify cluster nodes have internet access

### Services work locally but not through Cloudflare

- Double-check service names in Cloudflare routes match Docker service names
- Ensure cloudflared container is on correct networks
- Check Cloudflare tunnel health status in dashboard

---

## Updating Your Deployment

### Update application code:

```bash
# Build new image
docker build -t your-registry/raptor:latest -f docker/cd.Dockerfile .

# Push to registry
docker push your-registry/raptor:latest

# Update stack
docker stack deploy -c docker/cd-stack.yml raptor
```

### Scale workers:

Edit `docker/configs/cd.stack.env`:
```bash
NUM_WORKERS=16  # Increase/decrease as needed
```

Redeploy:
```bash
docker stack deploy -c docker/cd-stack.yml raptor
```

---

## Monitoring

### View logs:

```bash
# API logs
docker service logs raptor_raptor-manager --follow

# Worker logs
docker service logs raptor_raptor-engine --follow

# RabbitMQ logs
docker service logs raptor_rabbitmq --follow

# Tunnel logs
docker service logs raptor_cloudflared --follow
```

### Monitor resources:

```bash
# Service resource usage
docker stats

# View all running containers across cluster
docker node ls
docker service ps raptor_raptor-manager
```

---

## Cost

- **Cloudflare Tunnel**: FREE (unlimited bandwidth)
- **SSL Certificates**: FREE (automatic)
- **Domain**: FREE (use Cloudflare's subdomain) or $10/year for custom
- **Cloudflare Access**: FREE (first 50 users)

**Total: $0 - $10/year**

---

## Architecture Overview

```
Internet Users
    ↓
Cloudflare Edge Network (SSL, DDoS protection)
    ↓
Cloudflare Tunnel (secure connection)
    ↓
Your University Cluster
    ↓
Docker Swarm with Traefik
    ├── raptor-manager (API)
    ├── raptor-engine (Workers)
    ├── rabbitmq (Message Queue)
    └── minio (Object Storage)
```

---

## Summary

You now have:
- ✅ Your app deployed on university cluster
- ✅ Public HTTPS URLs with automatic SSL
- ✅ No DNS or networking knowledge required
- ✅ No firewall changes needed
- ✅ DDoS protection included
- ✅ Accessible from anywhere on the internet

**Your endpoints:**
- API: `https://raptor-api.openpra.org/q/`
- RabbitMQ: `https://raptor-rmq.openpra.org`
- MinIO: `https://raptor-minio.openpra.org`

Need help? Check Cloudflare Tunnel documentation: https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/
