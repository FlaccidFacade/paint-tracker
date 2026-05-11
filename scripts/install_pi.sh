#!/usr/bin/env bash
# install_pi.sh – One-click Paint Tracker installer for Raspberry Pi Zero 2 W
#
# Run as the default user (typically `admin` or your chosen username):
#
#   bash <(curl -fsSL https://raw.githubusercontent.com/FlaccidFacade/paint-tracker/main/scripts/install_pi.sh)
#
# The script will:
#   1. Update pip and install paint-tracker from PyPI.
#   2. Install a systemd service so Paint Tracker starts on every boot.
#   3. Open port 8000 in ufw if the firewall is active.
#   4. Print the local URL where the UI is reachable.

set -euo pipefail

SERVICE_NAME="paint-tracker"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
INSTALL_USER="${SUDO_USER:-${USER}}"
PYTHON="${PYTHON:-python3}"

# ── helpers ──────────────────────────────────────────────────────────────────
info()    { echo "ℹ️  $*"; }
success() { echo "✅  $*"; }
warn()    { echo "⚠️  $*"; }
die()     { echo "❌  $*" >&2; exit 1; }

need_cmd() { command -v "$1" >/dev/null 2>&1 || die "Required command not found: $1"; }

# ── pre-flight ────────────────────────────────────────────────────────────────
need_cmd "$PYTHON"
need_cmd pip3
need_cmd systemctl

info "Installing Paint Tracker for user '${INSTALL_USER}' …"

# ── 1. Install from PyPI ──────────────────────────────────────────────────────
info "Upgrading pip …"
"$PYTHON" -m pip install --upgrade pip --quiet

info "Installing paint-tracker from PyPI …"
# Use --user so no sudo is needed; the launcher will still be on PATH via ~/.local/bin
"$PYTHON" -m pip install --upgrade paint-tracker --quiet

LAUNCHER="$(python3 -c 'import site, os; print(os.path.join(site.getusersitepackages().replace("lib/python"+__import__("sys").version[:3]+"/site-packages",""), "bin", "paint-tracker"))' 2>/dev/null || echo "$HOME/.local/bin/paint-tracker")"
# Simpler reliable path:
LAUNCHER="$HOME/.local/bin/paint-tracker"

success "paint-tracker installed: ${LAUNCHER}"

# ── 2. Create systemd service ─────────────────────────────────────────────────
info "Installing systemd service …"

sudo tee "$SERVICE_FILE" > /dev/null << EOF
[Unit]
Description=Paint Tracker – paint and stain shelf tracker
Documentation=https://github.com/FlaccidFacade/paint-tracker
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=${INSTALL_USER}
ExecStart=${LAUNCHER} --host 0.0.0.0 --port 8000 --no-update-check
Restart=on-failure
RestartSec=10
# Give uvicorn time to start before systemd considers it failed
TimeoutStartSec=30
# Store the SQLite database in the user's home directory
Environment="HOME=/home/${INSTALL_USER}"

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now "$SERVICE_NAME"

success "systemd service '${SERVICE_NAME}' enabled and started."

# ── 3. Open firewall port (best-effort) ──────────────────────────────────────
if command -v ufw >/dev/null 2>&1; then
    UFW_STATUS="$(sudo ufw status 2>/dev/null | head -1)"
    if [[ "$UFW_STATUS" == *"active"* ]]; then
        info "Opening port 8000 in ufw …"
        sudo ufw allow 8000/tcp > /dev/null
        success "Port 8000 opened."
    fi
fi

# ── 4. Done ───────────────────────────────────────────────────────────────────
LOCAL_IP="$(hostname -I 2>/dev/null | awk '{print $1}')"
echo ""
success "Paint Tracker is running!"
echo ""
echo "   🌐  Open your browser to:"
echo ""
if [[ -n "$LOCAL_IP" ]]; then
    echo "        http://${LOCAL_IP}:8000"
fi
echo "        http://$(hostname).local:8000"
echo ""
echo "   📋  Service commands:"
echo "        sudo systemctl status  ${SERVICE_NAME}"
echo "        sudo systemctl restart ${SERVICE_NAME}"
echo "        sudo journalctl -u     ${SERVICE_NAME} -f"
echo ""
