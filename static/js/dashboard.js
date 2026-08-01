(function () {
  "use strict";

  const SVG_NS = "http://www.w3.org/2000/svg";
  const XLINK_NS = "http://www.w3.org/1999/xlink";

  function svgElement(name, attributes) {
    const element = document.createElementNS(SVG_NS, name);
    Object.entries(attributes || {}).forEach(([key, value]) => {
      element.setAttribute(key, String(value));
    });
    return element;
  }

  function appendText(parent, text, attributes) {
    const node = svgElement("text", attributes);
    node.textContent = text;
    parent.appendChild(node);
    return node;
  }

  function renderTrendChart() {
    const chart = document.getElementById("dashboard-trend-chart");
    if (!chart) return;

    const svg = chart.querySelector("svg");
    const empty = chart.querySelector(".dashboard-chart-empty");
    let points = [];
    try {
      points = JSON.parse(chart.dataset.points || "[]");
    } catch (error) {
      points = [];
    }

    if (!svg || !points.length) {
      if (empty) empty.hidden = false;
      return;
    }

    const width = 900;
    const height = 280;
    const margin = { top: 22, right: 24, bottom: 48, left: 48 };
    const plotWidth = width - margin.left - margin.right;
    const plotHeight = height - margin.top - margin.bottom;
    const maxValue = Math.max(1, ...points.map((point) => Number(point.count) || 0));
    const topValue = Math.max(4, Math.ceil(maxValue / 4) * 4);
    const stepX = points.length > 1 ? plotWidth / (points.length - 1) : plotWidth;
    const xAt = (index) => margin.left + index * stepX;
    const yAt = (value) => margin.top + plotHeight - (value / topValue) * plotHeight;

    svg.replaceChildren();

    const defs = svgElement("defs");
    const gradient = svgElement("linearGradient", { id: "dashboardTrendFill", x1: "0", y1: "0", x2: "0", y2: "1" });
    gradient.appendChild(svgElement("stop", { offset: "0%", "stop-color": "#13b8a6", "stop-opacity": ".3" }));
    gradient.appendChild(svgElement("stop", { offset: "55%", "stop-color": "#1f8ee5", "stop-opacity": ".16" }));
    gradient.appendChild(svgElement("stop", { offset: "100%", "stop-color": "#7c5ce7", "stop-opacity": ".02" }));
    defs.appendChild(gradient);
    const lineGradient = svgElement("linearGradient", { id: "dashboardTrendLine", x1: "0", y1: "0", x2: "1", y2: "0" });
    lineGradient.appendChild(svgElement("stop", { offset: "0%", "stop-color": "#13b8a6" }));
    lineGradient.appendChild(svgElement("stop", { offset: "50%", "stop-color": "#1f8ee5" }));
    lineGradient.appendChild(svgElement("stop", { offset: "100%", "stop-color": "#7c5ce7" }));
    defs.appendChild(lineGradient);
    svg.appendChild(defs);

    for (let index = 0; index <= 4; index += 1) {
      const value = (topValue / 4) * index;
      const y = yAt(value);
      svg.appendChild(svgElement("line", {
        x1: margin.left,
        x2: width - margin.right,
        y1: y,
        y2: y,
        class: "dashboard-chart-gridline",
      }));
      appendText(svg, String(Math.round(value)), {
        x: margin.left - 12,
        y: y + 4,
        "text-anchor": "end",
        class: "dashboard-chart-axis-label",
      });
    }

    const coordinates = points.map((point, index) => [xAt(index), yAt(Number(point.count) || 0)]);
    const linePath = coordinates.map((coord, index) => `${index ? "L" : "M"}${coord[0]},${coord[1]}`).join(" ");
    const areaPath = `${linePath} L${coordinates[coordinates.length - 1][0]},${margin.top + plotHeight} L${coordinates[0][0]},${margin.top + plotHeight} Z`;

    svg.appendChild(svgElement("path", { d: areaPath, class: "dashboard-chart-area" }));
    svg.appendChild(svgElement("path", { d: linePath, class: "dashboard-chart-line" }));

    points.forEach((point, index) => {
      const [x, y] = coordinates[index];
      const link = svgElement("a", {
        href: `${chart.dataset.baseUrl}?search=${encodeURIComponent(point.date)}#documents`,
        class: "dashboard-chart-point-link",
        "aria-label": `${point.count} document${Number(point.count) === 1 ? "" : "s"} uploaded on ${point.label}`,
      });
      link.setAttributeNS(XLINK_NS, "xlink:href", `${chart.dataset.baseUrl}?search=${encodeURIComponent(point.date)}#documents`);
      const target = svgElement("circle", { cx: x, cy: y, r: 11, class: "dashboard-chart-point-target" });
      const marker = svgElement("circle", { cx: x, cy: y, r: 4.5, class: "dashboard-chart-point" });
      const title = svgElement("title");
      title.textContent = `${point.label}: ${point.count} upload${Number(point.count) === 1 ? "" : "s"}. Select to view.`;
      link.appendChild(target);
      link.appendChild(marker);
      link.appendChild(title);
      svg.appendChild(link);

      if (index % 2 === 0 || index === points.length - 1) {
        appendText(svg, point.label, {
          x,
          y: height - 17,
          "text-anchor": "middle",
          class: "dashboard-chart-axis-label dashboard-chart-date-label",
        });
      }
    });

    const total = points.reduce((sum, point) => sum + (Number(point.count) || 0), 0);
    chart.setAttribute(
      "aria-label",
      `Daily document upload trend for the last 14 days. ${total} uploads in total. Select a data point to view that date.`,
    );
  }

  document.addEventListener("DOMContentLoaded", renderTrendChart);
})();
