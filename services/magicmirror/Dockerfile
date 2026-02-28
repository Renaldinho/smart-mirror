# syntax=docker/dockerfile:1.7
FROM node:22-bookworm-slim

WORKDIR /opt/magic_mirror

ENV NPM_CONFIG_FUND=false
ENV NPM_CONFIG_AUDIT=false
ENV NPM_CONFIG_UPDATE_NOTIFIER=false

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    ca-certificates \
    git \
    make \
    g++ \
    python3 \
  && rm -rf /var/lib/apt/lists/*

# Install root dependencies in a cache-friendly layer.
COPY vendor/MagicMirror2/package.json /opt/magic_mirror/package.json
COPY vendor/MagicMirror2/package-lock.json /opt/magic_mirror/package-lock.json
RUN --mount=type=cache,target=/root/.npm \
  npm ci --omit=dev --ignore-scripts \
  || npm install --omit=dev --ignore-scripts

COPY vendor/MagicMirror2 /opt/magic_mirror

RUN mkdir -p /opt/magic_mirror/modules/MMM-GestureBridge
COPY services/mmm-gesture-bridge/package.json /opt/magic_mirror/modules/MMM-GestureBridge/package.json
COPY services/mmm-gesture-bridge/package-lock.json /opt/magic_mirror/modules/MMM-GestureBridge/package-lock.json
RUN --mount=type=cache,target=/root/.npm \
  cd /opt/magic_mirror/modules/MMM-GestureBridge \
  && npm ci --omit=dev --ignore-scripts
COPY services/mmm-gesture-bridge /opt/magic_mirror/modules/MMM-GestureBridge

COPY config/magicmirror/config.js /opt/magic_mirror/config/config.js
COPY config/magicmirror/custom.css /opt/magic_mirror/css/custom.css
COPY config/gestures.yaml /opt/magic_mirror/config/gestures.yaml
COPY shared/gesture-config/contract.json /opt/magic_mirror/shared/gesture-config/contract.json

EXPOSE 8080

CMD ["npm", "run", "server"]
