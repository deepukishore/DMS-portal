(function () {
  'use strict';

  const config = window.PRODUCT_TOUR_CONFIG || {};
  const labels = {
    next: config.labels?.next || 'Next',
    previous: config.labels?.previous || 'Previous',
    finish: config.labels?.finish || 'Finish'
  };
  const dashboardSteps = [
    {
      selector: '[data-tour="app-header"]',
      title: 'Welcome to Smart DMS',
      description: 'This workspace keeps document submission, review, controlled access, and reporting together.'
    },
    {
      selector: '[data-tour="main-navigation"]',
      title: 'Move around the portal',
      description: 'Use the main navigation to upload documents, open the approval queue, browse the library, track approvals, and view reports.'
    },
    {
      selector: '[data-tour="library-overview"]',
      title: 'Check library coverage',
      description: 'Open a controlled document category and see its available records from the library overview.'
    },
    {
      selector: '[data-tour="quick-actions"]',
      title: 'Start common tasks quickly',
      description: 'These shortcuts take you directly to uploads, approvals, tracking, reports, and revision history.'
    },
    {
      selector: '[data-tour="document-search"]',
      title: 'Find the document you need',
      description: 'Search and filter documents by file, uploader, document number, plant, department, status, customer, or date.'
    },
    {
      selector: '[data-tour="notifications"]',
      title: 'Stay informed',
      description: 'Notifications alert you to approval activity and important portal updates. You can mark or clear them here.'
    }
  ];

  const sharedPageSteps = [
    {
      selector: '[data-tour="app-header"], .review-brand-link',
      title: 'Application header',
      description: 'Use the header to return home, check your current location, and access common portal controls.'
    },
    {
      selector: '[data-tour="main-navigation"]',
      title: 'Main navigation',
      description: 'Move between document submission, approvals, the controlled library, reports, and account tools.'
    }
  ];

  const pageTours = {
    'auth.login': [
      { selector: '.auth-panel-left', title: 'Welcome to Smart DMS', description: 'This portal provides controlled document submission, approval, access, and reporting.' },
      { selector: '.auth-card', title: 'Sign in', description: 'Enter your registered email or employee ID and password to open your workspace.' },
      { selector: '.auth-form', title: 'Account access', description: 'Sign in, recover a forgotten password, or continue to registration if you are new.' }
    ],
    'auth.register': [
      { selector: '.auth-panel-left', title: 'Create your Smart DMS account', description: 'Registration connects your identity, plant, and department to controlled document access.' },
      { selector: '.auth-card', title: 'Employee registration', description: 'Complete the required employee and contact information for your account.' },
      { selector: '.auth-register-form', title: 'Secure your account', description: 'Choose your plant and department, then create and confirm a secure password.' }
    ],
    'auth.reset_password': [
      { selector: '.reset-brand, .auth-card', title: 'Reset your password', description: 'Use this secure page to replace the password for your Smart DMS account.' },
      { selector: '.auth-form', title: 'Choose a new password', description: 'Enter and confirm the new password, then select Update password.' }
    ],
    'upload.index': [
      { selector: '.upload-page-header, .page-header', title: 'Upload documents', description: 'This guided form collects the file and controlled-document information needed for approval.' },
      { selector: '.upload-file-step', title: 'Choose files', description: 'Drop files here or browse from your device. The selected files are listed before submission.' },
      { selector: '.upload-details-step', title: 'Add document details', description: 'Set the document number, revision, category, plant, department, and other required metadata.' },
      { selector: '.upload-revision-step, .library-path-card', title: 'Revision and destination', description: 'Choose whether this is a revision and confirm where the controlled document belongs.' },
      { selector: '.upload-submit-row', title: 'Submit for approval', description: 'Review the information and send the document into the approval workflow.' }
    ],
    'approvals.index': [
      { selector: '.page-header', title: 'Approval queue', description: 'Review documents that are waiting for your decision or monitor completed approval records.' },
      { selector: '.approval-stats-grid', title: 'Approval summary', description: 'See pending, approved, rejected, and hold totals at a glance.' },
      { selector: '.approval-records-filter', title: 'Find approval records', description: 'Search records and narrow the list by approval status.' },
      { selector: '.approval-records-wrap', title: 'Review queue', description: 'Open a document to inspect its content and complete the required approval action.' }
    ],
    'tracking.index': [
      { selector: '.page-header', title: 'Track approvals', description: 'Follow the current stage and decision history of document submissions.' },
      { selector: '.track-summary', title: 'Workflow summary', description: 'These totals show the overall state of the approval work you can access.' },
      { selector: '.filter-bar', title: 'Search and scope', description: 'Find a submission and switch between the approval scopes available to you.' },
      { selector: '.tracker-list, .empty-state', title: 'Approval timelines', description: 'Each record shows its progress through submission, first review, and final approval.' }
    ],
    'document_library.index': [
      { selector: '.page-header', title: 'Document library', description: 'Browse controlled documents by library area, folder, plant, and department.' },
      { selector: '.library-overview-panel, #library-content', title: 'Library folders', description: 'Choose a folder to open its controlled records and available document structure.' },
      { selector: '#library-content', title: 'Folder contents', description: 'Use this workspace to move through departments and open the documents you need.' }
    ],
    'graphics_report.index': [
      { selector: '.page-header', title: 'Graphics report', description: 'This page summarizes document and approval activity as visual reports.' },
      { selector: '.summary-grid', title: 'Key totals', description: 'Review the most important approval and document counts before exploring the charts.' },
      { selector: '.report-carousel', title: 'Interactive charts', description: 'Move between report views, pause automatic rotation, and inspect trends in detail.' }
    ],
    'revision_history.index': [
      { selector: '.page-header', title: 'Revision history', description: 'Review controlled-document versions and the people responsible for each revision.' },
      { selector: '.filter-bar', title: 'Filter revisions', description: 'Search the revision register and narrow it to the records you need.' },
      { selector: '.revision-history-wrap', title: 'Revision register', description: 'Compare current and previous versions, dates, and revision ownership.' }
    ],
    'archive.index': [
      { selector: '.page-header', title: 'Archive', description: 'High-level users can review documents removed from the active portal.' },
      { selector: '.pg-bar', title: 'Archive pagination', description: 'Change the number of archived records shown and move between result pages.' },
      { selector: '.table-wrap', title: 'Archived records', description: 'Inspect archived document details and perform the actions permitted for your role.' }
    ],
    'system_log.index': [
      { selector: '.page-header', title: 'System log', description: 'Audit important user and document activity across the portal.' },
      { selector: '.log-filter-tabs', title: 'Activity filters', description: 'Switch between log categories to focus on the events you need.' },
      { selector: '.table-wrap', title: 'Audit events', description: 'Review who performed each action and when it occurred.' }
    ],
    'people.index': [
      { selector: '.people-hero', title: 'People and access', description: 'Review registered users and how their quality access is configured.' },
      { selector: '.people-level-summary', title: 'Access-level summary', description: 'See how users are distributed across the available QMS access levels.' },
      { selector: '.people-filters', title: 'Find a user', description: 'Search and filter the directory by identity, plant, department, or access level.' },
      { selector: '.people-table-wrapper', title: 'User directory', description: 'Inspect user details and update access where your role permits it.' }
    ],
    'profile.index': [
      { selector: '.profile-hero', title: 'Your profile', description: 'Review your portal identity, role, plant, department, and avatar.' },
      { selector: '.profile-details-card', title: 'Profile and security', description: 'Update personal details or open the password-change controls.' },
      { selector: '.profile-activity-card', title: 'Your activity', description: 'Review the recent portal actions associated with your account.' }
    ],
    'notifications.portal_updates': [
      { selector: '.page-header', title: 'Portal updates', description: 'Administrators can publish important announcements to every registered user.' },
      { selector: '.portal-update-form', title: 'Create an announcement', description: 'Add a concise title, message, and optional destination for the update.' },
      { selector: '.portal-update-guide', title: 'Delivery preview', description: 'This guide explains how the popup and notification will appear to users.' }
    ],
    'about.index': [
      { selector: '.hero-panel', title: 'About Smart DMS', description: 'Learn what the portal controls and how it supports the organization.' },
      { selector: '.about-company-section', title: 'Company context', description: 'Review the organization, locations, and operating context behind the portal.' },
      { selector: '.about-tour-steps', title: 'Document workflow', description: 'Follow the main path from upload through review, approval, and controlled access.' },
      { selector: '.about-features-grid', title: 'Portal capabilities', description: 'Explore the tools available for document control, tracking, reporting, and governance.' }
    ],
    'about.about_track_docs': [
      { selector: '.page-header', title: 'About the system', description: 'This overview explains the purpose and scope of Smart DMS.' },
      { selector: '.info-grid-main-aside', title: 'System information', description: 'Review the platform summary and the document-control needs it addresses.' },
      { selector: '.benefits-grid', title: 'Key benefits', description: 'See how the portal improves control, visibility, traceability, and access.' },
      { selector: '.docs-category-grid', title: 'Document areas', description: 'Explore the categories and controlled information managed by the system.' }
    ],
    'customer_records.index': [
      { selector: '.page-header', title: 'Customer records', description: 'Browse controlled records associated with a specific customer.' },
      { selector: '#customer-grid', title: 'Choose a customer', description: 'Select a customer card to load its available document folders and files.' },
      { selector: '#asset-panel', title: 'Customer documents', description: 'Use the loaded workspace to select a plant or department and open a file.' }
    ],
    'plant_assets.index': [
      { selector: '.page-header', title: 'Plant document repository', description: 'Browse controlled document folders organized by manufacturing plant.' },
      { selector: '#plant-list', title: 'Choose a plant', description: 'Expand a plant to see its departments and the files available to you.' }
    ],
    'procedures.index': [
      { selector: '.page-header', title: 'Procedures', description: 'Choose a procedure category to begin browsing controlled documents.' },
      { selector: '.category-card-grid', title: 'Procedure categories', description: 'Each card opens a distinct procedure area and its plant folders.' }
    ],
    'procedures.sub_index': [
      { selector: '.page-header', title: 'Procedure documents', description: 'Browse this procedure category by plant and department.' },
      { selector: '#plant-grid', title: 'Choose a plant', description: 'Select a plant to load its available departments.' },
      { selector: '#asset-panel', title: 'Department files', description: 'Choose a department and open the controlled procedure files listed here.' }
    ],
    'approvals.review_document': [
      { selector: '.review-topbar, .review-card-narrow', title: 'Approval review', description: 'Review the document status and the request that needs your attention.' },
      { selector: '.review-document-details-card', title: 'Document details', description: 'Confirm the document number, revision, category, requester, and upload date.' },
      { selector: '.review-preview', title: 'Document preview', description: 'Inspect the controlled document content before making a decision.' },
      { selector: '#approval-form, .hold-correction-card', title: 'Complete the review', description: 'Approve, reject, place the document on hold, or provide the requested correction.' }
    ],
    'dashboard.view_document': [
      { selector: '.review-topbar', title: 'Document view', description: 'See the file name, bookmark control, and current approval status.' },
      { selector: '.review-document-details-card', title: 'Document details', description: 'Review the core controlled-document metadata at a glance.' },
      { selector: '.review-preview', title: 'Document preview', description: 'Read the available document content securely within the portal.' }
    ],
    'dashboard.view_document_by_file': [
      { selector: '.review-topbar', title: 'Document view', description: 'See the file name, bookmark control, and current approval status.' },
      { selector: '.review-document-details-card', title: 'Document details', description: 'Review the core controlled-document metadata at a glance.' },
      { selector: '.review-preview', title: 'Document preview', description: 'Read the available document content securely within the portal.' }
    ]
  };

  const categoryBrowserSteps = [
    { selector: '.page-header', title: 'Controlled document category', description: 'Browse this document category by plant and department.' },
    { selector: '#plant-grid', title: 'Choose a plant', description: 'Select a plant to load the departments available in this category.' },
    { selector: '#asset-panel', title: 'Department files', description: 'Choose a department and open one of its controlled documents.' }
  ];

  const genericPageSteps = [
    { selector: '.page-header, .hero-panel, .review-topbar', title: 'Page overview', description: 'This header explains the purpose of the current workspace.' },
    { selector: '.filter-bar, .people-filters, .log-filter-tabs', title: 'Search and filters', description: 'Use these controls to narrow the information displayed on this page.' },
    { selector: '.table-wrap, .surface-panel, .tracker-list, .category-card-grid, .plant-card-grid', title: 'Page workspace', description: 'This is the main working area for the current page.' }
  ];

  const root = document.getElementById('product-tour');
  const popover = root?.querySelector('.product-tour-popover');
  const highlight = root?.querySelector('.product-tour-highlight');
  const progress = document.getElementById('product-tour-progress');
  const title = document.getElementById('product-tour-title');
  const description = document.getElementById('product-tour-description');
  const previousButton = document.getElementById('product-tour-previous');
  const nextButton = document.getElementById('product-tour-next');
  const skipButton = document.getElementById('product-tour-skip');
  const closeButton = document.getElementById('product-tour-close');
  const launchButton = document.getElementById('product-tour-launch');
  const backdropTop = root?.querySelector('.product-tour-backdrop-top');
  const backdropRight = root?.querySelector('.product-tour-backdrop-right');
  const backdropBottom = root?.querySelector('.product-tour-backdrop-bottom');
  const backdropLeft = root?.querySelector('.product-tour-backdrop-left');
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const mobileNavigation = window.matchMedia('(max-width: 700px)');
  const pageEndpoint = config.pageEndpoint || 'unknown-page';
  const completionKey = `dms-product-tour-complete-v2-${config.userKey || 'guest'}-${pageEndpoint}`;

  let availableSteps = [];
  let currentIndex = 0;
  let active = false;
  let lastFocused = null;
  let positionFrame = null;
  let settleTimer = null;

  function getPageSteps() {
    if (pageEndpoint === 'dashboard.index') return dashboardSteps;
    if (pageEndpoint.startsWith('categories.')) {
      return [...sharedPageSteps, ...categoryBrowserSteps];
    }
    return [...sharedPageSteps, ...(pageTours[pageEndpoint] || genericPageSteps)];
  }

  function isAvailableTarget(element) {
    if (!element || !element.isConnected || !element.getClientRects().length) return false;
    const style = window.getComputedStyle(element);
    return style.display !== 'none' && style.visibility !== 'hidden';
  }

  function setRect(element, top, left, width, height) {
    if (!element) return;
    element.style.top = `${Math.max(0, top)}px`;
    element.style.left = `${Math.max(0, left)}px`;
    element.style.width = `${Math.max(0, width)}px`;
    element.style.height = `${Math.max(0, height)}px`;
  }

  function positionTour() {
    if (!active || !popover || !highlight) return;
    const step = availableSteps[currentIndex];
    const target = step?.element;
    if (!target) return;

    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;
    const targetRect = target.getBoundingClientRect();
    const padding = 8;
    const gap = 16;
    const holeTop = Math.max(6, targetRect.top - padding);
    const holeLeft = Math.max(6, targetRect.left - padding);
    const holeRight = Math.min(viewportWidth - 6, targetRect.right + padding);
    const holeBottom = Math.min(viewportHeight - 6, targetRect.bottom + padding);
    const holeWidth = Math.max(0, holeRight - holeLeft);
    const holeHeight = Math.max(0, holeBottom - holeTop);

    setRect(backdropTop, 0, 0, viewportWidth, holeTop);
    setRect(backdropBottom, holeBottom, 0, viewportWidth, viewportHeight - holeBottom);
    setRect(backdropLeft, holeTop, 0, holeLeft, holeHeight);
    setRect(backdropRight, holeTop, holeRight, viewportWidth - holeRight, holeHeight);
    setRect(highlight, holeTop, holeLeft, holeWidth, holeHeight);

    const popoverRect = popover.getBoundingClientRect();
    const safeMargin = 12;
    const spaceRight = viewportWidth - holeRight;
    const spaceLeft = holeLeft;
    const spaceBelow = viewportHeight - holeBottom;
    let left;
    let top;

    if (spaceRight >= popoverRect.width + gap) {
      left = holeRight + gap;
      top = holeTop + (holeHeight - popoverRect.height) / 2;
    } else if (spaceBelow >= popoverRect.height + gap) {
      left = holeLeft + (holeWidth - popoverRect.width) / 2;
      top = holeBottom + gap;
    } else if (spaceLeft >= popoverRect.width + gap) {
      left = holeLeft - popoverRect.width - gap;
      top = holeTop + (holeHeight - popoverRect.height) / 2;
    } else {
      left = holeLeft + (holeWidth - popoverRect.width) / 2;
      top = holeTop - popoverRect.height - gap;
    }

    left = Math.min(Math.max(safeMargin, left), viewportWidth - popoverRect.width - safeMargin);
    top = Math.min(Math.max(safeMargin, top), viewportHeight - popoverRect.height - safeMargin);
    popover.style.left = `${left}px`;
    popover.style.top = `${top}px`;
  }

  function schedulePosition() {
    if (!active || positionFrame) return;
    positionFrame = window.requestAnimationFrame(() => {
      positionFrame = null;
      positionTour();
    });
  }

  function setMobileNavigationForStep(step) {
    if (!mobileNavigation.matches || typeof window.setSidebarOpen !== 'function') return;
    window.setSidebarOpen(step.element?.matches('[data-tour="main-navigation"]'));
  }

  function showStep(index) {
    if (!active || !availableSteps.length) return;
    currentIndex = Math.min(Math.max(index, 0), availableSteps.length - 1);
    const step = availableSteps[currentIndex];

    setMobileNavigationForStep(step);
    progress.textContent = `Step ${currentIndex + 1} of ${availableSteps.length}`;
    title.textContent = step.title;
    description.textContent = step.description;
    previousButton.textContent = labels.previous;
    previousButton.disabled = currentIndex === 0;
    nextButton.textContent = currentIndex === availableSteps.length - 1 ? labels.finish : labels.next;

    step.element.scrollIntoView({
      behavior: reducedMotion.matches ? 'auto' : 'smooth',
      block: 'center',
      inline: 'nearest'
    });
    schedulePosition();
    if (settleTimer) window.clearTimeout(settleTimer);
    settleTimer = window.setTimeout(positionTour, reducedMotion.matches ? 0 : 420);
    nextButton.focus({ preventScroll: true });
  }

  function endTour(markComplete) {
    if (!active) return;
    active = false;
    if (settleTimer) window.clearTimeout(settleTimer);
    if (positionFrame) window.cancelAnimationFrame(positionFrame);
    settleTimer = null;
    positionFrame = null;
    root.hidden = true;
    root.setAttribute('aria-hidden', 'true');
    document.body.classList.remove('product-tour-open');
    if (markComplete) localStorage.setItem(completionKey, '1');
    if (mobileNavigation.matches && typeof window.setSidebarOpen === 'function') {
      window.setSidebarOpen(false);
    }
    lastFocused?.focus?.({ preventScroll: true });
  }

  function startTour() {
    if (!root || active) return;
    const usedTargets = new Set();
    availableSteps = getPageSteps()
      .map((step) => ({ ...step, element: document.querySelector(step.selector) }))
      .filter((step) => {
        if (!isAvailableTarget(step.element) || usedTargets.has(step.element)) return false;
        usedTargets.add(step.element);
        return true;
      });
    if (!availableSteps.length) return;

    const notificationPanel = document.getElementById('notification-panel');
    if (notificationPanel) notificationPanel.hidden = true;
    lastFocused = document.activeElement;
    active = true;
    currentIndex = 0;
    root.hidden = false;
    root.setAttribute('aria-hidden', 'false');
    document.body.classList.add('product-tour-open');
    showStep(0);
  }

  function launchTour() {
    startTour();
  }

  function trapFocus(event) {
    if (event.key !== 'Tab' || !active || !popover) return;
    const focusable = Array.from(popover.querySelectorAll('button:not([disabled])'));
    if (!focusable.length) return;
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

  previousButton?.addEventListener('click', () => showStep(currentIndex - 1));
  nextButton?.addEventListener('click', () => {
    if (currentIndex === availableSteps.length - 1) {
      endTour(true);
      return;
    }
    showStep(currentIndex + 1);
  });
  skipButton?.addEventListener('click', () => endTour(true));
  closeButton?.addEventListener('click', () => endTour(false));
  launchButton?.addEventListener('click', launchTour);

  document.addEventListener('keydown', (event) => {
    if (!active) return;
    trapFocus(event);
    if (event.key === 'Escape') {
      event.preventDefault();
      endTour(false);
    } else if (event.key === 'ArrowRight') {
      event.preventDefault();
      nextButton.click();
    } else if (event.key === 'ArrowLeft' && currentIndex > 0) {
      event.preventDefault();
      previousButton.click();
    }
  });

  window.addEventListener('resize', schedulePosition);
  window.addEventListener('scroll', schedulePosition, true);

  document.addEventListener('DOMContentLoaded', () => {
    const shouldAutoStart = Boolean(config.autoStart) && localStorage.getItem(completionKey) !== '1';
    if (!shouldAutoStart) return;

    const begin = () => window.setTimeout(startTour, 180);
    const welcomeModal = document.getElementById('welcome-modal');
    if (welcomeModal && !welcomeModal.hidden) {
      window.addEventListener('dms:welcome-closed', begin, { once: true });
    } else {
      begin();
    }
  });

  window.startProductTour = startTour;
})();
