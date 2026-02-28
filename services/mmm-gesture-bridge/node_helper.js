const NodeHelper = require("node_helper");
const mqtt = require("mqtt");
const { randomUUID } = require("crypto");

const { mapGestureToAction } = require("./lib/action-mapper");
const { loadContract, loadGestureConfig } = require("./lib/config-loader");

module.exports = NodeHelper.create({
  start() {
    this.client = null;
    this.runtimeConfig = null;
    this.gestureConfig = null;
    this.contract = null;
    this.connected = false;
  },

  socketNotificationReceived(notification, payload) {
    if (notification !== "MMM_GESTURE_BRIDGE_CONFIG") {
      return;
    }
    this.runtimeConfig = payload;
    this.initializeClient();
  },

  initializeClient() {
    if (!this.runtimeConfig) {
      return;
    }

    this.contract = loadContract(this.runtimeConfig.contractPath);
    this.gestureConfig = loadGestureConfig(this.runtimeConfig.configPath, this.contract);

    const brokerUrl = `mqtt://${this.runtimeConfig.mqttHost}:${this.runtimeConfig.mqttPort}`;
    const clientId = `mmm-gesture-bridge-${Math.random().toString(16).slice(2, 10)}`;

    this.client = mqtt.connect(brokerUrl, {
      clientId,
      username: this.runtimeConfig.mqttUsername,
      password: this.runtimeConfig.mqttPassword,
      reconnectPeriod: 1000
    });

    this.client.on("connect", () => {
      this.connected = true;
      this.sendSocketNotification("MMM_GESTURE_BROKER_STATUS", { connected: true });
      this.client.subscribe(this.contract.topics.raw, { qos: 1 });
      this.client.subscribe(this.contract.topics.status, { qos: 0 });
    });

    this.client.on("reconnect", () => {
      this.sendSocketNotification("MMM_GESTURE_BROKER_STATUS", { connected: false });
    });

    this.client.on("close", () => {
      this.connected = false;
      this.sendSocketNotification("MMM_GESTURE_BROKER_STATUS", { connected: false });
    });

    this.client.on("error", (error) => {
      console.error("[MMM-GestureBridge] MQTT error", error);
      this.sendSocketNotification("MMM_GESTURE_BROKER_STATUS", { connected: false });
    });

    this.client.on("message", (topic, messageBuffer) => {
      try {
        const payload = JSON.parse(messageBuffer.toString("utf8"));
        this.onMqttMessage(topic, payload);
      } catch (error) {
        console.error("[MMM-GestureBridge] Failed to parse MQTT payload", error);
      }
    });
  },

  onMqttMessage(topic, payload) {
    if (!this.contract || !this.gestureConfig) {
      return;
    }

    if (topic === this.contract.topics.status) {
      this.sendSocketNotification("MMM_GESTURE_STATUS", payload);
      return;
    }
    if (topic !== this.contract.topics.raw) {
      return;
    }
    if (payload.schema !== "gesture.raw.v1") {
      return;
    }

    const action = mapGestureToAction(payload.gesture, this.gestureConfig.mapping);
    this.sendSocketNotification("MMM_GESTURE_EVENT", {
      gesture: payload.gesture,
      confidence: payload.confidence,
      action,
      sourceEventId: payload.eventId
    });

    if (!action || payload.gesture === "UNKNOWN") {
      return;
    }

    const actionEvent = {
      schema: "gesture.action.v1",
      eventId: randomUUID(),
      sourceEventId: payload.eventId,
      ts: new Date().toISOString(),
      action,
      gesture: payload.gesture,
      deviceId: this.gestureConfig.device_id
    };
    this.client.publish(this.contract.topics.action, JSON.stringify(actionEvent), {
      qos: 1,
      retain: false
    });
  },

  stop() {
    if (this.client) {
      this.client.end(true);
    }
  }
});
