(function () {
  'use strict';

  const sourcePreview = document.querySelector('.document-preview-card .review-preview');
  const modal = document.getElementById('document-preview-modal');
  const modalBody = document.getElementById('document-preview-modal-body');
  const closeButton = document.getElementById('document-preview-modal-close');
  const openButtons = document.querySelectorAll('[data-open-document-preview]');
  const pagination = document.getElementById('document-preview-pagination');
  const previousPageButton = document.getElementById('document-preview-page-previous');
  const nextPageButton = document.getElementById('document-preview-page-next');
  const pageNumberInput = document.getElementById('document-preview-page-number');
  let lastFocused = null;
  let currentPage = 1;

  if (!sourcePreview || !modal || !modalBody || !closeButton) return;

  function pageCount() {
    const count = Number.parseInt(pagination?.dataset.pageCount || '0', 10);
    return Number.isFinite(count) && count > 0 ? count : null;
  }

  function updatePageControls() {
    if (!pagination || !pageNumberInput) return;
    const count = pageCount();
    pageNumberInput.value = String(currentPage);
    previousPageButton.disabled = currentPage <= 1;
    nextPageButton.disabled = count ? currentPage >= count : false;
  }

  function showPage(requestedPage) {
    const frame = modalBody.querySelector('.review-frame');
    if (!frame || !pageNumberInput) return;

    const count = pageCount();
    let page = Number.parseInt(requestedPage, 10);
    if (!Number.isFinite(page)) page = currentPage;
    page = Math.max(1, count ? Math.min(page, count) : page);
    currentPage = page;

    const sourceUrl = frame.dataset.documentSource || frame.getAttribute('src').split('#')[0];
    frame.dataset.documentSource = sourceUrl;
    frame.src = `${sourceUrl}#page=${page}&toolbar=0&navpanes=0&scrollbar=1&view=FitH`;
    updatePageControls();
  }

  function openPreview() {
    const previewClone = sourcePreview.cloneNode(true);
    previewClone.querySelectorAll('[data-open-document-preview]').forEach((button) => button.remove());
    previewClone.classList.add('document-preview-modal-content');
    previewClone.removeAttribute('oncontextmenu');

    lastFocused = document.activeElement;
    modalBody.replaceChildren(previewClone);
    modal.hidden = false;
    modal.setAttribute('aria-hidden', 'false');
    document.body.classList.add('document-preview-open');
    currentPage = 1;
    updatePageControls();
    closeButton.focus({ preventScroll: true });
  }

  function closePreview() {
    if (modal.hidden) return;
    modal.hidden = true;
    modal.setAttribute('aria-hidden', 'true');
    modalBody.replaceChildren();
    document.body.classList.remove('document-preview-open');
    lastFocused?.focus?.({ preventScroll: true });
  }

  openButtons.forEach((button) => button.addEventListener('click', openPreview));

  sourcePreview.addEventListener('click', (event) => {
    if (event.target.closest('button, a, input, select, textarea')) return;
    if (event.target.closest('.review-image, .review-generated-preview, .review-text-preview')) {
      openPreview();
    }
  });

  closeButton.addEventListener('click', closePreview);
  previousPageButton?.addEventListener('click', () => showPage(currentPage - 1));
  nextPageButton?.addEventListener('click', () => showPage(currentPage + 1));
  pageNumberInput?.addEventListener('change', () => showPage(pageNumberInput.value));
  pageNumberInput?.addEventListener('keydown', (event) => {
    if (event.key === 'Enter') {
      event.preventDefault();
      showPage(pageNumberInput.value);
      pageNumberInput.select();
    }
  });
  modal.addEventListener('click', (event) => {
    if (event.target === modal) closePreview();
  });

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Tab' && !modal.hidden) {
      const focusable = Array.from(modal.querySelectorAll('a[href], button:not([disabled])'));
      const first = focusable[0];
      const last = focusable[focusable.length - 1];
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    }
    if (event.key === 'Escape' && !modal.hidden) {
      event.preventDefault();
      closePreview();
    }
  });

  window.openDocumentPreview = openPreview;
})();
