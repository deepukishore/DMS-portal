let selectedPrimary = PRESELECT_PRIMARY || '';
let selectedSecondary = PRESELECT_SECONDARY || '';
let selectedPlant = '';
let selectedDept = '';
let currentPage = 1;
let currentPageSize = 20;
const PAGE_SIZE_OPTIONS = [10, 20, 50, 100];

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

function createHeader(title, subtitle, backLabel, onBack) {
  const panel = document.createElement('div');
  panel.className = 'surface-panel';
  panel.style.marginTop = '1rem';

  const header = document.createElement('div');
  header.className = 'asset-panel-header';
  header.innerHTML = `
    <div>
      <p class="eyebrow">Selected View</p>
      <h2>${title}</h2>
    </div>`;

  if (backLabel && onBack) {
    const button = document.createElement('button');
    button.className = 'btn-outline btn-sm';
    button.type = 'button';
    button.textContent = backLabel;
    button.addEventListener('click', onBack);
    header.appendChild(button);
  }

  const sub = document.createElement('p');
  sub.className = 'section-sub';
  sub.style.marginTop = '.75rem';
  sub.style.marginBottom = '1rem';
  sub.textContent = subtitle || '';

  panel.appendChild(header);
  panel.appendChild(sub);
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
      <div class="proc-type-header">${option.label}</div>
      <p class="proc-type-desc">${option.description || ''}</p>
      ${option.meta ? `<p class="proc-type-desc"><strong>${option.meta}</strong></p>` : ''}
      <span class="proc-type-cta">Browse documents</span>`;
    card.addEventListener('click', () => onSelect(option.key));
    grid.appendChild(card);
  });
  return grid;
}

function createCustomerGrid(customers, onSelect) {
  const grid = document.createElement('div');
  grid.className = 'customer-card-grid';
  customers.forEach(customer => {
    const card = document.createElement('button');
    card.type = 'button';
    card.className = 'customer-card';
    card.innerHTML = `
      <div class="customer-avatar">${customer.charAt(0)}</div>
      <div class="customer-info">
        <strong>${customer}</strong>
        <small>Open customer folder</small>
      </div>
      <div class="plant-card-arrow">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>
      </div>`;
    card.addEventListener('click', () => onSelect(customer));
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

    const icon = document.createElement('span');
    icon.className = 'asset-file-icon';
    icon.textContent = fileIcon(fileName);

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
  const panel = createHeader(title, subtitle, backLabel, onBack);
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
      `All documents related to ${selectedSecondary} are shown below.`,
      selected.customers[selectedSecondary] || [],
      'Change customer',
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
    `All score card files related to ${selectedPrimary} are shown below.`,
    CATEGORY_DATA.customers[selectedPrimary] || [],
    'Change customer',
    () => {
      selectedPrimary = '';
      render();
    }
  );
}

function renderQms() {
  const levels = CATEGORY_DATA.levels || {};
  const groups = CATEGORY_DATA.document_groups || {};

  // Non-admin users are locked to their assigned QMS level — skip the picker
  const lockedLevel = USER_QMS_LEVEL || 'L4';

  if (!selectedPrimary) {
    selectedPrimary = lockedLevel;
    renderQms();
    return;
  }

  // If user somehow selected a level they don't have access to, block it
  if (lockedLevel && selectedPrimary !== lockedLevel) {
    selectedPrimary = lockedLevel;
  }

  const level = levels[selectedPrimary];
  if (!level) { selectedPrimary = ''; render(); return; }

  if (!selectedSecondary) {
    const allowedGroups = (level.groups || []).map(key => ({
      key,
      label: groups[key]?.label || key,
      description: `${level.label} access: ${level.access}`,
    }));

    const el = setRoot();
    el.appendChild(createStepBar(['Select Document Type', 'Browse Files'], 0));

    // Level info banner
    const banner = document.createElement('div');
    banner.className = 'surface-panel';
    banner.style.marginBottom = '1rem';
    banner.style.padding = '.75rem 1rem';
    banner.innerHTML = `
      <div style="display:flex;align-items:center;gap:.75rem;flex-wrap:wrap">
        <span style="background:rgba(240,165,0,.12);color:var(--accent);font-family:'IBM Plex Mono',monospace;font-weight:700;font-size:.8rem;padding:.2rem .6rem;border-radius:4px">${level.label}</span>
        <span style="font-size:.8rem;color:var(--text-sub)">${level.access}</span>
        ${ level.can_edit ? '<span style="font-size:.75rem;color:var(--green);background:rgba(34,197,94,.1);padding:.15rem .5rem;border-radius:4px">Edit &amp; Delete enabled</span>' : '' }
      </div>`;
    el.appendChild(banner);

    const panel = createHeader(
      level.label,
      level.description || '',
      null,
      null
    );
    panel.appendChild(createOptionGrid(allowedGroups, key => {
      selectedSecondary = key;
      render();
    }));
    el.appendChild(panel);
    return;
  }

  const group = groups[selectedSecondary];
  renderFilesView(
    ['Select Document Type', 'Browse Files'],
    1,
    group?.label || selectedSecondary,
    `${level.label}: ${level.can_edit ? 'view, edit, delete, and approve.' : 'view-only.'}`,
    group?.files || [],
    '\u2190 Change document type',
    () => { selectedSecondary = ''; render(); },
    level
  );
}

function renderMasterRecords() {
  const plants = CATEGORY_DATA.plants || [];

  if (!selectedPlant) {
    const el = setRoot();
    el.appendChild(createStepBar(['Select Plant', 'Select Department', 'Browse Files'], 0));
    const panel = createHeader('Master Records', CATEGORY_DATA.description || '');

    const flow = document.createElement('div');
    flow.className = 'file-view-placeholder';
    flow.style.marginBottom = '1rem';
    flow.innerHTML = `<p>${(CATEGORY_DATA.approval_flow || []).join(' ')}</p>`;
    panel.appendChild(flow);

    const grid = document.createElement('div');
    grid.className = 'plant-card-grid';
    plants.forEach(plant => {
      const card = document.createElement('button');
      card.type = 'button';
      card.className = 'plant-card';
      card.innerHTML = `
        <div class="plant-card-id">${plant.id}</div>
        <div class="plant-card-info">
          <strong>${plant.label}</strong>
          <small>${plant.location || ''}</small>
        </div>
        <div class="plant-card-arrow">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>
        </div>`;
      card.addEventListener('click', () => {
        selectedPlant = plant.label;
        selectedDept = '';
        render();
      });
      grid.appendChild(card);
    });
    panel.appendChild(grid);
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
        <small>Open department folder</small>
      </div>
      <div class="plant-card-arrow">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>
      </div>`;
    card.addEventListener('click', () => { selectedDept = dept; render(); });
    grid.appendChild(card);
  });
  panel.appendChild(grid);
}

async function renderFilesForMasterRecords() {
  const el = setRoot();
  el.appendChild(createStepBar(['Select Plant', 'Select Department', 'Browse Files'], 2));
  const panel = createHeader(
    `${selectedPlant} / ${selectedDept}`,
    'Master record files for the selected plant and department.',
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
  alert(`Viewing: ${fileName}\n\nFile viewer would open here.`);
}

function render() {
  if (CATEGORY_KEY === 'qms') {
    renderQms();
    return;
  }

  if (CATEGORY_KEY === 'csr' || CATEGORY_KEY === 'awards_certifications' || CATEGORY_KEY === 'audit_nc') {
    renderPrimaryFolderCategory(CATEGORY_DATA.primary_options?.[selectedPrimary]?.label || document.querySelector('.horiz-tab.active .horiz-tab-label')?.textContent || 'Document Library');
    return;
  }

  if (CATEGORY_KEY === 'customer_score_card') {
    renderCustomerFolderCategory('Customer Score Card');
    return;
  }

  if (CATEGORY_KEY === 'master_records') {
    renderMasterRecords();
    return;
  }

  if (CATEGORY_DATA.files) {
    const title = document.querySelector('.horiz-tab.active .horiz-tab-label')?.textContent || 'Documents';
    renderFlatFiles(title);
  }
}

document.addEventListener('DOMContentLoaded', render);
