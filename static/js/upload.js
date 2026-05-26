// ── Element refs ────────────────────────────────────────────────────────────
const dropZone          = document.getElementById('drop-zone');
const fileInput         = document.getElementById('file-input');
const fileList          = document.getElementById('file-list');
const fileItems         = document.getElementById('file-items');
const fileCountLabel    = document.getElementById('file-count-label');
const clearBtn          = document.getElementById('clear-files');
const submitBtn         = document.getElementById('submit-btn');
const submitHint        = document.getElementById('submit-hint');
const browseTrig        = document.getElementById('browse-trigger');
const uploadForm        = document.getElementById('upload-form');
const docTypeInput      = document.getElementById('doc_type_input');
const customerSelect    = document.getElementById('customer-select');
const customerReqStar   = document.getElementById('customer-required-star');
const internalCheckbox  = document.getElementById('is_internal_checkbox');
const isRevisionCb      = document.getElementById('is_revision_checkbox');
const revisionFields    = document.getElementById('revision-fields');
const uploadTargetRadios = document.querySelectorAll('input[name="upload_target"]');
const libraryMeta       = document.getElementById('library-meta');
const libraryCatSelect  = document.getElementById('library-category-select');
const librarySubInput   = document.getElementById('library-subcategory-input');
const librarySubSelect  = document.getElementById('library-subcategory-select');
const libraryPrimWrap   = document.getElementById('library-primary-wrapper');
const libraryPrimSelect = document.getElementById('library-primary-select');
const librarySubHidden  = document.getElementById('library-subcategory-hidden');
const docNumInput       = document.getElementById('document-number-input');
const revNumInput       = document.getElementById('revision_number_input');

const ALLOWED_EXTS = ['.pdf', '.docx', '.doc', '.xlsx', '.xls', '.pptx', '.ppt'];

// ── Helpers ──────────────────────────────────────────────────────────────────
function formatSize(bytes) {
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / 1048576).toFixed(1) + ' MB';
}

function fileIcon(ext) {
  const colors = { pdf: '#ef4444', docx: '#3b82f6', doc: '#3b82f6', xlsx: '#22c55e', xls: '#22c55e', pptx: '#f97316', ppt: '#f97316' };
  const color = colors[ext] || 'var(--accent)';
  return `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="${color}" stroke-width="2">
    <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/>
    <polyline points="14 2 14 8 20 8"/>
  </svg>`;
}

function updateSubmitState(hasFiles) {
  submitBtn.disabled = !hasFiles;
  submitHint.style.display = hasFiles ? 'none' : 'inline';
}

// ── File rendering ────────────────────────────────────────────────────────────
function renderFiles(files) {
  fileItems.innerHTML = '';
  if (!files || files.length === 0) {
    fileList.style.display = 'none';
    updateSubmitState(false);
    return;
  }

  const invalid = Array.from(files).filter(f => {
    const ext = '.' + f.name.split('.').pop().toLowerCase();
    return !ALLOWED_EXTS.includes(ext);
  });

  if (invalid.length > 0) {
    showInlineError('Invalid file type(s): ' + invalid.map(f => f.name).join(', ') + '. Allowed: PDF, Word, Excel, PowerPoint.');
    fileInput.value = '';
    fileList.style.display = 'none';
    updateSubmitState(false);
    return;
  }

  fileList.style.display = 'block';
  fileCountLabel.textContent = files.length + ' file' + (files.length > 1 ? 's' : '') + ' selected';
  updateSubmitState(true);

  Array.from(files).forEach(f => {
    const ext = f.name.split('.').pop().toLowerCase();
    const li = document.createElement('li');
    li.innerHTML = `${fileIcon(ext)}<span class="fi-name">${f.name}</span><span class="fi-size">${formatSize(f.size)}</span>`;
    fileItems.appendChild(li);
  });
}

function showInlineError(msg) {
  let el = document.getElementById('upload-inline-error');
  if (!el) {
    el = document.createElement('div');
    el.id = 'upload-inline-error';
    el.className = 'alert alert-error';
    el.style.marginTop = '.75rem';
    dropZone.parentNode.insertBefore(el, dropZone.nextSibling);
  }
  el.textContent = msg;
  el.style.display = 'flex';
  setTimeout(() => { if (el) el.style.display = 'none'; }, 5000);
}

// ── Internal document toggle ──────────────────────────────────────────────────
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
internalCheckbox.addEventListener('change', updateInternalUI);

// ── Upload target (radio) ─────────────────────────────────────────────────────
function getUploadTarget() {
  const checked = document.querySelector('input[name="upload_target"]:checked');
  return checked ? checked.value : 'documents';
}

function updateTargetUI() {
  const isLibrary = getUploadTarget() === 'library';
  libraryMeta.style.display = isLibrary ? 'block' : 'none';

  // Toggle category required
  if (libraryCatSelect) {
    if (isLibrary) libraryCatSelect.setAttribute('required', 'required');
    else libraryCatSelect.removeAttribute('required');
  }

  // Highlight selected card
  document.getElementById('target-opt-documents').classList.toggle('selected', !isLibrary);
  document.getElementById('target-opt-library').classList.toggle('selected', isLibrary);

  if (!isLibrary) {
    if (librarySubInput) librarySubInput.value = '';
    if (librarySubSelect) librarySubSelect.value = '';
    if (librarySubHidden) librarySubHidden.value = '';
  }
}

uploadTargetRadios.forEach(r => r.addEventListener('change', updateTargetUI));
updateTargetUI(); // init

// ── Revision toggle ───────────────────────────────────────────────────────────
if (isRevisionCb) {
  isRevisionCb.addEventListener('change', () => {
    revisionFields.style.display = isRevisionCb.checked ? 'block' : 'none';
    if (!isRevisionCb.checked) document.getElementById('change_summary_input').value = '';
  });
}

// ── Library subcategory population ───────────────────────────────────────────
function populateSubcategories(catKey) {
  const data = window.LIBRARY_DATA && window.LIBRARY_DATA[catKey];
  if (!data) {
    if (libraryPrimWrap) libraryPrimWrap.style.display = 'none';
    if (librarySubSelect) librarySubSelect.style.display = 'none';
    if (librarySubInput) librarySubInput.style.display = 'block';
    return;
  }

  if (data.primary_options) {
    if (libraryPrimWrap) libraryPrimWrap.style.display = 'block';
    libraryPrimSelect.innerHTML = '<option value="">Select primary (optional)</option>';
    Object.keys(data.primary_options).forEach(k => {
      const o = document.createElement('option');
      o.value = k;
      o.textContent = data.primary_options[k].label || k;
      libraryPrimSelect.appendChild(o);
    });
    if (librarySubSelect) librarySubSelect.style.display = 'none';
    if (librarySubInput) librarySubInput.style.display = 'none';
    return;
  }

  const opts = data.secondary_options
    ? Object.keys(data.secondary_options).map(k => ({ key: k, label: data.secondary_options[k].label || k }))
    : [];

  if (opts.length > 0) {
    librarySubSelect.innerHTML = '<option value="">Select subcategory (optional)</option>';
    opts.forEach(o => {
      const el = document.createElement('option');
      el.value = o.key; el.textContent = o.label;
      librarySubSelect.appendChild(el);
    });
    librarySubSelect.style.display = 'block';
    if (librarySubInput) librarySubInput.style.display = 'none';
    if (libraryPrimWrap) libraryPrimWrap.style.display = 'none';
  } else {
    if (librarySubSelect) librarySubSelect.style.display = 'none';
    if (librarySubInput) librarySubInput.style.display = 'block';
    if (libraryPrimWrap) libraryPrimWrap.style.display = 'none';
  }
}

if (libraryCatSelect) {
  libraryCatSelect.addEventListener('change', e => populateSubcategories(e.target.value));
  populateSubcategories(libraryCatSelect.value);
}

if (libraryPrimSelect) {
  libraryPrimSelect.addEventListener('change', ev => {
    const primKey = ev.target.value;
    const parentData = window.LIBRARY_DATA && window.LIBRARY_DATA[libraryCatSelect.value];
    if (!parentData || !parentData.primary_options) return;
    const primData = parentData.primary_options[primKey];
    if (primData && primData.secondary_options) {
      librarySubSelect.innerHTML = '<option value="">Select subcategory (optional)</option>';
      Object.keys(primData.secondary_options).forEach(k => {
        const o = document.createElement('option');
        o.value = k; o.textContent = primData.secondary_options[k].label || k;
        librarySubSelect.appendChild(o);
      });
      librarySubSelect.style.display = 'block';
      if (librarySubInput) librarySubInput.style.display = 'none';
    } else {
      if (librarySubSelect) librarySubSelect.style.display = 'none';
      if (librarySubInput) librarySubInput.style.display = 'block';
    }
  });
}

// ── Drag & drop ───────────────────────────────────────────────────────────────
browseTrig.addEventListener('click', () => fileInput.click());
dropZone.addEventListener('click', e => { if (e.target !== browseTrig) fileInput.click(); });
fileInput.addEventListener('change', () => renderFiles(fileInput.files));
clearBtn.addEventListener('click', () => { fileInput.value = ''; renderFiles(null); });

['dragenter', 'dragover'].forEach(ev => dropZone.addEventListener(ev, e => {
  e.preventDefault(); dropZone.classList.add('drag-over');
}));
['dragleave', 'drop'].forEach(ev => dropZone.addEventListener(ev, e => {
  e.preventDefault(); dropZone.classList.remove('drag-over');
}));
dropZone.addEventListener('drop', e => {
  const dt = e.dataTransfer;
  if (dt.files && dt.files.length > 0) { fileInput.files = dt.files; renderFiles(dt.files); }
});

// ── Form submission ───────────────────────────────────────────────────────────
function showSuccessPopup(message, redirectUrl) {
  const popup = document.createElement('div');
  popup.className = 'success-popup';
  popup.innerHTML = `<div class="popup-content">
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="popup-icon"><polyline points="20 6 9 17 4 12"></polyline></svg>
    <h3>${message}</h3>
    <p>Redirecting…</p>
    ${redirectUrl ? `<a class="btn-primary" href="${redirectUrl}">Go to Document Library</a>` : ''}
  </div>`;
  document.body.appendChild(popup);
  setTimeout(() => popup.classList.add('show'), 10);
  setTimeout(() => { window.location.href = redirectUrl || window.location.href; }, 2500);
}

uploadForm.addEventListener('submit', e => {
  e.preventDefault();

  if (!docNumInput?.value.trim()) { showInlineError('Document number is required.'); return; }
  if (getUploadTarget() === 'library' && !libraryCatSelect?.value.trim()) {
    showInlineError('Category is required for Document Library uploads.'); return;
  }
  if (!internalCheckbox.checked && !customerSelect.value) {
    showInlineError('Please select a customer, or tick "Internal Document".');
    return;
  }

  // Sync hidden subcategory field
  if (getUploadTarget() === 'library' && librarySubHidden) {
    let chosen = '';
    if (librarySubSelect && librarySubSelect.style.display !== 'none' && librarySubSelect.value) chosen = librarySubSelect.value;
    else if (librarySubInput && librarySubInput.style.display !== 'none' && librarySubInput.value) chosen = librarySubInput.value;
    else if (libraryPrimSelect && libraryPrimWrap && libraryPrimWrap.style.display !== 'none' && libraryPrimSelect.value) chosen = libraryPrimSelect.value;
    librarySubHidden.value = chosen;
  }

  const originalLabel = submitBtn.innerHTML;
  submitBtn.disabled = true;
  submitBtn.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/></svg> Uploading…`;

  fetch(uploadForm.action, {
    method: 'POST',
    headers: { 'X-Requested-With': 'XMLHttpRequest' },
    body: new FormData(uploadForm),
  })
  .then(r => {
    const ct = r.headers.get('content-type') || '';
    return ct.includes('application/json') ? r.json() : r.text();
  })
  .then(data => {
    if (typeof data === 'object' && data.ok === false) throw new Error(data.message || 'Upload failed.');
    if (typeof data === 'object' && data.ok && data.saved_files) {
      const redirectUrl = data.redirect || '/document-library';
      showSuccessPopup('Saved to Document Library', redirectUrl);
      return;
    }
    window.location.reload();
  })
  .catch(err => {
    submitBtn.disabled = false;
    submitBtn.innerHTML = originalLabel;
    showInlineError(err.message || 'An error occurred. Please try again.');
  });
});
