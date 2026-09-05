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
const libraryQuaternaryRow = document.getElementById('library-quaternary-row');
const libraryQuaternaryWrapper = document.getElementById('library-quaternary-wrapper');
const libraryQuaternarySelect = document.getElementById('library-quaternary-select');
const libraryPrimWrap = document.getElementById('library-primary-wrapper');
const libraryPrimSelect = document.getElementById('library-primary-select');
const librarySubHidden = document.getElementById('library-subcategory-hidden');
const libraryPathPreview = document.getElementById('library-path-preview');
const libraryPathStatus = document.getElementById('library-path-status');
const docNumInput = document.getElementById('document-number-input');
const docNumLabel = document.getElementById('document-number-label');
const docNumHint = document.getElementById('document-number-hint');
const docNumValidation = document.getElementById('document-number-validation');
const revNumInput = document.getElementById('revision_number_input');
const plantSelect = document.getElementById('plant-select');
const deptSelect = document.getElementById('department-select');

const ALLOWED_EXTS = ['.pdf', '.docx', '.doc', '.xlsx', '.xls', '.pptx', '.ppt'];
const LIBRARY_DATA = window.LIBRARY_DATA || {};
const NEXT_DOCUMENT_NUMBERS = window.NEXT_DOCUMENT_NUMBERS || {};
const PROFILE_NEXT_DOCUMENT_NUMBER = window.PROFILE_NEXT_DOCUMENT_NUMBER || '';
const DOCUMENT_NUMBER_VALIDATION_URL = window.DOCUMENT_NUMBER_VALIDATION_URL || '';
const REVISION_PREFILL = window.REVISION_PREFILL || null;

let currentPathState = {
  valid: false,
  value: '',
  display: 'No library path selected',
  missing: '',
};
let droppedFiles = null;
let hasSelectedFiles = false;
let revisionDocumentValidated = false;
let documentValidationTimer = null;
let documentValidationRequest = 0;
let documentValidationMessageTimer = null;

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

function showPrimary(visible, label = 'Folder') {
  showField(libraryPrimWrap, visible, libraryPrimSelect);
  if (libraryPrimWrap) {
    const marker = libraryPrimWrap.querySelector('#library-primary-required');
    libraryPrimWrap.childNodes[0].textContent = `${label} `;
    if (marker) libraryPrimWrap.insertBefore(marker, libraryPrimWrap.childNodes[1] || null);
  }
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

function showQuaternary(visible, label = 'List') {
  if (libraryQuaternaryRow) libraryQuaternaryRow.style.display = visible ? 'flex' : 'none';
  if (libraryQuaternaryWrapper) {
    const marker = libraryQuaternaryWrapper.querySelector('#library-quaternary-required');
    libraryQuaternaryWrapper.childNodes[0].textContent = `${label} `;
    if (marker) libraryQuaternaryWrapper.insertBefore(marker, libraryQuaternaryWrapper.childNodes[1] || null);
  }
  if (libraryQuaternarySelect) {
    libraryQuaternarySelect.style.display = visible ? 'block' : 'none';
    setRequired(libraryQuaternarySelect, visible);
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

function updateSubmitState(hasFiles = hasSelectedFiles) {
  hasSelectedFiles = Boolean(hasFiles);
  const revisionReady = !isRevisionCb?.checked || revisionDocumentValidated;
  submitBtn.disabled = !hasSelectedFiles || !revisionReady;
  submitHint.style.display = submitBtn.disabled ? 'inline' : 'none';
  if (!hasSelectedFiles) {
    submitHint.textContent = 'Select at least one file to continue';
  } else if (!revisionReady) {
    submitHint.textContent = 'Verify the existing document number to continue';
  }
}

function setDocumentValidation(state, message = '') {
  if (!docNumValidation) return;
  if (documentValidationMessageTimer) {
    clearTimeout(documentValidationMessageTimer);
    documentValidationMessageTimer = null;
  }
  docNumValidation.className = `document-number-validation${state ? ` is-${state}` : ''}`;
  docNumValidation.textContent = message;
  if ((state === 'valid' || state === 'error') && message) {
    documentValidationMessageTimer = setTimeout(() => {
      docNumValidation.className = 'document-number-validation';
      docNumValidation.textContent = '';
      documentValidationMessageTimer = null;
    }, 3200);
  }
}

async function validateRevisionDocument() {
  if (!isRevisionCb?.checked || !docNumInput) return;
  const documentNumber = docNumInput.value.trim();
  if (!/^ZRAI-DOC-P[1-4]-\d{4}-\d{3,}$/i.test(documentNumber)) {
    revisionDocumentValidated = false;
    if (revNumInput) revNumInput.value = '';
    setDocumentValidation('error', 'Enter a complete document number to verify it.');
    updateSubmitState();
    return;
  }

  const requestId = ++documentValidationRequest;
  revisionDocumentValidated = false;
  if (revNumInput) revNumInput.value = '';
  setDocumentValidation('checking', 'Checking document number...');
  updateSubmitState();

  try {
    const params = new URLSearchParams({
      document_number: documentNumber,
      plant: plantSelect?.value || '',
    });
    const response = await fetch(`${DOCUMENT_NUMBER_VALIDATION_URL}?${params.toString()}`, {
      headers: { 'X-Requested-With': 'XMLHttpRequest' },
    });
    const data = await response.json();
    if (requestId !== documentValidationRequest) return;
    if (!response.ok || !data.ok) throw new Error(data.message || 'Document number could not be verified.');

    revisionDocumentValidated = true;
    if (revNumInput) revNumInput.value = data.document?.next_revision_number || '';
    const details = [data.document?.file_name, data.document?.revision_number].filter(Boolean).join(' · ');
    setDocumentValidation('valid', details ? `Verified: ${details}` : 'Document verified.');
  } catch (error) {
    if (requestId !== documentValidationRequest) return;
    revisionDocumentValidated = false;
    if (revNumInput) revNumInput.value = '';
    setDocumentValidation('error', error.message || 'Document number could not be verified.');
  }
  updateSubmitState();
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

function resetLibraryFields() {
  showPrimary(false);
  showSecondary(false);
  showTertiary(false);
  showQuaternary(false);
  if (libraryPrimSelect) setOptions(libraryPrimSelect, 'Select folder', []);
  if (librarySubSelect) setOptions(librarySubSelect, 'Select subfolder', []);
  if (libraryTertiarySelect) setOptions(libraryTertiarySelect, 'Select subfolder', []);
  if (libraryQuaternarySelect) setOptions(libraryQuaternarySelect, 'Select folder', []);
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
    showPrimary(false);
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
    showPrimary(true);
    setOptions(
      libraryPrimSelect,
      'Select folder',
      Object.entries(data.primary_options).map(([value, folder]) => ({ value, label: folder.label || value }))
    );
    setPathState(false, `${categoryLabel(category)} / Select folder`, '', 'Select folder.');
    return;
  }

  if (data.customers) {
    showSecondary(false);
    showPrimary(true, 'Customer');
    setOptions(
      libraryPrimSelect,
      'Select customer',
      Object.keys(data.customers).map(customer => ({ value: customer, label: customer }))
    );
    setPathState(false, `${categoryLabel(category)} / Select customer`, '', 'Select a customer folder.');
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
  showQuaternary(false);
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

  if (data.customers) {
    updateLibraryPath();
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
    setPathState(
      false,
      `${categoryLabel(category)} / ${folder.label || primary} / Select customer`,
      '',
      'Select a customer folder.'
    );
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
  showQuaternary(false);
  const category = libraryCatSelect.value;
  const data = LIBRARY_DATA[category];

  if (data?.scope && data.document_groups) {
    const groupKey = librarySubSelect.value;
    const group = data.document_groups[groupKey];
    if (group?.secondary_options) {
      const isAuditFolder = groupKey === 'iatf_audit';
      showTertiary(true, isAuditFolder ? 'Audit type' : 'Business Procedure folder');
      setOptions(
        libraryTertiarySelect,
        isAuditFolder ? 'Select Internal Audit or External Audit' : 'Select Business Procedure folder',
        Object.entries(group.secondary_options).map(([value, folder]) => ({
          value,
          label: folder.label || value,
        }))
      );
      setPathState(
        false,
        `${categoryLabel(category)} / ${group.label || groupKey} / ${isAuditFolder ? 'Select audit type' : 'Select subfolder'}`,
        '',
        isAuditFolder ? 'Select Internal Audit or External Audit.' : 'Select a Business Procedures subfolder.'
      );
      return;
    }
    // Handle groups that expose plant -> department folders (plant_departments)
    if (group?.plant_departments) {
      const plant = plantSelect?.value;
      const dept = deptSelect?.value;
      if (!plant) {
        setPathState(false, `${categoryLabel(category)} / ${group.label || groupKey} / Select plant`, '', 'Select plant.');
        return;
      }
      if (!dept) {
        setPathState(false, `${categoryLabel(category)} / ${group.label || groupKey} / ${plantCode(plant)} / Select department`, '', 'Select department.');
        return;
      }
      setPathState(true, `${categoryLabel(category)} / ${group.label || groupKey} / ${plantCode(plant)} / ${dept}`, `${groupKey}:${plant}:${dept}`);
      return;
    }
  }

  updateLibraryPath();
}

function configureLibraryTertiary() {
  showQuaternary(false);
  const category = libraryCatSelect.value;
  const data = LIBRARY_DATA[category];
  if (data?.scope && data.document_groups) {
    const groupKey = librarySubSelect.value;
    const tertiaryKey = libraryTertiarySelect.value;
    const subfolder = data.document_groups[groupKey]?.secondary_options?.[tertiaryKey];
    if (subfolder?.secondary_options) {
      showQuaternary(true, 'Audit folder');
      setOptions(
        libraryQuaternarySelect,
        'Select audit folder',
        Object.entries(subfolder.secondary_options).map(([value, folder]) => ({
          value,
          label: folder.label || value,
        }))
      );
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
    setPathState(true, `${categoryLabel(category)} / ${plantCode(plant)} / ${dept}`, `${plant}:${dept}`);
    return;
  }

  if (data.files && !data.primary_options && !data.customers && !data.scope) {
    setPathState(true, categoryLabel(category), category);
    return;
  }

  if (data.customers) {
    const customer = libraryPrimSelect.value;
    if (!customer) {
      setPathState(false, `${categoryLabel(category)} / Select customer`, '', 'Select a customer folder.');
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
        const isIatfAudit = secondary === 'iatf_audit';
        setPathState(
          false,
          `${categoryLabel(category)} / ${group.label || secondary} / ${isIatfAudit ? 'Select audit type' : 'Select subfolder'}`,
          '',
          isIatfAudit ? 'Select Internal Audit or External Audit.' : 'Select a Business Procedures subfolder.'
        );
        return;
      }
      const subfolder = group.secondary_options[tertiary];
      if (subfolder?.secondary_options) {
        const quaternary = libraryQuaternarySelect.value;
        if (!quaternary) {
          setPathState(
            false,
            `${categoryLabel(category)} / ${group.label || secondary} / ${subfolder.label || tertiary} / Select audit folder`,
            '',
            'Select an audit folder.'
          );
          return;
        }
        const nestedFolder = subfolder.secondary_options[quaternary];
        const plant = plantSelect.value;
        const requiresPlant = Boolean(nestedFolder?.plants);
        if (requiresPlant && !plant) {
          setPathState(
            false,
            `${categoryLabel(category)} / ${group.label || secondary} / ${subfolder.label || tertiary} / ${nestedFolder.label || quaternary} / Select plant`,
            '',
            'Select the plant for this audit folder.'
          );
          return;
        }
        setPathState(
          true,
          `${categoryLabel(category)} / ${group.label || secondary} / ${subfolder.label || tertiary} / ${nestedFolder?.label || quaternary}${requiresPlant ? ` / ${plantCode(plant)}` : ''}`,
          `${secondary}:${tertiary}:${quaternary}${requiresPlant ? `:${plant}` : ''}`
        );
        return;
      }
      if (subfolder?.plants) {
        const plant = plantSelect.value;
        if (!plant) {
          setPathState(
            false,
            `${categoryLabel(category)} / ${group.label || secondary} / ${subfolder.label || tertiary} / Select plant`,
            '',
            'Select the plant for this IATF Audit document.'
          );
          return;
        }
        setPathState(
          true,
          `${categoryLabel(category)} / ${group.label || secondary} / ${subfolder.label || tertiary} / ${plantCode(plant)}`,
          `${secondary}:${tertiary}:${plant}`
        );
        return;
      }
      setPathState(
        true,
        `${categoryLabel(category)} / ${group.label || secondary} / ${subfolder?.label || tertiary}`,
        `${secondary}:${tertiary}`
      );
      return;
    }
    // Handle groups that expose plant -> department folders (plant_departments)
    if (group?.plant_departments) {
      const plant = plantSelect.value;
      const dept = deptSelect.value;
      if (!plant) {
        setPathState(false, `${categoryLabel(category)} / ${group.label || secondary} / Select plant`, '', 'Select plant.');
        return;
      }
      if (!dept) {
        setPathState(false, `${categoryLabel(category)} / ${group.label || secondary} / ${plantCode(plant)} / Select department`, '', 'Select department.');
        return;
      }
      setPathState(true, `${categoryLabel(category)} / ${group.label || secondary} / ${plantCode(plant)} / ${dept}`, `${secondary}:${plant}:${dept}`);
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
    const customer = librarySubSelect.value;
    if (!customer) {
      setPathState(false, `${categoryLabel(category)} / ${folder.label || primary} / Select customer`, '', 'Select a customer folder.');
      return;
    }
    setPathState(
      true,
      `${categoryLabel(category)} / ${folder.label || primary} / ${customer}`,
      `${primary}:${customer}`
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
        `${categoryLabel(category)} / ${folder.label || primary} / ${secondaryFolder.label || secondary} / ${plantCode(plant)}`,
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

libraryCatSelect?.addEventListener('change', configureLibraryCategory);
libraryPrimSelect?.addEventListener('change', configureLibraryPrimary);
librarySubSelect?.addEventListener('change', configureLibrarySecondary);
libraryTertiarySelect?.addEventListener('change', configureLibraryTertiary);
libraryQuaternarySelect?.addEventListener('change', updateLibraryPath);
plantSelect?.addEventListener('change', updateLibraryPath);
plantSelect?.addEventListener('change', () => {
  if (!isRevisionCb?.checked && docNumInput) {
    docNumInput.value = NEXT_DOCUMENT_NUMBERS[plantSelect.value] || '';
  } else if (isRevisionCb?.checked) {
    revisionDocumentValidated = false;
    validateRevisionDocument();
  }
});
deptSelect?.addEventListener('change', updateLibraryPath);

function updateRevisionUI() {
  const isRevised = Boolean(isRevisionCb?.checked);
  isRevisionCb?.setAttribute('aria-expanded', String(isRevised));
  isRevisionCb?.closest('.revision-confirm-checkbox')?.classList.toggle('is-checked', isRevised);
  revisionDocumentValidated = false;
  documentValidationRequest += 1;
  if (documentValidationTimer) clearTimeout(documentValidationTimer);
  if (revisionFields) revisionFields.style.display = isRevised ? 'block' : 'none';
  if (revNumInput) {
    revNumInput.disabled = !isRevised;
    revNumInput.readOnly = true;
    revNumInput.value = '';
  }
  if (!isRevised) {
    const summaryInput = document.getElementById('change_summary_input');
    if (summaryInput) summaryInput.value = '';
  }
  if (docNumInput) {
    docNumInput.readOnly = !isRevised;
    docNumInput.inputMode = 'text';
    docNumInput.pattern = isRevised ? 'ZRAI-DOC-P[1-4]-[0-9]{4}-[0-9]{3,}' : '';
    docNumInput.placeholder = isRevised
      ? 'e.g. ZRAI-DOC-P1-2026-001'
      : 'Assigned automatically after selecting a plant';
    docNumInput.value = isRevised
      ? (REVISION_PREFILL?.document_number || '')
      : (NEXT_DOCUMENT_NUMBERS[plantSelect?.value] || PROFILE_NEXT_DOCUMENT_NUMBER);
  }
  if (docNumLabel) docNumLabel.textContent = 'Document Number';
  if (docNumHint) {
    docNumHint.textContent = isRevised
      ? 'Enter the complete document number for the document being revised.'
      : 'Assigned automatically and separately for each plant.';
  }
  setDocumentValidation(
    isRevised ? 'pending' : '',
    isRevised ? 'Enter an existing document number to continue.' : ''
  );
  updateSubmitState();
}

if (isRevisionCb) {
  isRevisionCb.addEventListener('change', updateRevisionUI);
  updateRevisionUI();
}
docNumInput?.addEventListener('input', () => {
  if (!isRevisionCb?.checked) return;
  docNumInput.value = docNumInput.value.toUpperCase();
  revisionDocumentValidated = false;
  if (revNumInput) revNumInput.value = '';
  documentValidationRequest += 1;
  setDocumentValidation('pending', 'Enter an existing document number to continue.');
  updateSubmitState();
  if (documentValidationTimer) clearTimeout(documentValidationTimer);
  if (/^ZRAI-DOC-P[1-4]-\d{4}-\d{3,}$/i.test(docNumInput.value.trim())) {
    documentValidationTimer = setTimeout(validateRevisionDocument, 350);
  }
});

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

  if (
    isRevisionCb?.checked
    && !/^ZRAI-DOC-P[1-4]-\d{4}-\d{3,}$/i.test(docNumInput?.value.trim() || '')
  ) {
    showInlineError('Enter the complete document number (for example, ZRAI-DOC-P1-2026-001).');
    return;
  }
  if (isRevisionCb?.checked) {
    const documentPlant = docNumInput.value.trim().match(/^ZRAI-DOC-(P[1-4])-/i)?.[1]?.toUpperCase();
    const selectedPlant = plantSelect?.value.match(/^\s*(P[1-4])(?:\s|-)/i)?.[1]?.toUpperCase();
    if (documentPlant && selectedPlant && documentPlant !== selectedPlant) {
      showInlineError('The document number must match the selected plant.');
      return;
    }
    if (!revisionDocumentValidated) {
      showInlineError('Verify an existing document number before uploading the revision.');
      validateRevisionDocument();
      return;
    }
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
      submitBtn.innerHTML = originalLabel;
      if (isRevisionCb?.checked) {
        revisionDocumentValidated = false;
        validateRevisionDocument();
      } else {
        updateSubmitState();
      }
      showInlineError(error.message || 'An error occurred. Please try again.');
    });
});

function normalizeRevisionLibraryPathParts(pathParts) {
  const parts = [...pathParts];
  if (parts[0] === 'plans') {
    return ['iatf_audit', 'external_audit', 'plans', ...parts.slice(1)];
  }

  const legacyAuditType = {
    iatf_internal_audits: 'internal_audit',
    iatf_external_audits: 'external_audit',
  }[parts[0]] || parts[0];
  if (['internal_audit', 'external_audit'].includes(legacyAuditType)
      && ['ncs', 'reports'].includes(parts[1])) {
    return [
      'iatf_audit',
      legacyAuditType,
      parts[1] === 'ncs' ? 'audit_ncs' : 'audit_reports',
      ...parts.slice(2),
    ];
  }

  if (parts[0] !== 'iatf_audit' || !parts[1]) return parts;
  const legacyFolderMap = {
    plans: ['external_audit', 'plans'],
    internal_audit_ncs: ['internal_audit', 'audit_ncs'],
    internal_audit_reports: ['internal_audit', 'audit_reports'],
    external_audit_ncs: ['external_audit', 'audit_ncs'],
    external_audit_reports: ['external_audit', 'audit_reports'],
  };
  if (legacyFolderMap[parts[1]]) {
    return ['iatf_audit', ...legacyFolderMap[parts[1]], ...parts.slice(2)];
  }
  if (parts[1] === 'auditors_list') {
    return ['iatf_audit', 'internal_audit', 'auditors_list', ...parts.slice(3)];
  }
  return parts;
}

function applyRevisionPrefill() {
  configureLibraryCategory();
  if (!REVISION_PREFILL) {
    updateLibraryPath();
    return;
  }

  const parts = normalizeRevisionLibraryPathParts(
    Array.isArray(REVISION_PREFILL.library_path_parts)
      ? REVISION_PREFILL.library_path_parts
      : []
  );
  const categoryData = LIBRARY_DATA[libraryCatSelect?.value];

  if (categoryData?.scope && categoryData.document_groups) {
    if (librarySubSelect && parts[0]) librarySubSelect.value = parts[0];
    configureLibrarySecondary();
    if (libraryTertiarySelect && parts[1]) libraryTertiarySelect.value = parts[1];
    configureLibraryTertiary();
    if (libraryQuaternarySelect && parts[2]) libraryQuaternarySelect.value = parts[2];
  } else if (categoryData?.primary_options) {
    if (libraryPrimSelect && parts[0]) libraryPrimSelect.value = parts[0];
    configureLibraryPrimary();
    if (librarySubSelect && parts[1]) librarySubSelect.value = parts[1];
  } else if (categoryData?.customers && libraryPrimSelect && parts[0]) {
    libraryPrimSelect.value = parts[0];
  }

  updateLibraryPath();
  if (isRevisionCb?.checked && docNumInput?.value) validateRevisionDocument();
}

applyRevisionPrefill();
