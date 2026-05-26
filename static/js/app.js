// Initialize theme from localStorage or system preference
function initializeTheme() {
  const savedTheme = localStorage.getItem('theme');
  const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  const theme = savedTheme || (systemPrefersDark ? 'dark' : 'light');
  
  if (theme === 'light') {
    document.documentElement.setAttribute('data-theme', 'light');
  } else {
    document.documentElement.removeAttribute('data-theme');
  }
  localStorage.setItem('theme', theme);
}

// Initialize theme on page load
initializeTheme();

// Theme toggle button handler
document.getElementById('theme-toggle')?.addEventListener('click', () => {
  const html = document.documentElement;
  const currentTheme = html.getAttribute('data-theme');
  const newTheme = currentTheme === 'light' ? 'dark' : 'light';
  
  if (newTheme === 'light') {
    html.setAttribute('data-theme', 'light');
  } else {
    html.removeAttribute('data-theme');
  }
  
  localStorage.setItem('theme', newTheme);
});

const shell = document.querySelector('.shell');
const sidebarToggle = document.getElementById('sidebar-toggle');
const sidebarClose = document.getElementById('sidebar-close');
const sidebarBackdrop = document.getElementById('sidebar-backdrop');
const mobileSidebarQuery = window.matchMedia('(max-width: 700px)');

function setSidebarOpen(isOpen) {
  if (!shell) return;
  shell.classList.toggle('sidebar-open', isOpen);
  if (sidebarToggle) {
    sidebarToggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
  }
  document.body.classList.toggle('nav-open', isOpen);
}

sidebarToggle?.addEventListener('click', () => {
  setSidebarOpen(!shell?.classList.contains('sidebar-open'));
});

sidebarClose?.addEventListener('click', () => {
  setSidebarOpen(false);
});

sidebarBackdrop?.addEventListener('click', () => {
  setSidebarOpen(false);
});

document.querySelectorAll('.sidebar .nav-item').forEach(link => {
  link.addEventListener('click', () => {
    if (mobileSidebarQuery.matches) {
      setSidebarOpen(false);
    }
  });
});

mobileSidebarQuery.addEventListener('change', event => {
  if (!event.matches) {
    setSidebarOpen(false);
  }
});

document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && shell?.classList.contains('sidebar-open')) {
    setSidebarOpen(false);
  }
});

const notificationWrap = document.getElementById('notification-wrap');
const notificationToggle = document.getElementById('notification-toggle');
const notificationPanel = document.getElementById('notification-panel');
const notificationMarkAll = document.getElementById('notification-mark-all');

function getNotificationBadge() {
  return document.getElementById('notification-badge');
}

function setNotificationBadgeCount(count) {
  const badge = getNotificationBadge();
  if (count <= 0) {
    badge?.remove();
    return;
  }
  if (badge) {
    badge.textContent = String(count);
  }
}

function setNotificationsOpen(isOpen) {
  if (!notificationPanel || !notificationToggle) return;
  notificationPanel.hidden = !isOpen;
  notificationToggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
  notificationWrap?.classList.toggle('is-open', isOpen);
}

notificationToggle?.addEventListener('click', (event) => {
  event.stopPropagation();
  setNotificationsOpen(notificationPanel?.hidden);
});

document.addEventListener('click', (event) => {
  if (!notificationWrap?.contains(event.target)) {
    setNotificationsOpen(false);
  }
});

notificationMarkAll?.addEventListener('click', async () => {
  try {
    await fetch(window.APP_SHORTCUTS.markAllNotificationsRead, {
      method: 'POST',
      headers: { 'X-Requested-With': 'XMLHttpRequest' }
    });
    document.querySelectorAll('.notification-item.is-unread').forEach((item) => item.classList.remove('is-unread'));
    setNotificationBadgeCount(0);
  } catch (error) {
    console.error('Notification mark-all error:', error);
  }
});

document.querySelectorAll('.notification-item[data-notification-id]').forEach((item) => {
  item.addEventListener('click', async (event) => {
    const notificationId = item.dataset.notificationId;
    const hasLink = item.dataset.hasLink === '1';
    const href = item.getAttribute('href');

    if (!hasLink) {
      event.preventDefault();
    }

    try {
      await fetch(`${window.APP_SHORTCUTS.markNotificationReadBase}${notificationId}`, {
        method: 'POST',
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
      });
      item.classList.remove('is-unread');
      setNotificationBadgeCount(document.querySelectorAll('.notification-item.is-unread').length);
    } catch (error) {
      console.error('Notification mark-read error:', error);
    }

    if (!hasLink || !href || href === '#') {
      setNotificationsOpen(false);
    }
  });
});

// Auto-dismiss alerts after 5s
document.querySelectorAll('.alert').forEach(el => {
  setTimeout(() => el.style.opacity = '0', 4500);
  setTimeout(() => el.remove(), 5000);
});

// Password visibility toggle
document.querySelectorAll('.password-toggle-checkbox').forEach(checkbox => {
  checkbox.addEventListener('change', function() {
    const passwordInput = this.closest('.password-field-wrapper').querySelector('input[type="password"], input[type="text"]');
    if (passwordInput) {
      passwordInput.type = this.checked ? 'text' : 'password';
    }
  });
});

// Toggle all passwords in change password form
const toggleAllPasswordsCheckbox = document.getElementById('toggle-all-passwords');
if (toggleAllPasswordsCheckbox) {
  toggleAllPasswordsCheckbox.addEventListener('change', function() {
    const passwordForm = document.getElementById('password-form');
    if (passwordForm) {
      const passwordInputs = passwordForm.querySelectorAll('input[type="password"], input[type="text"]');
      passwordInputs.forEach(input => {
        if (input.name && (input.name === 'current_password' || input.name === 'new_password' || input.name === 'confirm_password')) {
          input.type = this.checked ? 'text' : 'password';
        }
      });
    }
  });
}

// Close modal on overlay click
document.querySelectorAll('.modal-overlay').forEach(overlay => {
  overlay.addEventListener('click', e => {
    if (e.target === overlay) overlay.classList.remove('open');
  });
});

function applyApprovalStatusUpdate(rawPayload) {
  if (!rawPayload) return;

  let payload;
  try {
    payload = JSON.parse(rawPayload);
  } catch {
    return;
  }

  if (payload?.docId === undefined || payload?.docId === null || !payload?.status) return;

  const row = document.querySelector(`[data-doc-id="${payload.docId}"]`);
  const statusPill = row?.querySelector('[data-approval-status]');
  if (!statusPill) return;

  statusPill.textContent = payload.status;
  statusPill.className = `status-pill status-${payload.status.toLowerCase()}`;
}

applyApprovalStatusUpdate(localStorage.getItem('approval-status-update'));

window.addEventListener('storage', (event) => {
  if (event.key !== 'approval-status-update') return;
  applyApprovalStatusUpdate(event.newValue);
});

function isTypingTarget(target) {
  if (!target) return false;
  const tag = target.tagName?.toLowerCase();
  return tag === 'input' || tag === 'textarea' || tag === 'select' || target.isContentEditable;
}

document.addEventListener('keydown', (event) => {
  if (event.defaultPrevented || event.ctrlKey || event.metaKey || event.altKey || event.shiftKey) {
    return;
  }
  if (isTypingTarget(event.target)) {
    return;
  }

  const key = event.key.toLowerCase();
  if (key === 'd') {
    window.location.href = window.APP_SHORTCUTS.dashboard;
  } else if (key === 'u') {
    window.location.href = window.APP_SHORTCUTS.upload;
  } else if (key === 'p') {
    window.location.href = window.APP_SHORTCUTS.approvals;
  }
});
