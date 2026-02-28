Module.register("MMM-GestureBridge", {
  defaults: {
    mqttHost: "mosquitto",
    mqttPort: 1883,
    mqttUsername: "mirror",
    mqttPassword: "mirror-secret",
    configPath: "/opt/magic_mirror/config/gestures.yaml",
    contractPath: "/opt/magic_mirror/shared/gesture-config/contract.json",
    diagnosticsOverlay: true
  },

  start() {
    this.lastGesture = "-";
    this.lastAction = "-";
    this.lastConfidence = 0;
    this.brokerConnected = false;
    this.layoutCycle = ["layout-default", "layout-split", "layout-focus"];
    this.currentLayout = "layout-default";
    this.focusIndex = -1;
    this.focusMode = false;
    this.widgetsHidden = false;

    document.body.classList.add(this.currentLayout);
    this.sendSocketNotification("MMM_GESTURE_BRIDGE_CONFIG", this.config);
  },

  getStyles() {
    return ["MMM-GestureBridge/styles.css"];
  },

  socketNotificationReceived(notification, payload) {
    if (notification === "MMM_GESTURE_BROKER_STATUS") {
      this.brokerConnected = Boolean(payload.connected);
      this.updateDom(100);
      return;
    }
    if (notification === "MMM_GESTURE_STATUS") {
      this.brokerConnected = payload.broker === "connected";
      this.updateDom(100);
      return;
    }
    if (notification !== "MMM_GESTURE_EVENT") {
      return;
    }

    this.lastGesture = payload.gesture || "-";
    this.lastConfidence = Number(payload.confidence || 0);
    if (payload.action) {
      this.lastAction = payload.action;
      this.applyAction(payload.action);
    }
    this.updateDom(0);
  },

  applyAction(action) {
    if (action === "TOGGLE_WIDGETS") {
      this.widgetsHidden = !this.widgetsHidden;
      document.body.classList.toggle("gesture-widgets-hidden", this.widgetsHidden);
      return;
    }

    if (action === "NEXT_LAYOUT") {
      const currentIndex = this.layoutCycle.indexOf(this.currentLayout);
      const nextLayout = this.layoutCycle[(currentIndex + 1) % this.layoutCycle.length];
      this.layoutCycle.forEach((layoutClass) => document.body.classList.remove(layoutClass));
      document.body.classList.add(nextLayout);
      this.currentLayout = nextLayout;
      return;
    }

    if (action === "NEXT_WIDGET") {
      this.advanceFocusedWidget();
      return;
    }

    if (action === "TOGGLE_FOCUS_MODE") {
      this.focusMode = !this.focusMode;
      document.body.classList.toggle("gesture-focus-mode", this.focusMode);
      if (this.focusMode) {
        this.advanceFocusedWidget(true);
      } else {
        this.clearFocusedWidgets();
      }
    }
  },

  getVisibleModules() {
    const modules = Array.from(document.querySelectorAll(".module"));
    return modules.filter((element) => {
      if (element.classList.contains("MMM-GestureBridge")) {
        return false;
      }
      const style = window.getComputedStyle(element);
      return style.display !== "none" && style.visibility !== "hidden" && Number(style.opacity) > 0;
    });
  },

  clearFocusedWidgets() {
    document.querySelectorAll(".gesture-focused").forEach((element) => {
      element.classList.remove("gesture-focused");
    });
    this.focusIndex = -1;
  },

  advanceFocusedWidget(forceFirst = false) {
    const visibleModules = this.getVisibleModules();
    if (visibleModules.length === 0) {
      this.clearFocusedWidgets();
      return;
    }

    this.clearFocusedWidgets();
    if (forceFirst) {
      this.focusIndex = 0;
    } else {
      this.focusIndex = (this.focusIndex + 1) % visibleModules.length;
    }

    const target = visibleModules[this.focusIndex];
    target.classList.add("gesture-focused");
    target.scrollIntoView({ block: "center", behavior: "smooth" });
  },

  getDom() {
    const wrapper = document.createElement("div");
    wrapper.className = "mmm-gesture-overlay";

    if (!this.config.diagnosticsOverlay) {
      wrapper.style.display = "none";
      return wrapper;
    }

    const statusClass = this.brokerConnected
      ? "mmm-gesture-overlay__status mmm-gesture-overlay__status--online"
      : "mmm-gesture-overlay__status mmm-gesture-overlay__status--offline";
    const statusLabel = this.brokerConnected ? "online" : "offline";

    wrapper.innerHTML = `
      <div>Gesture: <strong>${this.lastGesture}</strong></div>
      <div>Action: <strong>${this.lastAction}</strong></div>
      <div>Confidence: <strong>${this.lastConfidence.toFixed(2)}</strong></div>
      <div>Broker <span class="${statusClass}">${statusLabel}</span></div>
    `;
    return wrapper;
  }
});
