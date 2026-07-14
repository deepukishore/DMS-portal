// Initialize theme from localStorage or system preference (default to light mode)
function initializeTheme() {
  const savedTheme = localStorage.getItem('theme');
  const theme = savedTheme || 'light'; // Default to light mode
  
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
  const body = document.body;

  body?.classList.add('theme-switching');
  
  if (newTheme === 'light') {
    html.setAttribute('data-theme', 'light');
  } else {
    html.removeAttribute('data-theme');
  }
  
  localStorage.setItem('theme', newTheme);
  window.setTimeout(() => body?.classList.remove('theme-switching'), 360);
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
const notificationClearAll = document.getElementById('notification-clear-all');

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

notificationClearAll?.addEventListener('click', async () => {
  try {
    const response = await fetch(window.APP_SHORTCUTS.clearAllNotifications, {
      method: 'POST',
      headers: { 'X-Requested-With': 'XMLHttpRequest' }
    });
    const payload = await response.json();
    if (!response.ok || !payload.ok) {
      throw new Error(payload.message || 'Notification clear failed.');
    }

    const list = document.querySelector('.notification-list');
    if (list) {
      list.innerHTML = '<div class="notification-empty">No notifications yet.</div>';
    }
    setNotificationBadgeCount(0);
  } catch (error) {
    console.error('Notification clear-all error:', error);
  }
});

function getUnreadNotificationCount() {
  return document.querySelectorAll('.notification-item.is-unread').length;
}

async function markNotificationRead(notificationId, item) {
  if (!notificationId || !item || !item.classList.contains('is-unread')) {
    return false;
  }
  if (item.dataset.readPending === '1') {
    return false;
  }

  item.dataset.readPending = '1';
  try {
    const response = await fetch(`${window.APP_SHORTCUTS.markNotificationReadBase}${notificationId}`, {
      method: 'POST',
      headers: { 'X-Requested-With': 'XMLHttpRequest' }
    });
    const payload = await response.json();
    if (!response.ok || !payload.ok) {
      throw new Error(payload.message || 'Notification update failed.');
    }
    item.classList.remove('is-unread');
    setNotificationBadgeCount(getUnreadNotificationCount());
    return true;
  } catch (error) {
    console.error('Notification mark-read error:', error);
    return false;
  } finally {
    delete item.dataset.readPending;
  }
}

document.querySelectorAll('.notification-item[data-notification-id]').forEach((item) => {
  item.addEventListener('mouseenter', () => {
    markNotificationRead(item.dataset.notificationId, item);
  });

  item.addEventListener('click', async (event) => {
    const notificationId = item.dataset.notificationId;
    const hasLink = item.dataset.hasLink === '1';
    const href = item.getAttribute('href');

    event.preventDefault();
    await markNotificationRead(notificationId, item);

    if (hasLink && href && href !== '#') {
      window.location.href = href;
      return;
    }

    setNotificationsOpen(false);
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
  if (!window.APP_SHORTCUTS) {
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

function initializeWelcomeModal() {
  const modal = document.getElementById('welcome-modal');
  const closeButton = document.getElementById('welcome-close');
  if (!modal || !closeButton) return;
  // Only show on first landing after login (server sets SHOW_WELCOME once)
  if (!window.SHOW_WELCOME) return;
  modal.hidden = false;
  closeButton.addEventListener('click', () => { modal.hidden = true; });
  // Also close on overlay click
  modal.addEventListener('click', (e) => { if (e.target === modal) modal.hidden = true; });
}

const reducedMotionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');

function animateStatValue(element) {
  if (!element || element.dataset.countAnimated === '1') return;

  const rawValue = element.textContent.trim();
  const normalizedValue = rawValue.replace(/,/g, '');
  if (!/^-?\d+$/.test(normalizedValue)) return;

  element.dataset.countAnimated = '1';
  if (reducedMotionQuery.matches) return;

  const target = Number(normalizedValue);
  const duration = 650;
  const startedAt = performance.now();
  const formatter = new Intl.NumberFormat();
  element.classList.add('is-counting');

  function updateValue(now) {
    const progress = Math.min((now - startedAt) / duration, 1);
    const easedProgress = 1 - Math.pow(1 - progress, 3);
    element.textContent = formatter.format(Math.round(target * easedProgress));

    if (progress < 1) {
      window.requestAnimationFrame(updateValue);
      return;
    }

    element.textContent = rawValue;
    element.classList.remove('is-counting');
  }

  window.requestAnimationFrame(updateValue);
}

function initializeMotionEffects() {
  if (reducedMotionQuery.matches || !('IntersectionObserver' in window)) return;

  const revealSelector = [
    '.stat-card',
    '.quick-action-card',
    '.chart-card',
    '.tracker-card',
    '.proc-type-card',
    '.asset-file-card',
    '.plant-card',
    '.customer-card',
    '.category-card',
    '.about-feature-card',
    '.dl-gallery-card',
    '.mr-dept-folder',
    '.upload-step-card',
    '.review-card'
  ].join(', ');

  document.documentElement.classList.add('motion-enabled');

  const revealObserver = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;

      entry.target.classList.add('is-visible');
      entry.target.querySelectorAll('.stat-value').forEach(animateStatValue);
      revealObserver.unobserve(entry.target);
    });
  }, { rootMargin: '0px 0px -6% 0px', threshold: 0.08 });

  function decorateMotionElements(scope = document) {
    scope.querySelectorAll(revealSelector).forEach((element, index) => {
      if (element.dataset.motionReady === '1') return;

      element.dataset.motionReady = '1';
      element.classList.add('motion-reveal');
      element.style.setProperty('--reveal-delay', `${(index % 6) * 55}ms`);
      revealObserver.observe(element);
    });

    scope.querySelectorAll('.stat-value').forEach((element) => {
      if (!element.closest(revealSelector)) animateStatValue(element);
    });
  }

  decorateMotionElements();

  const dynamicLibrary = document.getElementById('library-content');
  if (dynamicLibrary && 'MutationObserver' in window) {
    const libraryObserver = new MutationObserver(() => decorateMotionElements(dynamicLibrary));
    libraryObserver.observe(dynamicLibrary, { childList: true, subtree: true });
  }
}

function initializeScrollEffects() {
  const content = document.querySelector('.content');
  if (!content) return;

  const updateScrollState = () => {
    document.body.classList.toggle('content-scrolled', content.scrollTop > 8);
  };

  content.addEventListener('scroll', updateScrollState, { passive: true });
  updateScrollState();
}

document.addEventListener('DOMContentLoaded', () => {
  initializeWelcomeModal();
  initializeMotionEffects();
  initializeScrollEffects();
});
