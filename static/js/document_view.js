(function () {
  'use strict';

  const sourcePreview = document.querySelector('.document-preview-card .review-preview');
  const modal = document.getElementById('document-preview-modal');
  const modalBody = document.getElementById('document-preview-modal-body');
  const closeButton = document.getElementById('document-preview-modal-close');
  const openButtons = document.querySelectorAll('[data-open-document-preview]');
  let lastFocused = null;

  if (!sourcePreview || !modal || !modalBody || !closeButton) return;

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
  modal.addEventListener('click', (event) => {
    if (event.target === modal) closePreview();
  });

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && !modal.hidden) {
      event.preventDefault();
      closePreview();
    }
  });

  window.openDocumentPreview = openPreview;
})();
