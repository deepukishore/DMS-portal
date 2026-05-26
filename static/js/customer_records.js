let selectedCustomer = '';

function selectCustomer(card, customerName) {
  document.querySelectorAll('.customer-card').forEach(c => c.classList.remove('selected'));
  card.classList.add('selected');
  selectedCustomer = customerName;

  document.getElementById('selected-customer-label').textContent = customerName;
  document.getElementById('customer-grid').style.display = 'none';
  document.getElementById('asset-panel').style.display = 'block';

  const sc = document.getElementById('cstep-customer');
  const sf = document.getElementById('cstep-files');
  if (sc) sc.classList.remove('active');
  if (sf) sf.classList.add('active');

  loadFiles(customerName);
}

function resetCustomer() {
  document.getElementById('customer-grid').style.display = 'grid';
  document.getElementById('asset-panel').style.display = 'none';
  selectedCustomer = '';

  const sc = document.getElementById('cstep-customer');
  const sf = document.getElementById('cstep-files');
  if (sf) sf.classList.remove('active');
  if (sc) sc.classList.add('active');

  resetFileArea();
}

async function loadFiles(customerName) {
  const area = document.getElementById('file-view-area');
  area.innerHTML = '<p style="color:var(--text-dim);font-size:.8rem;padding:.5rem 0">Loading files...</p>';

  const res = await fetch(`${FILE_URL}?customer=${encodeURIComponent(customerName)}`);
  const data = await res.json();

  if (!data.files || data.files.length === 0) {
    area.innerHTML = '<p style="color:var(--text-dim);font-size:.8rem">No files found for this customer.</p>';
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
  await fetch(VIEW_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ file_name: fname, customer: selectedCustomer })
  });
  alert(`Viewing: ${fname}\n\nIn a production environment, this would open the document viewer.`);
}

function resetFileArea() {
  document.getElementById('file-view-area').innerHTML = `
    <div class="file-view-placeholder">
      <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <path d="M22 19a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2h5l2 3h9a2 2 0 012 2z"/>
      </svg>
      <p>Choose a customer to see files.</p>
    </div>`;
}
