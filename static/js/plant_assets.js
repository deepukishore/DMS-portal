let selectedPlant = '';
let selectedDept  = '';

function selectPlant(card, plantLabel) {
  document.querySelectorAll('.plant-card').forEach(c => c.classList.remove('selected'));
  card.classList.add('selected');
  selectedPlant = plantLabel;

  document.getElementById('selected-plant-label').textContent = plantLabel;
  document.getElementById('plant-grid').style.display = 'none';
  document.getElementById('asset-panel').style.display = 'block';

  const sp = document.getElementById('step-plant');
  const sd = document.getElementById('step-dept');
  if (sp) sp.classList.remove('active');
  if (sd) sd.classList.add('active');

  loadDepartments(plantLabel);
}

function resetPlant() {
  document.getElementById('plant-grid').style.display = 'grid';
  document.getElementById('asset-panel').style.display = 'none';
  selectedPlant = '';
  selectedDept = '';

  const sp = document.getElementById('step-plant');
  const sd = document.getElementById('step-dept');
  const sf = document.getElementById('step-files');
  if (sf) sf.classList.remove('active');
  if (sd) sd.classList.remove('active');
  if (sp) sp.classList.add('active');
}

async function loadDepartments(plantLabel) {
  const tabs = document.getElementById('dept-tabs');
  tabs.innerHTML = '<span style="color:var(--text-dim);padding:.6rem 1rem;font-size:.8rem">Loading…</span>';
  resetFileArea();

  const url = typeof DEPT_URL !== 'undefined' ? DEPT_URL : '/plant-assets/departments';
  const params = new URLSearchParams({ plant: plantLabel });
  if (typeof CATEGORY_KEY !== 'undefined' && CATEGORY_KEY) params.append('category', CATEGORY_KEY);

  const res  = await fetch(`${url}?${params}`);
  const data = await res.json();
  tabs.innerHTML = '';
  data.departments.forEach(dept => {
    const label = typeof getDeptLabel === 'function' ? getDeptLabel(dept) : dept;
    const span = document.createElement('span');
    span.className = 'dept-tab';
    span.textContent = label;
    span.dataset.dept = dept;
    span.onclick = () => selectDept(span, dept);
    tabs.appendChild(span);
  });
}

function selectDept(tab, dept) {
  document.querySelectorAll('.dept-tab').forEach(t => t.classList.remove('active'));
  tab.classList.add('active');
  selectedDept = dept;

  const sd = document.getElementById('step-dept');
  const sf = document.getElementById('step-files');
  if (sd) sd.classList.remove('active');
  if (sf) sf.classList.add('active');

  loadFiles(selectedPlant, dept);
}

async function loadFiles(plantLabel, dept) {
  const area = document.getElementById('file-view-area');
  area.innerHTML = '<p style="color:var(--text-dim);font-size:.8rem;padding:.5rem 0">Loading files…</p>';

  const url = typeof FILE_URL !== 'undefined' ? FILE_URL : '/plant-assets/files';
  const params = new URLSearchParams({ plant: plantLabel, department: dept });
  if (typeof CATEGORY_KEY !== 'undefined' && CATEGORY_KEY) params.append('category', CATEGORY_KEY);

  const res  = await fetch(`${url}?${params}`);
  const data = await res.json();

  if (!data.files || data.files.length === 0) {
    area.innerHTML = '<p style="color:var(--text-dim);font-size:.8rem">No files found for this selection.</p>';
    return;
  }

  const grid = document.createElement('div');
  grid.className = 'asset-file-grid';
  data.files.forEach(fname => {
    const card = document.createElement('div');
    card.className = 'asset-file-card';
    card.innerHTML = `
      <svg class="asset-file-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/>
        <polyline points="14 2 14 8 20 8"/>
      </svg>
      <span class="asset-file-name">${fname}</span>
      <button class="btn-view-file" onclick="viewFile('${fname}')">
        <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
          <circle cx="12" cy="12" r="3"/>
        </svg>
        View
      </button>`;
    grid.appendChild(card);
  });
  area.innerHTML = '';
  area.appendChild(grid);
}

async function viewFile(fname) {
  const vUrl = typeof VIEW_URL !== 'undefined' ? VIEW_URL : '/plant-assets/view';
  await fetch(vUrl, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ file_name: fname, plant: selectedPlant, department: selectedDept })
  });
  alert(`Viewing: ${fname}\n\nIn a production environment, this would open the document viewer.`);
}

function resetFileArea() {
  document.getElementById('file-view-area').innerHTML = `
    <div class="file-view-placeholder">
      <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <path d="M22 19a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2h5l2 3h9a2 2 0 012 2z"/>
      </svg>
      <p>Choose a department to see files.</p>
    </div>`;
}
