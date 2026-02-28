/* global config, Log, module */

const path = require("path");

const config = {
  address: "0.0.0.0",
  port: 8080,
  basePath: "/",
  ipWhitelist: [],
  language: "en",
  locale: "en-US",
  units: "metric",
  timeFormat: 24,
  useHttps: false,

  modules: [
    {
      module: "alert"
    },
    {
      module: "updatenotification",
      position: "top_bar"
    },
    {
      module: "clock",
      position: "top_left"
    },
    {
      module: "calendar",
      header: "Calendar",
      position: "top_right",
      config: {
        calendars: [
          {
            symbol: "calendar-check",
            url: "https://calendar.google.com/calendar/ical/en.usa%23holiday%40group.v.calendar.google.com/public/basic.ics"
          }
        ]
      }
    },
    {
      module: "MMM-GestureBridge",
      position: "bottom_bar",
      config: {
        mqttHost: process.env.MQTT_HOST || "mosquitto",
        mqttPort: Number(process.env.MQTT_PORT || 1883),
        mqttUsername: process.env.MQTT_USERNAME || "mirror",
        mqttPassword: process.env.MQTT_PASSWORD || "mirror-secret",
        configPath: process.env.MM_GESTURE_CONFIG_PATH || path.join(__dirname, "gestures.yaml"),
        contractPath:
          process.env.MM_GESTURE_CONTRACT_PATH ||
          path.join(__dirname, "..", "shared", "gesture-config", "contract.json"),
        diagnosticsOverlay: true
      }
    }
  ]
};

/*************** DO NOT EDIT THE LINE BELOW ***************/
if (typeof module !== "undefined") {
  module.exports = config;
}
