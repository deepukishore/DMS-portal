let selectedPrimary = PRESELECT_PRIMARY || '';
let selectedSecondary = PRESELECT_SECONDARY || '';

const FILE_ICONS = {
  pdf: '📄',
  docx: '📝',
  doc: '📝',
  xlsx: '📊',
  xls: '📊',
  pptx: '📑',
  ppt: '📑',
};

function ext(name) {
  return (name.split('.').pop() || '').toLowerCase();
}

function fileIcon(name) {
  return FILE_ICONS[ext(name)] || '📄';
}

function contentRoot() {
  return document.getElementById('library-content');
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

function createOptionGrid(options, onSelect) {
  const grid = document.createElement('div');
  grid.className = 'proc-type-grid';
  options.forEach(option => {
    const card = document.createElement('div');
    card.className = 'proc-type-card';
    card.innerHTML = `
      <div class="proc-type-header">${option.label}</div>
      <p class="proc-type-desc">${option.description || ''}</p>
      <span class="proc-type-cta">Browse documents →</span>`;
    card.addEventListener('click', () => onSelect(option.key));
    grid.appendChild(card);
  });
  return grid;
}

function createCustomerGrid(customers, onSelect) {
  const grid = document.createElement('div');
  grid.className = 'customer-card-grid';
  customers.forEach(customer => {
    const card = document.createElement('div');
    card.className = 'customer-card';
    card.innerHTML = `
      <div class="customer-avatar">${customer[0]}</div>
      <div class="customer-info">
        <strong>${customer}</strong>
        <small>Click to view documents</small>
      </div>
      <div class="plant-card-arrow">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>
      </div>`;
    card.addEventListener('click', () => onSelect(customer));
    grid.appendChild(card);
  });
  return grid;
}

function createHeader(title, subtitle, backLabel, onBack) {
  const wrap = document.createElement('div');
  wrap.className = 'asset-panel-header';

  const text = document.createElement('div');
  text.innerHTML = `
    <p class="eyebrow">Selected View</p>
    <h2>${title}</h2>`;
  wrap.appendChild(text);

  if (backLabel && onBack) {
    const button = document.createElement('button');
    button.className = 'btn-outline btn-sm';
    button.textContent = backLabel;
    button.addEventListener('click', onBack);
    wrap.appendChild(button);
  }

  const sub = document.createElement('p');
  sub.className = 'section-sub';
  sub.style.marginTop = '0.75rem';
  sub.style.marginBottom = '1rem';
  sub.textContent = subtitle;

  return { wrap, sub };
}

function createFileGrid(files) {
  if (!files.length) {
    const empty = document.createElement('div');
    empty.className = 'file-view-placeholder';
    empty.innerHTML = '<p>No documents found for this selection.</p>';
    return empty;
  }

  const grid = document.createElement('div');
  grid.className = 'asset-file-grid';
  files.forEach(fileName => {
    const card = document.createElement('div');
    card.className = 'asset-file-card';

    const icon = document.createElement('span');
    icon.className = 'asset-file-icon';
    icon.textContent = fileIcon(fileName);

    const name = document.createElement('span');
    name.className = 'asset-file-name';
    name.textContent = fileName;

    const button = document.createElement('button');
    button.className = 'btn-view-file';
    button.textContent = 'View';
    button.addEventListener('click', () => logAndView(fileName));

    card.appendChild(icon);
    card.appendChild(name);
    card.appendChild(button);
    grid.appendChild(card);
  });
  return grid;
}

function createGallery(files) {
  if (!files.length) {
    const empty = document.createElement('div');
    empty.className = 'file-view-placeholder';
    empty.innerHTML = '<p>No documents found.</p>';
    return empty;
  }

  const grid = document.createElement('div');
  grid.className = 'dl-gallery-grid';
  files.forEach(fileName => {
    const card = document.createElement('div');
    card.className = 'dl-gallery-card';
    card.innerHTML = `
      <div class="dl-gallery-icon">${fileIcon(fileName)}</div>
      <div class="dl-gallery-name" title="${fileName}">${fileName}</div>`;

    const button = document.createElement('button');
    button.className = 'btn-primary btn-sm dl-gallery-btn';
    button.textContent = 'View';
    button.addEventListener('click', () => logAndView(fileName));

    card.appendChild(button);
    grid.appendChild(card);
  });
  return grid;
}

function renderFilesView(stepLabels, activeIndex, title, subtitle, files, backLabel, onBack) {
  const root = contentRoot();
  root.innerHTML = '';
  root.appendChild(createStepBar(stepLabels, activeIndex));

  const panel = document.createElement('div');
  panel.className = 'surface-panel';
  panel.style.marginTop = '1rem';

  const header = createHeader(title, subtitle, backLabel, onBack);
  panel.appendChild(header.wrap);
  panel.appendChild(header.sub);
  panel.appendChild(createFileGrid(files));

  root.appendChild(panel);
}

function renderAwardsOrCertifications() {
  const root = contentRoot();
  root.innerHTML = '';

  const intro = document.createElement('div');
  intro.className = 'dl-gallery-header';
  intro.innerHTML = `<p class="section-sub">${CATEGORY_DATA.description || ''}</p>`;
  root.appendChild(intro);
  root.appendChild(createGallery(CATEGORY_DATA.files || []));
}

function renderProcedures() {
  const root = contentRoot();
  root.innerHTML = '';

  if (!selectedPrimary) {
    root.appendChild(createStepBar(['Select Procedure Type', 'Browse Files'], 0));
    root.appendChild(createOptionGrid([
      {
        key: 'cq_manuals',
        label: 'CQ Manuals - Customer Quality Manuals',
        description: CATEGORY_DATA.primary_options.cq_manuals.description,
      },
      {
        key: 'business_procedures',
        label: 'Business Procedures',
        description: CATEGORY_DATA.primary_options.business_procedures.description,
      },
    ], key => {
      selectedPrimary = key;
      selectedSecondary = '';
      render();
    }));
    return;
  }

  if (selectedPrimary === 'cq_manuals') {
    renderFilesView(
      ['Select Procedure Type', 'Browse Files'],
      1,
      'CQ Manuals - Customer Quality Manuals',
      'All documents related to CQ Manuals are shown below.',
      CATEGORY_DATA.primary_options.cq_manuals.files || [],
      'Change procedure type',
      () => {
        selectedPrimary = '';
        render();
      }
    );
    return;
  }

  if (!selectedSecondary) {
    const businessOptions = Object.entries(
      CATEGORY_DATA.primary_options.business_procedures.secondary_options || {}
    ).map(([key, value]) => ({
      key,
      label: value.label,
      description: value.description,
    }));
    root.appendChild(createStepBar(['Procedure Type', 'Select Business Procedure', 'Browse Files'], 1));

    const browser = document.createElement('div');
    browser.style.marginTop = '1rem';

    const header = createHeader(
      'Business Procedures',
      'Choose the business procedure orientation to view all related documents.',
      'Change procedure type',
      () => {
        selectedPrimary = '';
        render();
      }
    );
    browser.appendChild(header.wrap);
    browser.appendChild(header.sub);
    browser.appendChild(createOptionGrid(businessOptions, key => {
      selectedSecondary = key;
      render();
    }));
    root.appendChild(browser);
    return;
  }

  const selected = CATEGORY_DATA.primary_options.business_procedures.secondary_options[selectedSecondary];
  renderFilesView(
    ['Procedure Type', 'Business Procedure', 'Browse Files'],
    2,
    selected.label,
    `All documents related to ${selected.label} are shown below.`,
    selected.files || [],
    'Change business procedure',
    () => {
      selectedSecondary = '';
      render();
    }
  );
}

function renderManualCategory() {
  const root = contentRoot();
  root.innerHTML = '';

  const primaryOptions = CATEGORY_DATA.primary_options || {};

  if (!selectedPrimary) {
    root.appendChild(createStepBar(['Select Source', 'Browse Files'], 0));
    root.appendChild(createOptionGrid([
      {
        key: 'rane_docs',
        label: 'Rane Docs',
        description: primaryOptions.rane_docs.description,
      },
      {
        key: 'customer_docs',
        label: 'Customer Docs',
        description: primaryOptions.customer_docs.description,
      },
    ], key => {
      selectedPrimary = key;
      selectedSecondary = '';
      render();
    }));
    return;
  }

  if (selectedPrimary === 'rane_docs') {
    renderFilesView(
      ['Select Source', 'Browse Files'],
      1,
      'Rane Docs',
      'All internal documents related to this section are shown below.',
      primaryOptions.rane_docs.files || [],
      'Change source',
      () => {
        selectedPrimary = '';
        render();
      }
    );
    return;
  }

  const customerMap = primaryOptions.customer_docs.customers || {};
  const customers = Object.keys(customerMap);

  if (!selectedSecondary) {
    root.appendChild(createStepBar(['Select Source', 'Select Customer', 'Browse Files'], 1));

    const section = document.createElement('div');
    section.style.marginTop = '1rem';
    const header = createHeader(
      'Customer Docs',
      'Select a customer to view all related documents.',
      'Change source',
      () => {
        selectedPrimary = '';
        render();
      }
    );
    section.appendChild(header.wrap);
    section.appendChild(header.sub);
    section.appendChild(createCustomerGrid(customers, customer => {
      selectedSecondary = customer;
      render();
    }));
    root.appendChild(section);
    return;
  }

  renderFilesView(
    ['Select Source', 'Select Customer', 'Browse Files'],
    2,
    selectedSecondary,
    `All documents related to ${selectedSecondary} are shown below.`,
    customerMap[selectedSecondary] || [],
    'Change customer',
    () => {
      selectedSecondary = '';
      render();
    }
  );
}

async function logAndView(fileName) {
  await fetch(VIEW_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ file_name: fileName, category: CATEGORY_KEY })
  });
  alert(`Viewing: ${fileName}\n\nFile viewer would open here.`);
}

function render() {
  if (CATEGORY_KEY === 'awards' || CATEGORY_KEY === 'certifications') {
    renderAwardsOrCertifications();
    return;
  }

  if (CATEGORY_KEY === 'procedures') {
    renderProcedures();
    return;
  }

  if (CATEGORY_KEY === 'standard_manuals' || CATEGORY_KEY === 'core_tools_manuals') {
    renderManualCategory();
  }
}

document.addEventListener('DOMContentLoaded', render);
