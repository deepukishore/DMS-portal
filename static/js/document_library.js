let selectedPrimary = PRESELECT_PRIMARY || '';
let selectedSecondary = PRESELECT_SECONDARY || '';
let selectedTertiary = PRESELECT_TERTIARY || '';
let selectedPlant = PRESELECT_PLANT || '';
let selectedDept = PRESELECT_DEPARTMENT || '';
let currentPage = 1;
let currentPageSize = 20;
const PAGE_SIZE_OPTIONS = [10, 20, 50, 100];

function navigateToCurrentSelection() {
  const url = new URL(window.location.href);
  const state = {
    primary: selectedPrimary,
    secondary: selectedSecondary,
    tertiary: selectedTertiary,
    plant: selectedPlant,
    department: selectedDept,
  };
  Object.entries(state).forEach(([key, value]) => {
    if (value) url.searchParams.set(key, value);
    else url.searchParams.delete(key);
  });
  const destination = `${url.pathname}${url.search}`;
  const current = `${window.location.pathname}${window.location.search}`;
  if (destination !== current) {
    window.history.pushState({ documentLibrary: true }, '', destination);
  }
}

function runAndNavigate(callback, value) {
  callback(value);
  navigateToCurrentSelection();
}

function restoreSelectionFromUrl() {
  const params = new URLSearchParams(window.location.search);
  selectedPrimary = params.get('primary') || '';
  selectedSecondary = params.get('secondary') || '';
  selectedTertiary = params.get('tertiary') || '';
  selectedPlant = params.get('plant') || '';
  selectedDept = params.get('department') || '';
  currentPage = 1;
}

window.addEventListener('popstate', () => {
  restoreSelectionFromUrl();
  render();
});

const FILE_ICONS = {
  pdf: 'PDF',
  docx: 'DOC',
  doc: 'DOC',
  xlsx: 'XLS',
  xls: 'XLS',
  pptx: 'PPT',
  ppt: 'PPT',
};

function ext(name) {
  return (name.split('.').pop() || '').toLowerCase();
}

function fileIcon(name) {
  return FILE_ICONS[ext(name)] || 'FILE';
}

function formatPageRange(totalCount) {
  const start = Math.min(totalCount, (currentPage - 1) * currentPageSize + 1);
  const end = Math.min(totalCount, currentPage * currentPageSize);
  return totalCount === 0 ? 'No documents' : `Showing ${start}-${end} of ${totalCount} documents`;
}

function createPaginationBar(totalCount) {
  const pageCount = Math.max(1, Math.ceil(totalCount / currentPageSize));
  currentPage = Math.min(currentPage, pageCount);

  const wrapper = document.createElement('div');
  wrapper.className = 'pagination-bar';

  const info = document.createElement('div');
  info.className = 'pagination-info';
  info.textContent = formatPageRange(totalCount);
  wrapper.appendChild(info);

  const controls = document.createElement('div');
  controls.className = 'pagination-controls';

  const sizeSelect = document.createElement('select');
  sizeSelect.className = 'pagination-select';
  PAGE_SIZE_OPTIONS.forEach(size => {
    const option = document.createElement('option');
    option.value = size;
    option.textContent = `${size} per page`;
    if (size === currentPageSize) option.selected = true;
    sizeSelect.appendChild(option);
  });
  sizeSelect.addEventListener('change', event => {
    currentPageSize = Number(event.target.value);
    currentPage = 1;
    render();
  });

  const prevButton = document.createElement('button');
  prevButton.type = 'button';
  prevButton.textContent = 'Prev';
  prevButton.disabled = currentPage <= 1;
  prevButton.addEventListener('click', () => {
    if (currentPage > 1) {
      currentPage -= 1;
      render();
    }
  });

  const pageInfo = document.createElement('span');
  pageInfo.className = 'pagination-page';
  pageInfo.textContent = `Page ${currentPage} of ${pageCount}`;

  const nextButton = document.createElement('button');
  nextButton.type = 'button';
  nextButton.textContent = 'Next';
  nextButton.disabled = currentPage >= pageCount;
  nextButton.addEventListener('click', () => {
    if (currentPage < pageCount) {
      currentPage += 1;
      render();
    }
  });

  controls.appendChild(sizeSelect);
  controls.appendChild(prevButton);
  controls.appendChild(pageInfo);
  controls.appendChild(nextButton);
  wrapper.appendChild(controls);

  return wrapper;
}

function root() {
  return document.getElementById('library-content');
}

function setRoot() {
  const el = root();
  el.innerHTML = '';
  return el;
}

function createStepBar(labels, activeIndex) {
  const wrap = document.createElement('div');
  wrap.className = 'flow-steps';
  labels.forEach((label, index) => {
    const step = document.createElement('span');
    step.className = `flow-step${index === activeIndex ? ' active' : ''}`;
    step.textContent = `${index + 1} - ${label}`;
    wrap.appendChild(step);
  });
  return wrap;
}

function createHeader(title, subtitle, backLabel, onBack, headerAction = null) {
  const panel = document.createElement('div');
  panel.className = 'surface-panel library-browser-panel';
  panel.style.marginTop = '1rem';

  const header = document.createElement('div');
  header.className = 'asset-panel-header library-browser-header';
  header.innerHTML = `
    <div>
      <h2>${title}</h2>
    </div>`;

  const actions = document.createElement('div');
  actions.className = 'asset-panel-header-actions';

  if (headerAction?.href && headerAction?.label) {
    const link = document.createElement('a');
    link.className = headerAction.className || 'btn-primary';
    link.href = headerAction.href;
    link.textContent = headerAction.label;
    if (headerAction.download) link.setAttribute('download', '');
    actions.appendChild(link);
  }

  if (backLabel && onBack) {
    const button = document.createElement('button');
    button.className = 'btn-outline btn-sm';
    button.type = 'button';
    button.textContent = backLabel;
    button.addEventListener('click', () => runAndNavigate(onBack));
    actions.appendChild(button);
  }

  if (actions.childElementCount) header.appendChild(actions);

  panel.appendChild(header);
  if (subtitle) {
    const sub = document.createElement('p');
    sub.className = 'section-sub';
    sub.style.marginTop = '.75rem';
    sub.style.marginBottom = '1rem';
    sub.textContent = subtitle;
    panel.appendChild(sub);
  }
  return panel;
}

function createOptionGrid(options, onSelect) {
  const grid = document.createElement('div');
  grid.className = 'proc-type-grid';
  options.forEach(option => {
    const card = document.createElement('button');
    card.type = 'button';
    card.className = 'proc-type-card';
    card.innerHTML = `
      <div class="proc-type-header">${option.label}</div>`;
    card.addEventListener('click', () => runAndNavigate(onSelect, option.key));
    grid.appendChild(card);
  });
  return grid;
}

function createPlantGrid(plants, onSelect) {
  const grid = document.createElement('div');
  grid.className = 'plant-card-grid';
  plants.forEach(plant => {
    const card = document.createElement('button');
    card.type = 'button';
    card.className = 'plant-card';
    card.innerHTML = `
      <div class="plant-card-id">${plant.id || 'PLANT'}</div>
      <div class="plant-card-info">
        <strong>${plantCode(plant.label)}</strong>
      </div>
      <div class="plant-card-arrow">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>
      </div>`;
    card.addEventListener('click', () => runAndNavigate(onSelect, plant.label));
    grid.appendChild(card);
  });
  return grid;
}

function plantOptionsFor(plantFiles) {
  const labels = Object.keys(plantFiles || {});
  const configured = (CATEGORY_DATA.plant_options || [])
    .filter(plant => labels.includes(plant.label));
  const configuredLabels = new Set(configured.map(plant => plant.label));
  const additional = labels
    .filter(label => !configuredLabels.has(label))
    .map(label => ({
      id: label.split(' - ')[0] || 'PLANT',
      label,
      location: '',
    }));
  return [...configured, ...additional];
}

function createCustomerGrid(customers, onSelect) {
  const grid = document.createElement('div');
  grid.className = 'customer-card-grid';
  customers.forEach(customer => {
    const card = document.createElement('button');
    card.type = 'button';
    card.className = 'customer-card';
    card.dataset.customerName = customer;
    card.innerHTML = `
      <div class="customer-info">
        <strong>${customer}</strong>
      </div>
      <div class="plant-card-arrow">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>
      </div>`;
    card.prepend(window.CustomerBrand?.createLogo(customer, 'card') || document.createTextNode(''));
    card.addEventListener('click', () => runAndNavigate(onSelect, customer));
    grid.appendChild(card);
  });
  return grid;
}

function departmentCardLabel(department, departmentData) {
  const configuredLabel = departmentData?.label;
  return typeof configuredLabel === 'string' && configuredLabel.trim()
    ? configuredLabel.trim()
    : department;
}

function departmentCardInitials(label) {
  const code = String(label || '').split(' - ')[0].trim();
  const codeParts = code.split(/\s+/).filter(Boolean);
  const initials = codeParts.length > 1
    ? codeParts.map(part => part[0]).join('')
    : code;
  return initials.replace(/[^a-z0-9]/gi, '').slice(0, 3).toUpperCase() || 'DEP';
}

function createDepartmentGrid(departments, onSelect) {
  const grid = document.createElement('div');
  grid.className = 'customer-card-grid';
  Object.entries(departments || {}).forEach(([department, departmentData]) => {
    const departmentLabel = departmentCardLabel(department, departmentData);
    const card = document.createElement('button');
    card.type = 'button';
    card.className = 'customer-card';
    const initials = departmentCardInitials(departmentLabel);
    card.innerHTML = `
      <div class="customer-avatar" style="background:rgba(240,165,0,.12);color:var(--accent);font-size:.75rem;font-weight:700;font-family:'IBM Plex Mono',monospace">${initials}</div>
      <div class="customer-info">
        <strong>${departmentLabel}</strong>
      </div>
      <div class="plant-card-arrow">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>
      </div>`;
    card.addEventListener('click', () => runAndNavigate(onSelect, department));
    grid.appendChild(card);
  });
  return grid;
}

function createDepartmentGridForPlant(departmentList, plantDepartments, onSelect) {
  const grid = document.createElement('div');
  grid.className = 'customer-card-grid';
  (departmentList || []).forEach(department => {
    const departmentData = plantDepartments[department] || { label: department, files: [] };
    const departmentLabel = departmentCardLabel(department, departmentData);
    const card = document.createElement('button');
    card.type = 'button';
    card.className = 'customer-card';
    const initials = departmentCardInitials(departmentLabel);
    card.innerHTML = `
      <div class="customer-avatar" style="background:rgba(240,165,0,.12);color:var(--accent);font-size:.75rem;font-weight:700;font-family:'IBM Plex Mono',monospace">${initials}</div>
      <div class="customer-info">
        <strong>${departmentLabel}</strong>
      </div>
      <div class="plant-card-arrow">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>
      </div>`;
    card.addEventListener('click', () => runAndNavigate(onSelect, department));
    grid.appendChild(card);
  });
  return grid;
}

function createFileGrid(files, permissions) {
  if (!files || files.length === 0) {
    const empty = document.createElement('div');
    empty.className = 'file-view-placeholder';
    empty.innerHTML = '<p>No documents found for this selection.</p>';
    return empty;
  }

  const totalCount = files.length;
  const pageCount = Math.max(1, Math.ceil(totalCount / currentPageSize));
  currentPage = Math.min(currentPage, pageCount);
  const pagedFiles = totalCount > currentPageSize
    ? files.slice((currentPage - 1) * currentPageSize, currentPage * currentPageSize)
    : files;

  const container = document.createElement('div');

  const grid = document.createElement('div');
  grid.className = 'asset-file-grid';
  pagedFiles.forEach(fileName => {
    const card = document.createElement('div');
    card.className = 'asset-file-card';

    const isImage = ['png','jpg','jpeg','gif','webp'].includes(ext(fileName));
    let icon;
    if (isImage) {
      const img = document.createElement('img');
      img.className = 'asset-file-thumb';
      img.alt = fileName;
      img.loading = 'lazy';
      icon = img;
      const fallbackToIcon = () => {
        const span = document.createElement('span');
        span.className = 'asset-file-icon';
        span.textContent = fileIcon(fileName);
        if (img.parentNode) img.parentNode.replaceChild(span, img);
        icon = span;
      };
      fetch(`/api/preview-url?file=${encodeURIComponent(fileName)}`)
        .then(r => r.json())
        .then(d => {
          if (d.url) {
            img.src = d.url;
          } else {
            fallbackToIcon();
          }
        })
        .catch(fallbackToIcon);
    } else {
      icon = document.createElement('span');
      icon.className = 'asset-file-icon';
      icon.textContent = fileIcon(fileName);
    }

    const name = document.createElement('span');
    name.className = 'asset-file-name';
    name.textContent = fileName;

    const view = document.createElement('button');
    view.className = 'btn-view-file';
    view.type = 'button';
    view.textContent = 'View';
    view.addEventListener('click', () => logAndView(fileName));

    card.appendChild(icon);
    card.appendChild(name);
    card.appendChild(view);

    if (permissions?.can_edit) {
      const edit = document.createElement('button');
      edit.className = 'btn-view-file';
      edit.type = 'button';
      edit.textContent = 'Edit';
      edit.addEventListener('click', () => alert(`Edit access available for: ${fileName}`));
      card.appendChild(edit);
    }

    if (permissions?.can_delete) {
      const del = document.createElement('button');
      del.className = 'btn-view-file';
      del.type = 'button';
      del.textContent = 'Delete';
      del.addEventListener('click', () => alert(`Delete access available for: ${fileName}`));
      card.appendChild(del);
    }

    grid.appendChild(card);
  });
  container.appendChild(grid);
  if (totalCount > currentPageSize) {
    container.appendChild(createPaginationBar(totalCount));
  }
  return container;
}

function renderFilesView(stepLabels, activeIndex, title, subtitle, files, backLabel, onBack, permissions) {
  const el = setRoot();
  el.appendChild(createStepBar(stepLabels, activeIndex));
  const customerBanner = window.CustomerBrand?.createBanner(title);
  const panel = createHeader(title, customerBanner ? '' : subtitle, backLabel, onBack);
  if (customerBanner) panel.prepend(customerBanner);
  panel.appendChild(createFileGrid(files, permissions));
  el.appendChild(panel);
}

function renderFlatFiles(title) {
  const el = setRoot();
  const panel = createHeader(title, CATEGORY_DATA.description || '');
  panel.appendChild(createFileGrid(CATEGORY_DATA.files || []));
  el.appendChild(panel);
}

function renderFolderOptions(title, options, backLabel, onBack) {
  const el = setRoot();
  const panel = createHeader(title, CATEGORY_DATA.description || '', backLabel, onBack);
  panel.appendChild(createOptionGrid(options, key => {
    selectedPrimary = key;
    selectedSecondary = '';
    render();
  }));
  el.appendChild(panel);
}

function primaryOptions() {
  return Object.entries(CATEGORY_DATA.primary_options || {}).map(([key, value]) => ({
    key,
    label: value.label || key,
    description: value.description || '',
  }));
}

function renderPrimaryFolderCategory(title) {
  const options = CATEGORY_DATA.primary_options || {};
  if (!selectedPrimary) {
    renderFolderOptions(title, primaryOptions());
    return;
  }

  const selected = options[selectedPrimary];
  if (!selected) {
    selectedPrimary = '';
    selectedSecondary = '';
    selectedPlant = '';
    render();
    return;
  }

  if (selected.customers) {
    const customers = Object.keys(selected.customers);
    if (!selectedSecondary) {
      const el = setRoot();
      el.appendChild(createStepBar(['Select Folder', 'Select Customer', 'Browse Files'], 1));
      const panel = createHeader(
        selected.label,
        selected.description || 'Select a customer to view all related documents.',
        'Change folder',
        () => {
          selectedPrimary = '';
          selectedSecondary = '';
          render();
        }
      );
      panel.appendChild(createCustomerGrid(customers, customer => {
        selectedSecondary = customer;
        render();
      }));
      el.appendChild(panel);
      return;
    }

    renderFilesView(
      ['Select Folder', 'Select Customer', 'Browse Files'],
      2,
      selectedSecondary,
      '',
      selected.customers[selectedSecondary] || [],
      'Change customer',
      () => {
        selectedSecondary = '';
        render();
      }
    );
    return;
  }

  if (selected.secondary_options) {
    const secondaryOptions = Object.entries(selected.secondary_options).map(([key, value]) => ({
      key,
      label: value.label || key,
      description: value.description || '',
    }));
    const stepLabels = ['Select Audit Type', 'Select Folder', 'Select Plant', 'Browse Files'];

    if (!selectedSecondary) {
      const el = setRoot();
      el.appendChild(createStepBar(stepLabels, 1));
      const panel = createHeader(
        selected.label,
        selected.description || 'Select a folder to continue.',
        'Change audit type',
        () => {
          selectedPrimary = '';
          selectedSecondary = '';
          selectedPlant = '';
          render();
        }
      );
      panel.appendChild(createOptionGrid(secondaryOptions, key => {
        selectedSecondary = key;
        selectedPlant = '';
        currentPage = 1;
        render();
      }));
      el.appendChild(panel);
      return;
    }

    const secondaryFolder = selected.secondary_options[selectedSecondary];
    if (!secondaryFolder) {
      selectedSecondary = '';
      selectedPlant = '';
      render();
      return;
    }

    if (secondaryFolder.plants) {
      if (!selectedPlant) {
        const el = setRoot();
        el.appendChild(createStepBar(stepLabels, 2));
        const panel = createHeader(
          `${selected.label} / ${secondaryFolder.label || selectedSecondary}`,
          secondaryFolder.description || 'Select a plant to view its documents.',
          'Change folder',
          () => {
            selectedSecondary = '';
            selectedPlant = '';
            render();
          }
        );
        panel.appendChild(createPlantGrid(
          plantOptionsFor(secondaryFolder.plants),
          plant => {
            selectedPlant = plant;
            currentPage = 1;
            render();
          }
        ));
        el.appendChild(panel);
        return;
      }

      renderFilesView(
        stepLabels,
        3,
        `${secondaryFolder.label || selectedSecondary} / ${selectedPlant}`,
        `${selected.label} documents for ${selectedPlant}.`,
        secondaryFolder.plants[selectedPlant] || [],
        'Change plant',
        () => {
          selectedPlant = '';
          render();
        }
      );
      return;
    }

    renderFilesView(
      ['Select Audit Type', 'Select Folder', 'Browse Files'],
      2,
      secondaryFolder.label || selectedSecondary,
      secondaryFolder.description || '',
      secondaryFolder.files || [],
      'Change folder',
      () => {
        selectedSecondary = '';
        render();
      }
    );
    return;
  }

  renderFilesView(
    ['Select Folder', 'Browse Files'],
    1,
    selected.label,
    selected.description || '',
    selected.files || [],
    'Change folder',
    () => {
      selectedPrimary = '';
      selectedSecondary = '';
      selectedPlant = '';
      render();
    }
  );
}

function renderCustomerFolderCategory(title) {
  const customers = Object.keys(CATEGORY_DATA.customers || {});
  if (!selectedPrimary) {
    const el = setRoot();
    el.appendChild(createStepBar(['Select Customer', 'Browse Files'], 0));
    const panel = createHeader(title, CATEGORY_DATA.description || '');
    panel.appendChild(createCustomerGrid(customers, customer => {
      selectedPrimary = customer;
      render();
    }));
    el.appendChild(panel);
    return;
  }

  renderFilesView(
    ['Select Customer', 'Browse Files'],
    1,
    selectedPrimary,
    '',
    CATEGORY_DATA.customers[selectedPrimary] || [],
    'Change customer',
    () => {
      selectedPrimary = '';
      render();
    }
  );
}

function renderQms() {
  const scope = CATEGORY_DATA.scope || {};
  const groups = CATEGORY_DATA.document_groups || {};

  if (!selectedSecondary) {
    const allowedGroups = (scope.groups || []).map(key => ({
      key,
      label: groups[key]?.label || key,
    }));

    const el = setRoot();
    el.appendChild(createStepBar(['Select Document Type', 'Browse Files'], 0));

    const panel = createHeader(
      'Quality Documents',
      'Choose a document type to browse available files.',
      null,
      null
    );
    panel.appendChild(createOptionGrid(allowedGroups, key => {
      selectedSecondary = key;
      selectedPrimary = '';
      selectedTertiary = '';
      selectedPlant = '';
      selectedDept = '';
      currentPage = 1;
      render();
    }));
    el.appendChild(panel);
    return;
  }

  const group = groups[selectedSecondary];
  if (!group) {
    selectedPrimary = '';
    selectedSecondary = '';
    selectedTertiary = '';
    render();
    return;
  }

  if (group.secondary_options) {
    const subfolders = group.secondary_options;
    if (!selectedPrimary) {
      const options = Object.entries(subfolders).map(([key, folder]) => ({
        key,
        label: folder.label || key,
        description: folder.description || '',
      }));
      const el = setRoot();
      el.appendChild(createStepBar(['Select Document Type', 'Select Subfolder', 'Browse Files'], 1));
      const panel = createHeader(
        group.label || selectedSecondary,
        'Choose a subfolder to browse its documents.',
        'Change document type',
        () => {
          selectedPrimary = '';
          selectedSecondary = '';
          selectedTertiary = '';
          render();
        },
        selectedSecondary === 'iatf_audit'
          ? {
              label: 'External Audit NCs CAPA format',
              href: IATF_CAPA_DOWNLOAD_URL,
              download: true,
            }
          : null
      );
      panel.appendChild(createOptionGrid(options, key => {
        selectedPrimary = key;
        selectedTertiary = '';
        selectedPlant = '';
        currentPage = 1;
        render();
      }));
      el.appendChild(panel);
      return;
    }

    const subfolder = subfolders[selectedPrimary];
    if (!subfolder) {
      selectedPrimary = '';
      selectedTertiary = '';
      render();
      return;
    }

    if (subfolder.secondary_options) {
      const nestedFolders = subfolder.secondary_options;
      const stepLabels = ['Select Document Type', 'Select Audit Folder', 'Select List', 'Select Plant', 'Browse Files'];

      if (!selectedTertiary) {
        const options = Object.entries(nestedFolders).map(([key, folder]) => ({
          key,
          label: folder.label || key,
          description: folder.description || '',
        }));
        const el = setRoot();
        el.appendChild(createStepBar(stepLabels, 2));
        const panel = createHeader(
          subfolder.label || selectedPrimary,
          subfolder.description || 'Choose a list to continue.',
          'Change audit folder',
          () => {
            selectedPrimary = '';
            selectedTertiary = '';
            selectedPlant = '';
            render();
          }
        );
        panel.appendChild(createOptionGrid(options, key => {
          selectedTertiary = key;
          selectedPlant = '';
          currentPage = 1;
          render();
        }));
        el.appendChild(panel);
        return;
      }

      const nestedFolder = nestedFolders[selectedTertiary];
      if (!nestedFolder) {
        selectedTertiary = '';
        selectedPlant = '';
        render();
        return;
      }

      if (!selectedPlant) {
        const el = setRoot();
        el.appendChild(createStepBar(stepLabels, 3));
        const panel = createHeader(
          nestedFolder.label || selectedTertiary,
          nestedFolder.description || 'Select a plant to open its PDF.',
          'Change list',
          () => {
            selectedTertiary = '';
            selectedPlant = '';
            render();
          }
        );
        panel.appendChild(createPlantGrid(
          plantOptionsFor(nestedFolder.plants || {}),
          plant => {
            selectedPlant = plant;
            currentPage = 1;
            render();
          }
        ));
        el.appendChild(panel);
        return;
      }

      renderFilesView(
        stepLabels,
        4,
        `${nestedFolder.label || selectedTertiary} / ${selectedPlant}`,
        `PDF files for ${selectedPlant}.`,
        nestedFolder.plants?.[selectedPlant] || [],
        'Change plant',
        () => {
          selectedPlant = '';
          render();
        },
        scope
      );
      return;
    }

    if (subfolder.plants) {
      const stepLabels = ['Select Document Type', 'Select Audit Folder', 'Select Plant', 'Browse Files'];
      if (!selectedPlant) {
        const el = setRoot();
        el.appendChild(createStepBar(stepLabels, 2));
        const panel = createHeader(
          subfolder.label || selectedPrimary,
          subfolder.description || 'Select a plant to browse IATF Audit documents.',
          'Change audit folder',
          () => {
            selectedPrimary = '';
            selectedTertiary = '';
            selectedPlant = '';
            render();
          }
        );
        panel.appendChild(createPlantGrid(
          Object.keys(subfolder.plants).map(label => {
            const plant = (CATEGORY_DATA.plant_options || []).find(item => item.label === label);
            return plant || { id: label.split(' ')[0], label, location: '' };
          }),
          plant => {
            selectedPlant = plant;
            currentPage = 1;
            render();
          }
        ));
        el.appendChild(panel);
        return;
      }

      renderFilesView(
        stepLabels,
        3,
        `${subfolder.label || selectedPrimary} / ${selectedPlant}`,
        `IATF Audit documents for ${selectedPlant}.`,
        subfolder.plants[selectedPlant] || [],
        'Change plant',
        () => {
          selectedPlant = '';
          render();
        },
        scope
      );
      return;
    }

    renderFilesView(
      ['Select Document Type', 'Select Subfolder', 'Browse Files'],
      2,
      subfolder.label || selectedPrimary,
      subfolder.description || `Documents available in ${subfolder.label || 'this subfolder'}.`,
      subfolder.files || [],
      'Change subfolder',
      () => {
        selectedPrimary = '';
        selectedTertiary = '';
        render();
      },
      scope
    );
    return;
  }

  if (group.plant_departments) {
    const plantDepartments = group.plant_departments;
    const stepLabels = ['Select Document Type', 'Select Plant', 'Select Department', 'Browse Files'];

    if (!selectedPlant) {
      const el = setRoot();
      el.appendChild(createStepBar(stepLabels, 1));
      const panel = createHeader(
        group.label || selectedSecondary,
        'Choose a plant to browse department folders.',
        'Change document type',
        () => {
          selectedPrimary = '';
          selectedSecondary = '';
          selectedPlant = '';
          selectedDept = '';
          render();
        }
      );
      panel.appendChild(createPlantGrid(
        Object.keys(plantDepartments).map(label => {
          const plant = (CATEGORY_DATA.plant_options || []).find(item => item.label === label);
          return plant || { id: label.split(' ')[0], label, location: '' };
        }),
        plant => {
          selectedPlant = plant;
          selectedDept = '';
          currentPage = 1;
          render();
        }
      ));
      el.appendChild(panel);
      return;
    }

    const selectedPlantData = plantDepartments[selectedPlant];
    if (!selectedPlantData) {
      selectedPlant = '';
      selectedDept = '';
      render();
      return;
    }

    if (!selectedDept) {
      const el = setRoot();
      el.appendChild(createStepBar(stepLabels, 2));
      const panel = createHeader(
        `${group.label || selectedSecondary} / ${selectedPlant}`,
        'Choose a department to browse its documents.',
        '← Change plant',
        () => {
          selectedPlant = '';
          selectedDept = '';
          render();
        }
      );
      panel.appendChild(createDepartmentGridForPlant(CATEGORY_DATA.departments || [], selectedPlantData.departments || {}, department => {
        selectedDept = department;
        currentPage = 1;
        render();
      }));
      el.appendChild(panel);
      return;
    }

    const departmentData = (selectedPlantData.departments || {})[selectedDept];
    renderFilesView(
      stepLabels,
      3,
      `${group.label || selectedSecondary} / ${selectedPlant} / ${selectedDept}`,
      `${selectedDept} documents for ${selectedPlant}.`,
      departmentData?.files || [],
      '← Change department',
      () => {
        selectedDept = '';
        render();
      },
      scope
    );
    return;
  }

  renderFilesView(
    ['Select Document Type', 'Browse Files'],
    1,
    group?.label || selectedSecondary,
    `Documents available in ${group?.label || 'this category'}.`,
    group?.files || [],
    '\u2190 Change document type',
    () => { selectedPrimary = ''; selectedSecondary = ''; selectedTertiary = ''; render(); },
    scope
  );
}

function renderMasterRecords() {
  const plants = CATEGORY_DATA.plants || [];

  if (!selectedPlant) {
    const el = setRoot();
    el.appendChild(createStepBar(['Select Plant', 'Select Department', 'Browse Files'], 0));
    const panel = createHeader('Plant Wise Records', CATEGORY_DATA.description || '');

    panel.appendChild(createPlantGrid(plants, plant => {
      selectedPlant = plant;
      selectedDept = '';
      render();
    }));
    el.appendChild(panel);
    return;
  }

  if (!selectedDept) {
    renderDepartmentsForMasterRecords();
    return;
  }

  renderFilesForMasterRecords();
}

async function renderDepartmentsForMasterRecords() {
  const el = setRoot();
  el.appendChild(createStepBar(['Select Plant', 'Select Department', 'Browse Files'], 1));
  const panel = createHeader(
    selectedPlant,
    'Select a department folder to view its documents.',
    '← Change plant',
    () => { selectedPlant = ''; selectedDept = ''; render(); }
  );

  const loadingMsg = document.createElement('p');
  loadingMsg.style.cssText = 'color:var(--text-dim);font-size:.8rem;padding:.5rem 0';
  loadingMsg.textContent = 'Loading departments…';
  panel.appendChild(loadingMsg);
  el.appendChild(panel);

  const res = await fetch(`${MASTER_DEPT_URL}?${new URLSearchParams({ plant: selectedPlant })}`);
  const data = await res.json();
  panel.removeChild(loadingMsg);

  const depts = data.departments || [];
  if (!depts.length) {
    const empty = document.createElement('p');
    empty.style.cssText = 'color:var(--text-dim);font-size:.8rem';
    empty.textContent = 'No departments found for this plant.';
    panel.appendChild(empty);
    return;
  }

  const grid = document.createElement('div');
  grid.className = 'customer-card-grid';
  depts.forEach(dept => {
    const card = document.createElement('button');
    card.type = 'button';
    card.className = 'customer-card';
    const initials = dept.split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase();
    card.innerHTML = `
      <div class="customer-avatar" style="background:rgba(240,165,0,.12);color:var(--accent);font-size:.75rem;font-weight:700;font-family:'IBM Plex Mono',monospace">${initials}</div>
      <div class="customer-info">
        <strong>${dept}</strong>
      </div>
      <div class="plant-card-arrow">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>
      </div>`;
    card.addEventListener('click', () => runAndNavigate(() => { selectedDept = dept; render(); }));
    grid.appendChild(card);
  });
  panel.appendChild(grid);
}

async function renderFilesForMasterRecords() {
  const el = setRoot();
  el.appendChild(createStepBar(['Select Plant', 'Select Department', 'Browse Files'], 2));
  const panel = createHeader(
    `${selectedPlant} / ${selectedDept}`,
    'Approved records for the selected plant and department.',
    '← Change department',
    () => {
      selectedDept = '';
      render();
    }
  );
  panel.appendChild(document.createTextNode('Loading files...'));
  el.appendChild(panel);

  const params = new URLSearchParams({ plant: selectedPlant, department: selectedDept });
  const res = await fetch(`${MASTER_FILE_URL}?${params}`);
  const data = await res.json();
  panel.lastChild.remove();
  panel.appendChild(createFileGrid(data.files || []));
}

async function logAndView(fileName) {
  await fetch(VIEW_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ file_name: fileName, category: CATEGORY_KEY }),
  });
  window.location.href = `/document-view?file=${encodeURIComponent(fileName)}`;
}

function render() {
  if (CATEGORY_KEY === 'qms') {
    renderQms();
    return;
  }

  if (
    CATEGORY_KEY === 'csr'
    || CATEGORY_KEY === 'core_tools_manuals'
    || CATEGORY_KEY === 'awards_certifications'
    || CATEGORY_KEY === 'audit_nc'
  ) {
    renderPrimaryFolderCategory(CATEGORY_DATA.primary_options?.[selectedPrimary]?.label || ACTIVE_CATEGORY_LABEL || 'Document Library');
    return;
  }

  if (CATEGORY_KEY === 'customer_score_card') {
    renderCustomerFolderCategory('Customer Score Card');
    return;
  }

  if (CATEGORY_DATA.files) {
    const title = ACTIVE_CATEGORY_LABEL || 'Documents';
    renderFlatFiles(title);
  }
}

document.addEventListener('DOMContentLoaded', render);
