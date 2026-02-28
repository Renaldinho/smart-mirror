const DEFAULT_LAYOUTS = ["layout-default", "layout-split", "layout-focus"];

function mapGestureToAction(gesture, mapping) {
  const action = mapping[gesture];
  if (!action || action === "IGNORE") {
    return null;
  }
  return action;
}

function nextLayoutClass(currentClass, layouts = DEFAULT_LAYOUTS) {
  const currentIndex = layouts.indexOf(currentClass);
  if (currentIndex === -1) {
    return layouts[0];
  }
  return layouts[(currentIndex + 1) % layouts.length];
}

module.exports = {
  DEFAULT_LAYOUTS,
  mapGestureToAction,
  nextLayoutClass
};
