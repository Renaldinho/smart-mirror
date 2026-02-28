FROM node:22-bookworm-slim

WORKDIR /opt/magic_mirror

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    ca-certificates \
    git \
    make \
    g++ \
    python3 \
  && rm -rf /var/lib/apt/lists/*

COPY vendor/MagicMirror2 /opt/magic_mirror
RUN npm ci --omit=dev --ignore-scripts \
  || npm install --omit=dev --ignore-scripts --no-audit --no-fund

COPY services/mmm-gesture-bridge /opt/magic_mirror/modules/MMM-GestureBridge
RUN cd /opt/magic_mirror/modules/MMM-GestureBridge && npm ci --omit=dev --ignore-scripts

COPY config/magicmirror/config.js /opt/magic_mirror/config/config.js
COPY config/magicmirror/custom.css /opt/magic_mirror/css/custom.css
COPY config/gestures.yaml /opt/magic_mirror/config/gestures.yaml
COPY shared/gesture-config/contract.json /opt/magic_mirror/shared/gesture-config/contract.json

EXPOSE 8080

CMD ["npm", "run", "server"]
