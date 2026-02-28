#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SERVICE_DIR="$ROOT_DIR/services/gesture-service"
VENV_DIR="$SERVICE_DIR/.venv"
SYSTEMD_DIR="$HOME/.config/systemd/user"
UNIT_NAME="smart-mirror-gesture.service"
UNIT_PATH="$SYSTEMD_DIR/$UNIT_NAME"

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required but not found." >&2
  exit 1
fi

mkdir -p "$SYSTEMD_DIR"

if [ ! -d "$VENV_DIR" ]; then
  python3 -m venv "$VENV_DIR" --system-site-packages
fi

# shellcheck source=/dev/null
source "$VENV_DIR/bin/activate"
python -m pip install --upgrade pip
pip install -e "$SERVICE_DIR"

cat >"$UNIT_PATH" <<EOF
[Unit]
Description=Smart Mirror Gesture Service (host Picamera2)
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=$ROOT_DIR
ExecStart=$ROOT_DIR/scripts/run-gesture-host.sh
Restart=always
RestartSec=2

[Install]
WantedBy=default.target
EOF

systemctl --user daemon-reload
systemctl --user enable --now "$UNIT_NAME"

echo "Installed and started $UNIT_NAME"
echo "Enable linger to start at boot without login:"
echo "  sudo loginctl enable-linger $USER"
echo "Service status:"
echo "  systemctl --user status $UNIT_NAME"
