const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("fs");
const os = require("os");
const path = require("path");

const { loadContract, loadGestureConfig } = require("../lib/config-loader");

test("loadGestureConfig validates against contract", () => {
  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), "gesture-config-test-"));
  const contractPath = path.join(tempDir, "contract.json");
  const configPath = path.join(tempDir, "gestures.yaml");

  fs.writeFileSync(
    contractPath,
    JSON.stringify({
      version: 1,
      gestures: ["OPEN_PALM", "FIST"],
      actions: ["TOGGLE_WIDGETS", "NEXT_LAYOUT", "IGNORE"],
      topics: { raw: "a", action: "b", status: "c" }
    }),
    "utf8"
  );

  fs.writeFileSync(
    configPath,
    [
      "version: 1",
      "device_id: test-device",
      "detection:",
      "  min_detection_confidence: 0.7",
      "  min_tracking_confidence: 0.7",
      "  stability_frames: 4",
      "  cooldown_ms: 1200",
      "  publish_fps: 15",
      "  no_hand_reset_ms: 1000",
      "mapping:",
      "  OPEN_PALM: TOGGLE_WIDGETS",
      "  FIST: NEXT_LAYOUT",
      "diagnostics:",
      "  overlay_enabled: true"
    ].join("\n"),
    "utf8"
  );

  const contract = loadContract(contractPath);
  const config = loadGestureConfig(configPath, contract);
  assert.equal(config.mapping.OPEN_PALM, "TOGGLE_WIDGETS");
  assert.equal(config.mapping.FIST, "NEXT_LAYOUT");
});
