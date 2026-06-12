const loadedPlants = {};
let currentPlant = '';
let currentDept = '';

// Auto-load department counts for all plants on page load
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.mr-plant-header').forEach((header, i) => {
    const plantLabel = header.querySelector('.mr-plant-info strong').textContent;
    fetchDeptCount(plantLabel, i + 1);
  });
});

async function fetchDeptCount(plantLabel, idx) {
  try {
    const res = await fetch(`${DEPT_URL}?plant=${encodeURIComponent(plantLabel)}`);
    const data = await res.json();
    const count = data.departments ? data.departments.length : 0;
    const el = document.getElementById(`dept-count-${idx}`);
    if (el) el.textContent = `${count} department${count !== 1 ? 's' : ''}`;
  } catch {
    const el = document.getElementById(`dept-count-${idx}`);
    if (el) el.textContent = '';
  }
}

async function togglePlant(header, plantLabel, idx) {
  const grid = document.getElementById(`dept-grid-${idx}`);
  const chevron = header.querySelector('.mr-plant-chevron');
  const isOpen = grid.style.display !== 'none';

  // Close all others
  document.querySelectorAll('.mr-plant-block').forEach((block, i) => {
    const g = document.getElementById(`dept-grid-${i + 1}`);
    const c = block.querySelector('.mr-plant-chevron');
    const h = block.querySelector('.mr-plant-header');
    if (g && i + 1 !== idx) {
      g.style.display = 'none';
      if (c) c.style.transform = '';
      if (h) h.classList.remove('open');
    }
  });

  if (isOpen) {
    grid.style.display = 'none';
    chevron.style.transform = '';
    header.classList.remove('open');
    return;
  }

  header.classList.add('open');
  chevron.style.transform = 'rotate(180deg)';
  grid.style.display = 'grid';

  if (loadedPlants[plantLabel]) return;
  loadedPlants[plantLabel] = true;

  grid.innerHTML = '<div class="mr-loading">Loading departments…</div>';

  const res = await fetch(`${DEPT_URL}?plant=${encodeURIComponent(plantLabel)}`);
  const data = await res.json();
  grid.innerHTML = '';

  if (!data.departments || data.departments.length === 0) {
    grid.innerHTML = '<p class="mr-empty">No departments found.</p>';
    return;
  }

  data.departments.forEach(dept => {
    const card = document.createElement('div');
    card.className = 'mr-dept-folder';
    card.onclick = () => openDeptFiles(plantLabel, dept);
    card.innerHTML = `
      <div class="mr-folder-icon">
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M22 19a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2h5l2 3h9a2 2 0 012 2z"/>
        </svg>
      </div>
      <span class="mr-folder-name">${dept}</span>
      <svg class="mr-folder-arrow" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>`;
    grid.appendChild(card);
  });
}

async function openDeptFiles(plantLabel, dept) {
  currentPlant = plantLabel;
  currentDept = dept;

  document.getElementById('modal-plant-label').textContent = plantLabel;
  document.getElementById('modal-dept-label').textContent = dept;
  const listEl = document.getElementById('modal-file-list');
  listEl.innerHTML = '<p style="color:var(--text-dim);font-size:.8rem">Loading files…</p>';

  document.getElementById('file-modal').classList.add('open');

  const res = await fetch(`${FILE_URL}?plant=${encodeURIComponent(plantLabel)}&department=${encodeURIComponent(dept)}`);
  const data = await res.json();

  if (!data.files || data.files.length === 0) {
    listEl.innerHTML = '<p style="color:var(--text-dim);font-size:.8rem;padding:.5rem 0">No files in this folder.</p>';
    return;
  }

  const ul = document.createElement('ul');
  ul.className = 'mr-file-list';
  data.files.forEach(fname => {
    const ext = fname.split('.').pop().toLowerCase();
    const li = document.createElement('li');
    li.className = 'mr-file-row';
    li.innerHTML = `
      <span class="mr-file-ext mr-ext-${ext}">${ext}</span>
      <span class="mr-file-name">${fname}</span>
      <button class="btn-view-file" onclick="viewFile('${fname.replace(/'/g,"\\'")}')">
        <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
          <circle cx="12" cy="12" r="3"/>
        </svg>
        View
      </button>`;
    ul.appendChild(li);
  });
  listEl.innerHTML = '';
  listEl.appendChild(ul);
}

async function viewFile(fname) {
  await fetch(VIEW_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ file_name: fname, plant: currentPlant, department: currentDept })
  });
  window.location.href = `/document-view?file=${encodeURIComponent(fname)}`;
}

function closeModal() {
  document.getElementById('file-modal').classList.remove('open');
}

document.addEventListener('keydown', e => { if (e.key === 'Escape') closeModal(); });
