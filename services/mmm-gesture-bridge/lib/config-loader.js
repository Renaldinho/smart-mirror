const fs = require("fs");
const yaml = require("js-yaml");

function loadContract(contractPath) {
  const raw = fs.readFileSync(contractPath, "utf8");
  const contract = JSON.parse(raw);
  if (contract.version !== 1) {
    throw new Error(`Unsupported gesture contract version: ${contract.version}`);
  }
  return contract;
}

function loadGestureConfig(configPath, contract) {
  const raw = fs.readFileSync(configPath, "utf8");
  const config = yaml.load(raw);

  if (config.version !== contract.version) {
    throw new Error(
      `Config version ${config.version} does not match contract version ${contract.version}`
    );
  }
  if (!config.mapping || typeof config.mapping !== "object") {
    throw new Error("Gesture config mapping is missing");
  }

  for (const gesture of contract.gestures) {
    if (!(gesture in config.mapping)) {
      throw new Error(`Missing mapping for gesture ${gesture}`);
    }
  }
  for (const [gesture, action] of Object.entries(config.mapping)) {
    if (!contract.gestures.includes(gesture)) {
      throw new Error(`Unsupported gesture in config mapping: ${gesture}`);
    }
    if (!contract.actions.includes(action)) {
      throw new Error(`Unsupported action in config mapping: ${action}`);
    }
  }

  return config;
}

module.exports = {
  loadContract,
  loadGestureConfig
};
