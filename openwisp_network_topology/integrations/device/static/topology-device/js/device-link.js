"use strict";
// Adds a "View device" button to the details of a node that has a
// related device. The device comes in each node's "device" key, which
// is taken off the node before the graph uses the data, so it is not
// listed among the node details.
window.netjsongraphExtensions = window.netjsongraphExtensions || [];
window.netjsongraphExtensions.push(function (graph) {
  const devices = new Map();
  const prepareData = graph.config.prepareData;
  graph.config.prepareData = function (data) {
    (data.nodes || []).forEach(function (node) {
      if (node.device) {
        devices.set(node.id, node.device);
        delete node.device;
      } else {
        devices.delete(node.id);
      }
    });
    return prepareData.apply(this, arguments);
  };
  const onClickElement = graph.config.onClickElement;
  graph.config.onClickElement = function (type, data) {
    onClickElement.apply(this, arguments);
    const device = type === "node" && data ? devices.get(data.id) : null;
    const container = this.el.querySelector(".njg-infoContainer");
    if (!device || !container) {
      return;
    }
    const link = document.createElement("a");
    link.className = "button njg-device-link";
    link.href = device.url;
    link.textContent =
      typeof gettext === "function" ? gettext("View device") : "View device";
    container.appendChild(link);
  };
});
