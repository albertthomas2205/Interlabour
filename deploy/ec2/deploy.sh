#!/usr/bin/env bash
# Deploy / update on EC2. Run from repo root on the server:
#   chmod +x deploy/ec2/deploy.sh
#   ./deploy/ec2/deploy.sh docker
#   ./deploy/ec2/deploy.sh venv

set -euo pipefail

MODE="${1:-docker}"
APP_DIR="/var/www/interlabour"
REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

cd "$REPO_ROOT"

if [[ ! -f "$APP_DIR/.env" ]]; then
  echo "Missing $APP_DIR/.env — copy deploy/ec2/env.production.example first."
  exit 1
fi

if [[ "$MODE" == "docker" ]]; then
  echo "==> Building and starting Docker container..."
  docker compose -f deploy/ec2/docker-compose.yml build --no-cache
  docker compose -f deploy/ec2/docker-compose.yml up -d
  echo "==> Container logs (last 30 lines):"
  docker logs --tail 30 interlabour
elif [[ "$MODE" == "venv" ]]; then
  echo "==> Python venv deploy..."
  if [[ ! -d "$APP_DIR/venv" ]]; then
    python3 -m venv "$APP_DIR/venv"
  fi
  # shellcheck source=/dev/null
  source "$APP_DIR/venv/bin/activate"
  pip install --upgrade pip
  pip install -r requirements.txt

  set -a
  # shellcheck source=/dev/null
  source "$APP_DIR/.env"
  set +a

  python manage.py migrate --noinput
  python manage.py collectstatic --noinput
  if [[ -f staticfiles/js/main.js@v=1.0 ]]; then
    ln -sf main.js@v=1.0 staticfiles/js/main.js
  fi

  sudo cp deploy/ec2/systemd/interlabour.service /etc/systemd/system/interlabour.service
  sudo systemctl daemon-reload
  sudo systemctl enable interlabour
  sudo systemctl restart interlabour
  sudo systemctl status interlabour --no-pager
else
  echo "Usage: $0 [docker|venv]"
  exit 1
fi

echo "==> Deploy finished. Test: curl -I http://127.0.0.1:8000/health/"
