# Deploy Interlabour on AWS EC2

Stack: **EC2** (Ubuntu) + **RDS PostgreSQL** + **Zoho Mail** + **GoDaddy DNS**. No SES, no S3.

## 1. AWS — RDS

1. RDS → Create **PostgreSQL** database `interlabour_db`
2. Note endpoint, username, password
3. Security group: allow **5432** from your **EC2 security group**

`DATABASE_URL` format:

```text
postgres://USER:PASSWORD@endpoint.region.rds.amazonaws.com:5432/interlabour_db
```

## 2. AWS — EC2

1. Launch **Ubuntu 24.04**, type **t3.small**
2. Security group inbound:
   - **22** — your IP only
   - **80**, **443** — anywhere
3. Download `.pem` key pair

SSH:

```bash
ssh -i your-key.pem ubuntu@EC2_PUBLIC_IP
```

## 3. Clone project on server

```bash
sudo mkdir -p /var/www/interlabour
sudo chown ubuntu:ubuntu /var/www/interlabour
git clone YOUR_REPO_URL /var/www/interlabour
cd /var/www/interlabour
```

## 4. Environment file

```bash
cp deploy/ec2/env.production.example /var/www/interlabour/.env
nano /var/www/interlabour/.env
```

Fill in `DATABASE_URL`, `DJANGO_SECRET_KEY`, and Zoho app passwords.

Generate secret key:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

## 5. One-time server setup

**Docker (recommended — uses your Dockerfile):**

```bash
chmod +x deploy/ec2/setup-server.sh deploy/ec2/deploy.sh
./deploy/ec2/setup-server.sh docker
# log out and back in after docker group is added
./deploy/ec2/deploy.sh docker
```

**Or Python venv + systemd:**

```bash
./deploy/ec2/setup-server.sh venv
./deploy/ec2/deploy.sh venv
```

## 6. GoDaddy DNS

| Type | Name | Value |
|------|------|-------|
| A | @ | EC2 public IP |
| CNAME | www | interlabour.nl |

Keep Zoho **MX**, **SPF**, and **DKIM** records for email.

## 7. HTTPS

After DNS propagates:

```bash
sudo certbot --nginx -d interlabour.nl -d www.interlabour.nl
```

## 8. Updates (redeploy)

```bash
cd /var/www/interlabour
git pull
./deploy/ec2/deploy.sh docker
```

## Checklist

- [ ] RDS running, EC2 can connect on 5432
- [ ] `.env` on server with production values
- [ ] `curl http://127.0.0.1:8000/health/` returns 200
- [ ] Site loads at `https://www.interlabour.nl`
- [ ] Register → OTP email via Zoho

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Database connection refused | RDS security group → allow EC2 SG on 5432 |
| 502 Bad Gateway | `docker logs interlabour` or `journalctl -u interlabour` |
| OTP email fails | Check Zoho app password, `smtp.zoho.in` vs `.com` / `.eu` |
| Static files 404 | Run deploy again (collectstatic runs in entrypoint) |
