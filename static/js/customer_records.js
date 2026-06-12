let selectedCustomer = '';

function selectCustomer(card, customerName) {
  document.querySelectorAll('.customer-card').forEach(c => c.classList.remove('selected'));
  card.classList.add('selected');
  selectedCustomer = customerName;

  document.getElementById('selected-customer-label').textContent = customerName;
  document.getElementById('customer-grid').style.display = 'none';
  document.getElementById('asset-panel').style.display = 'block';

  loadFiles(customerName);
}

function resetCustomer() {
  document.getElementById('customer-grid').style.display = 'grid';
  document.getElementById('asset-panel').style.display = 'none';
  selectedCustomer = '';
}

async function loadFiles(customerName) {
  const area = document.getElementById('file-view-area');
  area.innerHTML = '<p style="color:var(--text-dim);font-size:.8rem;padding:.75rem 1.5rem">Loading files…</p>';

  const res = await fetch(`${FILE_URL}?customer=${encodeURIComponent(customerName)}`);
  const data = await res.json();

  if (!data.files || data.files.length === 0) {
    area.innerHTML = '<p style="color:var(--text-dim);font-size:.8rem;padding:.75rem 1.5rem">No files found for this customer.</p>';
    return;
  }

  const grid = document.createElement('div');
  grid.className = 'asset-file-grid';
  grid.style.padding = '1.5rem';

  data.files.forEach(fname => {
    const ext = fname.split('.').pop().toLowerCase();
    const card = document.createElement('div');
    card.className = 'asset-file-card';
    card.innerHTML = `
      <span class="mr-file-ext mr-ext-${ext}">${ext}</span>
      <span class="asset-file-name">${fname}</span>
      <button class="btn-view-file" onclick="viewFile('${fname.replace(/'/g, "\\'")}')">
        <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>
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
  window.location.href = `/document-view?file=${encodeURIComponent(fname)}`;
}

if (typeof PRESELECT_CUSTOMER !== 'undefined' && PRESELECT_CUSTOMER) {
  document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.customer-card').forEach(card => {
      const strong = card.querySelector('strong');
      if (strong && strong.textContent.trim() === PRESELECT_CUSTOMER) {
        selectCustomer(card, PRESELECT_CUSTOMER);
      }
    });
  });
}
