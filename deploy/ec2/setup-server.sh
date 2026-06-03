#!/usr/bin/env bash
# One-time EC2 setup (Ubuntu 24.04). Run on the server as ubuntu:
#   chmod +x deploy/ec2/setup-server.sh
#   ./deploy/ec2/setup-server.sh docker
#   ./deploy/ec2/setup-server.sh venv

set -euo pipefail

MODE="${1:-docker}"
APP_DIR="/var/www/interlabour"

echo "==> Installing system packages..."
sudo apt-get update
sudo apt-get install -y git nginx certbot python3-certbot-nginx

if [[ "$MODE" == "docker" ]]; then
  sudo apt-get install -y docker.io docker-compose-v2
  sudo usermod -aG docker "$USER"
  echo "Docker mode selected. Log out and back in so docker group applies."
elif [[ "$MODE" == "venv" ]]; then
  sudo apt-get install -y python3-venv python3-pip
else
  echo "Usage: $0 [docker|venv]"
  exit 1
fi

echo "==> Creating app directory..."
sudo mkdir -p "$APP_DIR/media" "$APP_DIR/staticfiles"
sudo chown -R "$USER:$USER" "$APP_DIR"

echo "==> Installing nginx site (HTTP only — run certbot after DNS points here)..."
sudo cp deploy/ec2/nginx/interlabour.conf /etc/nginx/sites-available/interlabour
sudo ln -sf /etc/nginx/sites-available/interlabour /etc/nginx/sites-enabled/interlabour
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl enable nginx
sudo systemctl reload nginx

echo ""
echo "Next steps:"
echo "  1. Clone your repo into $APP_DIR (or git pull)"
echo "  2. cp deploy/ec2/env.production.example $APP_DIR/.env && nano $APP_DIR/.env"
echo "  3. Open RDS security group: PostgreSQL 5432 from this EC2 security group"
echo "  4. Run: ./deploy/ec2/deploy.sh $MODE"
echo "  5. Point GoDaddy DNS A record @ and CNAME www to this server's public IP"
echo "  6. sudo certbot --nginx -d interlabour.nl -d www.interlabour.nl"
