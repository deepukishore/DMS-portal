const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const fileList = document.getElementById('file-list');
const fileItems = document.getElementById('file-items');
const fileCountLabel = document.getElementById('file-count-label');
const clearBtn = document.getElementById('clear-files');
const submitBtn = document.getElementById('submit-btn');
const submitHint = document.getElementById('submit-hint');
const browseTrig = document.getElementById('browse-trigger');
const uploadForm = document.getElementById('upload-form');
const docTypeInput = document.getElementById('doc_type_input');
const customerSelect = document.getElementById('customer-select');
const customerReqStar = document.getElementById('customer-required-star');
const internalCheckbox = document.getElementById('is_internal_checkbox');
const isRevisionCb = document.getElementById('is_revision_checkbox');
const revisionFields = document.getElementById('revision-fields');
const uploadTargetRadios = document.querySelectorAll('input[name="upload_target"]');
const libraryMeta = document.getElementById('library-meta');
const libraryCatSelect = document.getElementById('library-category-select');
const librarySubSelect = document.getElementById('library-subcategory-select');
const librarySubWrapper = document.getElementById('library-sub-wrapper');
const librarySecondaryRow = document.getElementById('library-secondary-row');
const libraryTertiaryRow = document.getElementById('library-tertiary-row');
const libraryTertiaryWrapper = document.getElementById('library-tertiary-wrapper');
const libraryTertiarySelect = document.getElementById('library-tertiary-select');
const libraryPrimWrap = document.getElementById('library-primary-wrapper');
const libraryPrimSelect = document.getElementById('library-primary-select');
const librarySubHidden = document.getElementById('library-subcategory-hidden');
const libraryPathPreview = document.getElementById('library-path-preview');
const libraryPathStatus = document.getElementById('library-path-status');
const docNumInput = document.getElementById('document-number-input');
const revNumInput = document.getElementById('revision_number_input');
const plantSelect = document.getElementById('plant-select');
const deptSelect = document.getElementById('department-select');

const ALLOWED_EXTS = ['.pdf', '.docx', '.doc', '.xlsx', '.xls', '.pptx', '.ppt'];
const LIBRARY_DATA = window.LIBRARY_DATA || {};

let currentPathState = {
  valid: false,
  value: '',
  display: 'No library path selected',
  missing: '',
};
let droppedFiles = null;

function formatSize(bytes) {
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / 1048576).toFixed(1) + ' MB';
}

function assignFilesToInput(files) {
  if (!fileInput) return;
  if (typeof DataTransfer !== 'undefined') {
    const dataTransfer = new DataTransfer();
    Array.from(files).forEach(file => dataTransfer.items.add(file));
    try {
      fileInput.files = dataTransfer.files;
      droppedFiles = null;
      return;
    } catch (error) {
      // Some browsers may not allow setting input.files directly.
    }
  }
  droppedFiles = files;
}

function fileIcon(ext) {
  const colors = { pdf: '#ef4444', docx: '#3b82f6', doc: '#3b82f6', xlsx: '#22c55e', xls: '#22c55e', pptx: '#f97316', ppt: '#f97316' };
  const color = colors[ext] || 'var(--accent)';
  return `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="${color}" stroke-width="2">
    <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/>
    <polyline points="14 2 14 8 20 8"/>
  </svg>`;
}

function categoryLabel(key) {
  const option = libraryCatSelect?.querySelector(`option[value="${CSS.escape(key || '')}"]`);
  return option?.textContent || key || '';
}

function selectedOptionText(select) {
  return select?.selectedOptions?.[0]?.textContent || '';
}

function setOptions(select, placeholder, entries) {
  select.innerHTML = '';
  const empty = document.createElement('option');
  empty.value = '';
  empty.textContent = placeholder;
  select.appendChild(empty);
  entries.forEach(entry => {
    const option = document.createElement('option');
    option.value = entry.value;
    option.textContent = entry.label;
    select.appendChild(option);
  });
}

function setRequired(field, required) {
  if (!field) return;
  if (required) field.setAttribute('required', 'required');
  else field.removeAttribute('required');
}

function showField(wrapper, visible, requiredField) {
  if (wrapper) wrapper.style.display = visible ? 'block' : 'none';
  setRequired(requiredField, visible);
}

function showSecondary(visible, label = 'Subfolder') {
  if (librarySecondaryRow) librarySecondaryRow.style.display = visible ? 'flex' : 'none';
  if (librarySubWrapper) {
    const marker = librarySubWrapper.querySelector('#library-sub-required');
    librarySubWrapper.childNodes[0].textContent = `${label} `;
    if (marker) librarySubWrapper.insertBefore(marker, librarySubWrapper.childNodes[1] || null);
  }
  if (librarySubSelect) {
    librarySubSelect.style.display = visible ? 'block' : 'none';
    setRequired(librarySubSelect, visible);
  }
}

function showTertiary(visible, label = 'Subfolder') {
  if (libraryTertiaryRow) libraryTertiaryRow.style.display = visible ? 'flex' : 'none';
  if (libraryTertiaryWrapper) {
    const marker = libraryTertiaryWrapper.querySelector('#library-tertiary-required');
    libraryTertiaryWrapper.childNodes[0].textContent = `${label} `;
    if (marker) libraryTertiaryWrapper.insertBefore(marker, libraryTertiaryWrapper.childNodes[1] || null);
  }
  if (libraryTertiarySelect) {
    libraryTertiarySelect.style.display = visible ? 'block' : 'none';
    setRequired(libraryTertiarySelect, visible);
  }
}

function setPathState(valid, display, value, missing = '') {
  currentPathState = { valid, display, value, missing };
  if (librarySubHidden) librarySubHidden.value = valid ? value : '';
  if (libraryPathPreview) {
    libraryPathPreview.textContent = display;
    libraryPathPreview.classList.toggle('ready', valid);
  }
  if (libraryPathStatus) {
    libraryPathStatus.textContent = valid ? 'Ready' : 'Path required';
    libraryPathStatus.classList.toggle('ready', valid);
  }
}

function getUploadTarget() {
  const checked = document.querySelector('input[name="upload_target"]:checked') || document.querySelector('input[name="upload_target"][type="hidden"]');
  return checked ? checked.value : 'library';
}

function updateSubmitState(hasFiles) {
  submitBtn.disabled = !hasFiles;
  submitHint.style.display = hasFiles ? 'none' : 'inline';
}

function renderFiles(files) {
  fileItems.innerHTML = '';
  if (!files || files.length === 0) {
    droppedFiles = null;
    fileList.style.display = 'none';
    updateSubmitState(false);
    return;
  }

  const invalid = Array.from(files).filter(file => {
    const extension = '.' + file.name.split('.').pop().toLowerCase();
    return !ALLOWED_EXTS.includes(extension);
  });

  if (invalid.length > 0) {
    droppedFiles = null;
    showInlineError('Invalid file type(s): ' + invalid.map(file => file.name).join(', ') + '. Allowed: PDF, Word, Excel, PowerPoint.');
    fileInput.value = '';
    fileList.style.display = 'none';
    updateSubmitState(false);
    return;
  }

  fileList.style.display = 'block';
  fileCountLabel.textContent = files.length + ' file' + (files.length > 1 ? 's' : '') + ' selected';
  updateSubmitState(true);
  droppedFiles = null;

  Array.from(files).forEach(file => {
    const extension = file.name.split('.').pop().toLowerCase();
    const item = document.createElement('li');
    item.innerHTML = `${fileIcon(extension)}<span class="fi-name">${file.name}</span><span class="fi-size">${formatSize(file.size)}</span>`;
    fileItems.appendChild(item);
  });
}

function showInlineError(message) {
  let el = document.getElementById('upload-inline-error');
  if (!el) {
    el = document.createElement('div');
    el.id = 'upload-inline-error';
    el.className = 'alert alert-error';
    el.style.marginTop = '.75rem';
    dropZone.parentNode.insertBefore(el, dropZone.nextSibling);
  }
  el.textContent = message;
  el.style.display = 'flex';
  setTimeout(() => { if (el) el.style.display = 'none'; }, 5000);
}

function updateInternalUI() {
  const isInternal = internalCheckbox.checked;
  docTypeInput.value = isInternal ? 'internal' : 'external';
  customerSelect.disabled = isInternal;
  customerSelect.classList.toggle('disabled-field', isInternal);
  if (isInternal) {
    customerSelect.removeAttribute('required');
    customerSelect.value = '';
    customerReqStar.style.display = 'none';
  } else {
    customerSelect.setAttribute('required', 'required');
    customerReqStar.style.display = '';
  }
}

function resetLibraryFields() {
  showField(libraryPrimWrap, false, libraryPrimSelect);
  showSecondary(false);
  showTertiary(false);
  if (libraryPrimSelect) setOptions(libraryPrimSelect, 'Select folder', []);
  if (librarySubSelect) setOptions(librarySubSelect, 'Select subfolder', []);
  if (libraryTertiarySelect) setOptions(libraryTertiarySelect, 'Select subfolder', []);
  setPathState(false, 'No library path selected', '', 'Select a library category.');
}

function configureLibraryCategory() {
  resetLibraryFields();
  const category = libraryCatSelect.value;
  const data = LIBRARY_DATA[category];
  if (!category || !data) return;

  if (category === 'master_records') {
    updateLibraryPath();
    return;
  }

  if (data.scope && data.document_groups) {
    showField(libraryPrimWrap, false, libraryPrimSelect);
    const groups = data.scope.groups || [];
    showSecondary(true, 'Document type');
    setOptions(
      librarySubSelect,
      'Select document type',
      groups.map(key => ({ value: key, label: data.document_groups[key]?.label || key }))
    );
    setPathState(false, `${categoryLabel(category)} / Select document type`, '', 'Select document type.');
    return;
  }

  if (data.primary_options) {
    showField(libraryPrimWrap, true, libraryPrimSelect);
    setOptions(
      libraryPrimSelect,
      'Select folder',
      Object.entries(data.primary_options).map(([value, folder]) => ({ value, label: folder.label || value }))
    );
    setPathState(false, `${categoryLabel(category)} / Select folder`, '', 'Select folder.');
    return;
  }

  if (data.customers) {
    showSecondary(true, 'Customer');
    setOptions(
      librarySubSelect,
      'Select customer',
      Object.keys(data.customers).map(customer => ({ value: customer, label: customer }))
    );
    setPathState(false, `${categoryLabel(category)} / Select customer`, '', 'Select customer folder.');
    return;
  }

  if (data.files) {
    setPathState(true, categoryLabel(category), category);
  }
}

function configureLibraryPrimary() {
  const category = libraryCatSelect.value;
  const data = LIBRARY_DATA[category];
  const primary = libraryPrimSelect.value;

  showSecondary(false);
  showTertiary(false);
  if (!data || !primary) {
    configureLibraryCategory();
    return;
  }

  if (data.scope && data.document_groups) {
    const groups = data.scope.groups || [];
    showSecondary(true, 'Document type');
    setOptions(
      librarySubSelect,
      'Select document type',
      groups.map(key => ({ value: key, label: data.document_groups[key]?.label || key }))
    );
    setPathState(false, `${categoryLabel(category)} / ${selectedOptionText(libraryPrimSelect)} / Select document type`, '', 'Select document type.');
    return;
  }

  const folder = data.primary_options?.[primary];
  if (!folder) return;

  if (folder.customers) {
    showSecondary(true, 'Customer');
    setOptions(
      librarySubSelect,
      'Select customer',
      Object.keys(folder.customers).map(customer => ({ value: customer, label: customer }))
    );
    setPathState(false, `${categoryLabel(category)} / ${folder.label || primary} / Select customer`, '', 'Select customer folder.');
    return;
  }

  if (folder.secondary_options) {
    showSecondary(true, 'Subfolder');
    setOptions(
      librarySubSelect,
      'Select subfolder',
      Object.entries(folder.secondary_options).map(([value, item]) => ({ value, label: item.label || value }))
    );
    setPathState(false, `${categoryLabel(category)} / ${folder.label || primary} / Select subfolder`, '', 'Select subfolder.');
    return;
  }

  showSecondary(false);
  setPathState(true, `${categoryLabel(category)} / ${folder.label || primary}`, primary);
}

function configureLibrarySecondary() {
  showTertiary(false);
  const category = libraryCatSelect.value;
  const data = LIBRARY_DATA[category];

  if (data?.scope && data.document_groups) {
    const groupKey = librarySubSelect.value;
    const group = data.document_groups[groupKey];
    if (group?.secondary_options) {
      showTertiary(true, 'Business Procedure folder');
      setOptions(
        libraryTertiarySelect,
        'Select Business Procedure folder',
        Object.entries(group.secondary_options).map(([value, folder]) => ({
          value,
          label: folder.label || value,
        }))
      );
      setPathState(
        false,
        `${categoryLabel(category)} / ${group.label || groupKey} / Select subfolder`,
        '',
        'Select a Business Procedures subfolder.'
      );
      return;
    }
  }

  updateLibraryPath();
}

function updateLibraryPath() {
  if (getUploadTarget() !== 'library') return;
  const category = libraryCatSelect.value;
  const data = LIBRARY_DATA[category];
  if (!category || !data) {
    setPathState(false, 'No library path selected', '', 'Select a library category.');
    return;
  }

  if (category === 'master_records') {
    const plant = plantSelect.value;
    const dept = deptSelect.value;
    if (!plant || !dept) {
      setPathState(false, `${categoryLabel(category)} / Select plant / Select department`, '', 'Select plant and department for Master Records.');
      return;
    }
    setPathState(true, `${categoryLabel(category)} / ${plant} / ${dept}`, `${plant}:${dept}`);
    return;
  }

  if (data.files && !data.primary_options && !data.customers && !data.scope) {
    setPathState(true, categoryLabel(category), category);
    return;
  }

  if (data.customers) {
    const customer = librarySubSelect.value;
    if (!customer) {
      setPathState(false, `${categoryLabel(category)} / Select customer`, '', 'Select customer folder.');
      return;
    }
    setPathState(true, `${categoryLabel(category)} / ${customer}`, customer);
    return;
  }

  if (data.scope && data.document_groups) {
    const secondary = librarySubSelect.value;
    if (!secondary) {
      setPathState(false, `${categoryLabel(category)} / Select document type`, '', 'Select document type.');
      return;
    }
    const group = data.document_groups[secondary];
    if (group?.secondary_options) {
      const tertiary = libraryTertiarySelect.value;
      if (!tertiary) {
        setPathState(
          false,
          `${categoryLabel(category)} / ${group.label || secondary} / Select subfolder`,
          '',
          'Select a Business Procedures subfolder.'
        );
        return;
      }
      const subfolder = group.secondary_options[tertiary];
      setPathState(
        true,
        `${categoryLabel(category)} / ${group.label || secondary} / ${subfolder?.label || tertiary}`,
        `${secondary}:${tertiary}`
      );
      return;
    }
    setPathState(
      true,
      `${categoryLabel(category)} / ${selectedOptionText(librarySubSelect)}`,
      secondary
    );
    return;
  }

  const primary = libraryPrimSelect.value;
  if (!primary) {
    setPathState(false, `${categoryLabel(category)} / Select folder`, '', 'Select folder.');
    return;
  }

  const folder = data.primary_options?.[primary];
  if (folder?.customers) {
    const secondary = librarySubSelect.value;
    if (!secondary) {
      setPathState(false, `${categoryLabel(category)} / ${folder.label || primary} / Select customer`, '', 'Select customer.');
      return;
    }
    setPathState(
      true,
      `${categoryLabel(category)} / ${folder.label || primary} / ${selectedOptionText(librarySubSelect)}`,
      `${primary}:${secondary}`
    );
    return;
  }

  if (folder?.secondary_options) {
    const secondary = librarySubSelect.value;
    if (!secondary) {
      setPathState(false, `${categoryLabel(category)} / ${folder.label || primary} / Select subfolder`, '', 'Select subfolder.');
      return;
    }

    const secondaryFolder = folder.secondary_options[secondary];
    if (secondaryFolder?.plants) {
      const plant = plantSelect.value;
      if (!plant) {
        setPathState(
          false,
          `${categoryLabel(category)} / ${folder.label || primary} / ${selectedOptionText(librarySubSelect)} / Select plant`,
          '',
          'Select the plant for this IATF Audit document.'
        );
        return;
      }
      setPathState(
        true,
        `${categoryLabel(category)} / ${folder.label || primary} / ${secondaryFolder.label || secondary} / ${plant}`,
        `${primary}:${secondary}:${plant}`
      );
      return;
    }

    setPathState(
      true,
      `${categoryLabel(category)} / ${folder.label || primary} / ${secondaryFolder?.label || secondary}`,
      `${primary}:${secondary}`
    );
    return;
  }

  setPathState(true, `${categoryLabel(category)} / ${folder?.label || primary}`, primary);
}

function updateTargetUI() {
  const isLibrary = getUploadTarget() === 'library';
  libraryMeta.style.display = isLibrary ? 'block' : 'none';

  if (libraryCatSelect) {
    libraryCatSelect.setAttribute('required', 'required');
  }

  if (isLibrary) {
    configureLibraryCategory();
    updateLibraryPath();
  }
}

function showSuccessPopup(message, redirectUrl) {
  const popup = document.createElement('div');
  popup.className = 'success-popup';
  popup.innerHTML = `<div class="popup-content">
    <button type="button" class="popup-close" aria-label="Close success message">×</button>
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="popup-icon"><polyline points="20 6 9 17 4 12"></polyline></svg>
    <h3>${message}</h3>
    <p>Redirecting...</p>
    ${redirectUrl ? `<a class="btn-primary" href="${redirectUrl}">Go to Document Library</a>` : ''}
  </div>`;
  document.body.appendChild(popup);
  const closeButton = popup.querySelector('.popup-close');
  const dismiss = () => {
    if (popup.parentNode) popup.parentNode.removeChild(popup);
  };
  closeButton?.addEventListener('click', dismiss);
  setTimeout(() => popup.classList.add('show'), 10);
  setTimeout(() => { window.location.href = redirectUrl || window.location.href; }, 2500);
}

internalCheckbox.addEventListener('change', updateInternalUI);
libraryCatSelect?.addEventListener('change', configureLibraryCategory);
libraryPrimSelect?.addEventListener('change', configureLibraryPrimary);
librarySubSelect?.addEventListener('change', configureLibrarySecondary);
libraryTertiarySelect?.addEventListener('change', updateLibraryPath);
plantSelect?.addEventListener('change', updateLibraryPath);
deptSelect?.addEventListener('change', updateLibraryPath);

if (isRevisionCb) {
  isRevisionCb.addEventListener('change', () => {
    revisionFields.style.display = isRevisionCb.checked ? 'block' : 'none';
    if (!isRevisionCb.checked) document.getElementById('change_summary_input').value = '';
  });
}

browseTrig.addEventListener('click', () => fileInput.click());
dropZone.addEventListener('click', event => { if (event.target !== browseTrig) fileInput.click(); });
fileInput.addEventListener('change', () => renderFiles(fileInput.files));
clearBtn.addEventListener('click', () => { fileInput.value = ''; renderFiles(null); });

['dragenter', 'dragover'].forEach(eventName => dropZone.addEventListener(eventName, event => {
  event.preventDefault();
  dropZone.classList.add('drag-over');
}));

['dragleave', 'drop'].forEach(eventName => dropZone.addEventListener(eventName, event => {
  event.preventDefault();
  dropZone.classList.remove('drag-over');
}));

dropZone.addEventListener('drop', event => {
  const transfer = event.dataTransfer;
  if (transfer.files && transfer.files.length > 0) {
    assignFilesToInput(transfer.files);
    renderFiles(transfer.files);
  }
});

uploadForm.addEventListener('submit', event => {
  event.preventDefault();

  if (!docNumInput?.value.trim()) {
    showInlineError('Document number is required.');
    return;
  }

  if (getUploadTarget() === 'library') {
    updateLibraryPath();
    if (!libraryCatSelect?.value.trim()) {
      showInlineError('Category is required for Document Library uploads.');
      return;
    }
    if (!currentPathState.valid) {
      showInlineError(currentPathState.missing || 'Please select the exact Document Library folder path.');
      return;
    }
  }

  if (!internalCheckbox.checked && !customerSelect.value) {
    showInlineError('Please select a customer, or tick "Internal Document".');
    return;
  }

  const originalLabel = submitBtn.innerHTML;
  submitBtn.disabled = true;
  submitBtn.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/></svg> Uploading...`;

  const formData = new FormData(uploadForm);
  if ((!fileInput.files || fileInput.files.length === 0) && droppedFiles?.length) {
    Array.from(droppedFiles).forEach(file => formData.append('files', file));
  }

  fetch(uploadForm.action, {
    method: 'POST',
    headers: { 'X-Requested-With': 'XMLHttpRequest' },
    body: formData,
  })
    .then(response => {
      const contentType = response.headers.get('content-type') || '';
      return contentType.includes('application/json') ? response.json() : response.text();
    })
    .then(data => {
      if (typeof data === 'object' && data.ok === false) throw new Error(data.message || 'Upload failed.');
      if (typeof data === 'object' && data.ok) {
        const savedCount = Array.isArray(data.saved_files) ? data.saved_files.length : 0;
        const message = savedCount > 0
          ? `Saved ${savedCount} file${savedCount > 1 ? 's' : ''} to ${currentPathState.display}`
          : `Upload completed successfully`;
        const redirectUrl = data.redirect || '/document-library';
        showSuccessPopup(message, redirectUrl);
        return;
      }
      window.location.reload();
    })
    .catch(error => {
      submitBtn.disabled = false;
      submitBtn.innerHTML = originalLabel;
      showInlineError(error.message || 'An error occurred. Please try again.');
    });
});

updateInternalUI();
configureLibraryCategory();
updateLibraryPath();
