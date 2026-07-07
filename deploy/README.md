# DeePPy — production deployment (AWS EC2)

Single-instance deploy targeting `eu-central-1` (Frankfurt). Docker Compose on
one EC2 box, Caddy in front terminating TLS (or plain HTTP for smoke tests),
SQLite persisted on an EBS volume. Postgres profile stays dormant until we
outgrow one process.

## What's in this directory

| File | Purpose |
| --- | --- |
| `Dockerfile.web` | Multi-stage Vite build → Caddy serves the SPA + reverse-proxies `/api/*` |
| `Caddyfile` | Dual-mode: HTTP on `:80` (no domain) OR auto-TLS via Let's Encrypt (`DEPLOY_DOMAIN` set) |
| `docker-compose.prod.yml` | `api` (no exposed port) + `web` (80/443). Volumes at `/opt/deeppy/*` |
| `ec2-user-data.sh` | Runs once on first boot: installs Docker + AWS CLI, mounts EBS, pulls secrets from SSM, boots the stack |

## One-time AWS setup (do these in the console)

1. **Key pair** — `deeppy-prod`, ED25519, `.pem` downloaded. ✅
2. **Security Group** — `deeppy-prod-sg`: 22 from your IP, 80 & 443 from `0.0.0.0/0`. ✅
3. **SSM Parameter Store** — 3 SecureString params (default KMS key): ✅
   - `deeppy_prod_JWT_SECRET` — `openssl rand -hex 32` output
   - `deeppy_prod_GOOGLE_API_KEY`
   - `deeppy_prod_OPENAI_API_KEY`
4. **Elastic IP** — allocate one. Note the address.
5. **IAM role** — `deeppy-prod-ec2` for EC2 service:
   - `AmazonSSMManagedInstanceCore` (SSM Agent + Session Manager)
   - `AmazonSSMReadOnlyAccess` (read the 3 params above)

## Launching the instance

*EC2 → Instances → Launch instance:*

- **Name**: `deeppy-prod`
- **AMI**: Amazon Linux 2023
- **Instance type**: `t3.small` (2 vCPU / 2 GB). Bump to `t3.medium` if the extraction workload feels tight.
- **Key pair**: `deeppy-prod`
- **Network**: default VPC + public subnet; auto-assign public IP = enabled
- **Security group**: `deeppy-prod-sg`
- **Storage**:
  - Root: 15 GB gp3 (default is fine)
  - **Add volume**: 20 GB gp3, device `/dev/sdb` — this becomes `/opt/deeppy` inside the box
- **Advanced → IAM instance profile**: `deeppy-prod-ec2`
- **Advanced → User data**: paste the contents of [`ec2-user-data.sh`](./ec2-user-data.sh), **first editing `REPO_URL`** to your git URL.

Launch. Then *EC2 → Elastic IPs → your EIP → Associate* → the new instance.

## First-boot verification

SSH in (wait ~90 s for user-data to finish):

```bash
ssh -i ~/.ssh/deeppy-prod.pem ec2-user@<ELASTIC_IP>
tail -f /var/log/deeppy-bootstrap.log     # follow the bootstrap log
docker compose -f /opt/deeppy/app/deploy/docker-compose.prod.yml ps
curl http://localhost/api/health          # should return {"status":"ok",...}
```

From your laptop:

```bash
curl http://<ELASTIC_IP>/api/health       # end-to-end sanity
```

Open `http://<ELASTIC_IP>/` in a browser — you should see the DeePPy landing page.
Register an admin, upload a doc, extract, verify against BIO-MORTAR / VERSATILE parity.

## Later: adding TLS + a real domain

Once you have a domain (say `dpp.levery.it`):

1. **DNS**: create an A record for `dpp.levery.it` → the Elastic IP. Wait for propagation (`dig dpp.levery.it +short`).
2. **On the instance**: edit `/opt/deeppy/app/deploy/.env`:
   ```
   DEPLOY_DOMAIN=dpp.levery.it
   COOKIE_SECURE=true
   ```
3. Restart Caddy:
   ```bash
   cd /opt/deeppy/app/deploy
   docker compose -f docker-compose.prod.yml --env-file .env up -d web
   ```
4. Caddy auto-issues a Let's Encrypt cert (~30 s). Confirm:
   ```bash
   curl -I https://dpp.levery.it
   ```
5. FastAPI's B5 guard is now happy (`COOKIE_SECURE=true` matches HTTPS).

## Redeploys after code changes

```bash
ssh -i ~/.ssh/deeppy-prod.pem ec2-user@<host>
cd /opt/deeppy/app
git pull
cd deploy
docker compose -f docker-compose.prod.yml --env-file .env up -d --build
docker compose -f docker-compose.prod.yml --env-file .env exec api pytest -q
```

## Backups

Enable AWS Backup on the data EBS volume (the 20 GB one attached at `/dev/sdb`):
*AWS Backup → Backup plans → Create plan → Daily, 7-day retention* → assign the volume by tag.

The root volume can be left snapshot-less; it's rebuild-from-user-data.

## Troubleshooting

| Symptom | Look at |
| --- | --- |
| `/var/log/deeppy-bootstrap.log` mentions `REPO_URL not set` | You forgot to fill in `REPO_URL` in user-data. Fix + re-run `bash /var/lib/cloud/instance/scripts/part-001` |
| SSM parameter fetch returns `AccessDenied` | IAM role missing / not attached. Check *EC2 → Instance → IAM role* |
| `curl http://<EIP>/api/health` hangs | Security group missing port 80 rule OR the instance's private DNS is what the health probe uses |
| Caddy log: `no such host` on domain mode | DNS hasn't propagated yet. Wait or verify with `dig`. |
| API startup: `Refusing to start: JWT_SECRET must be at least 32 chars` | SSM param has fewer than 32 chars. Re-generate + update. |
