const test = require("node:test");
const assert = require("node:assert/strict");

const { mapGestureToAction, nextLayoutClass } = require("../lib/action-mapper");

test("mapGestureToAction returns mapped value", () => {
  const mapping = { OPEN_PALM: "TOGGLE_WIDGETS", UNKNOWN: "IGNORE" };
  assert.equal(mapGestureToAction("OPEN_PALM", mapping), "TOGGLE_WIDGETS");
});

test("mapGestureToAction returns null for ignored gestures", () => {
  const mapping = { UNKNOWN: "IGNORE" };
  assert.equal(mapGestureToAction("UNKNOWN", mapping), null);
});

test("nextLayoutClass cycles layout classes", () => {
  assert.equal(nextLayoutClass("layout-default"), "layout-split");
  assert.equal(nextLayoutClass("layout-split"), "layout-focus");
  assert.equal(nextLayoutClass("layout-focus"), "layout-default");
});
