# Deployment Guide: Exposing Your On-Premise Cluster to the Internet

This guide shows you how to deploy your RAPTOR application on your university cluster and make it accessible from the public internet - without needing DNS knowledge, SSL certificates, or a public IP address.

## Prerequisites

- Docker Swarm cluster running on university network
- Internet connection from cluster nodes
- No public IP or domain required

---

## Step 1: Sign Up for Cloudflare

1. Go to https://dash.cloudflare.com/sign-up
2. Create an account
3. Verify your email and provide credit card information

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

sudo cloudflared service install eyJh...
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