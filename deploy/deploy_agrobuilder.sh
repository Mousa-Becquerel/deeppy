#!/usr/bin/env bash
# Bring the AGRO.Build.ER landing site online at https://deeppy.eu/agrobuilder.
#
# Run on the EC2 as:
#     cd /opt/deeppy/app && sudo git pull && sudo bash deploy/deploy_agrobuilder.sh
#
# Idempotent: safe to re-run after `git pull`s of either the main repo or
# the landing repo.

set -euo pipefail
cd "$(dirname "$0")"

LANDING_DIR="/opt/deeppy/static/deeppy-landing"

echo "=== 1. Clone / update deeppy-landing repo ==="
mkdir -p /opt/deeppy/static
if [ ! -d "${LANDING_DIR}/.git" ]; then
  git clone --depth 1 https://github.com/deeppy-tech/deeppy-landing.git "${LANDING_DIR}"
else
  git -C "${LANDING_DIR}" pull --ff-only
fi
echo "  landing repo at: $(git -C "${LANDING_DIR}" rev-parse --short HEAD)"

echo
echo "=== 2. Sanity: agribuilder folder exists + has index.html ==="
ls -la "${LANDING_DIR}/public/agribuilder/index.html" || {
  echo "ERROR: index.html missing — repo structure changed?"
  exit 1
}

echo
echo "=== 3. Rebuild web container (bakes new Caddyfile + adds /srv/static mount) ==="
docker compose -f docker-compose.prod.yml --env-file .env up -d --build web
sleep 8

echo
echo "=== 4. Confirm mount is visible inside the web container ==="
docker exec deploy-web-1 ls /srv/static/deeppy-landing/public/agribuilder/index.html \
  && echo "  mount OK" || { echo "  MOUNT MISSING"; exit 1; }

echo
echo "=== 5. External smoke test ==="
for path in "/agrobuilder/" "/agrobuilder/agribuilder-logo.jpg"; do
  code=$(curl -s -o /dev/null -w "%{http_code}" "https://deeppy.eu${path}")
  echo "  https://deeppy.eu${path}  →  HTTP ${code}"
done

# Bare /agrobuilder should 308 redirect to /agrobuilder/
code=$(curl -s -o /dev/null -w "%{http_code}" "https://deeppy.eu/agrobuilder")
echo "  https://deeppy.eu/agrobuilder  →  HTTP ${code}  (expect 308)"

# And / should still be the DPP SPA (regression check)
code=$(curl -s -o /dev/null -w "%{http_code}" "https://deeppy.eu/")
echo "  https://deeppy.eu/           →  HTTP ${code}  (DPP SPA — regression)"

echo
echo "Done."
