(function () {
  "use strict";

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
      kicker.textContent = plantCode(activePlant);
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
      title.textContent = plantCode(plant);
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
    initializePlantBrowser();
  });
})();
