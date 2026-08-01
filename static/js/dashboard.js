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

  function initializePlantBrowser() {
    const browser = document.getElementById("dashboard-plant-browser");
    if (!browser) return;

    const plantButtons = document.getElementById("dashboard-plant-buttons");
    const panel = document.getElementById("dashboard-folder-panel");
    const backButton = document.getElementById("dashboard-folder-back");
    const title = document.getElementById("dashboard-folder-title");
    const description = document.getElementById("dashboard-folder-description");
    const kicker = document.getElementById("dashboard-folder-kicker");
    const departmentGrid = document.getElementById("dashboard-department-folders");
    const filesGrid = document.getElementById("dashboard-plant-files");
    const status = document.getElementById("dashboard-folder-status");
    let activePlant = "";

    const setStatus = (message, isError = false) => {
      status.textContent = message;
      status.classList.toggle("is-error", isError);
    };

    const showPlants = () => {
      activePlant = "";
      plantButtons.hidden = false;
      panel.hidden = true;
      departmentGrid.replaceChildren();
      filesGrid.replaceChildren();
      filesGrid.hidden = true;
      setStatus("");
      document.querySelectorAll(".dashboard-plant-button.is-active").forEach(button => button.classList.remove("is-active"));
    };

    const createDepartmentFolder = (department) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "dashboard-department-folder";

      const icon = document.createElement("span");
      icon.className = "dashboard-folder-icon";
      icon.setAttribute("aria-hidden", "true");
      icon.textContent = "▰";

      const copy = document.createElement("span");
      const name = document.createElement("strong");
      name.textContent = department;
      const help = document.createElement("small");
      help.textContent = "Open department folder";
      copy.append(name, help);

      const arrow = document.createElement("span");
      arrow.className = "dashboard-folder-arrow";
      arrow.setAttribute("aria-hidden", "true");
      arrow.textContent = "→";
      button.append(icon, copy, arrow);
      button.addEventListener("click", () => loadFiles(department));
      return button;
    };

    const openFile = async (fileName, department) => {
      try {
        await fetch(browser.dataset.viewUrl, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ file_name: fileName, plant: activePlant, department }),
        });
      } finally {
        window.location.href = `/document-view?file=${encodeURIComponent(fileName)}`;
      }
    };

    const createFileCard = (fileName, department) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "dashboard-plant-file";
      const extension = fileName.includes(".") ? fileName.split(".").pop().toUpperCase() : "FILE";

      const badge = document.createElement("span");
      badge.className = "dashboard-file-type";
      badge.textContent = extension;
      const copy = document.createElement("span");
      const name = document.createElement("strong");
      name.textContent = fileName;
      const help = document.createElement("small");
      help.textContent = "Open document";
      copy.append(name, help);
      const arrow = document.createElement("span");
      arrow.className = "dashboard-folder-arrow";
      arrow.setAttribute("aria-hidden", "true");
      arrow.textContent = "↗";
      button.append(badge, copy, arrow);
      button.addEventListener("click", () => openFile(fileName, department));
      return button;
    };

    async function loadFiles(department) {
      kicker.textContent = activePlant;
      title.textContent = department;
      description.textContent = "Approved documents in this department folder.";
      departmentGrid.hidden = true;
      filesGrid.hidden = false;
      filesGrid.replaceChildren();
      backButton.textContent = "← Departments";
      backButton.dataset.mode = "departments";
      setStatus("Loading files…");

      try {
        const query = new URLSearchParams({ plant: activePlant, department });
        const response = await fetch(`${browser.dataset.fileUrl}?${query}`);
        if (!response.ok) throw new Error("Unable to load files");
        const data = await response.json();
        const files = data.files || [];
        files.forEach(fileName => filesGrid.appendChild(createFileCard(fileName, department)));
        setStatus(files.length ? `${files.length} approved file${files.length === 1 ? "" : "s"} available.` : "No approved files are available in this folder yet.");
      } catch (error) {
        setStatus("The files could not be loaded. Please try again.", true);
      }
    }

    async function loadDepartments(plant, sourceButton) {
      activePlant = plant;
      document.querySelectorAll(".dashboard-plant-button.is-active").forEach(button => button.classList.remove("is-active"));
      sourceButton.classList.add("is-active");
      plantButtons.hidden = true;
      panel.hidden = false;
      departmentGrid.hidden = false;
      filesGrid.hidden = true;
      departmentGrid.replaceChildren();
      filesGrid.replaceChildren();
      kicker.textContent = "Departments";
      title.textContent = plant;
      description.textContent = "Open a department folder to see its approved documents.";
      backButton.textContent = "← All plants";
      backButton.dataset.mode = "plants";
      setStatus("Loading departments…");

      try {
        const query = new URLSearchParams({ plant });
        const response = await fetch(`${browser.dataset.departmentUrl}?${query}`);
        if (!response.ok) throw new Error("Unable to load departments");
        const data = await response.json();
        const departments = data.departments || [];
        departments.forEach(department => departmentGrid.appendChild(createDepartmentFolder(department)));
        setStatus(departments.length ? `${departments.length} department folder${departments.length === 1 ? "" : "s"} available.` : "No departments are available for this plant.");
      } catch (error) {
        setStatus("The departments could not be loaded. Please try again.", true);
      }
    }

    plantButtons.querySelectorAll(".dashboard-plant-button").forEach(button => {
      button.addEventListener("click", () => loadDepartments(button.dataset.plant, button));
    });

    backButton.addEventListener("click", () => {
      if (backButton.dataset.mode === "departments") {
        const activeButton = Array.from(plantButtons.querySelectorAll(".dashboard-plant-button"))
          .find(button => button.dataset.plant === activePlant);
        if (activeButton) loadDepartments(activePlant, activeButton);
        return;
      }
      showPlants();
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    renderTrendChart();
    initializePlantBrowser();
  });
})();
