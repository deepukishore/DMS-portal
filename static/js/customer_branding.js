(function () {
  const brands = window.CUSTOMER_BRANDS || {};
  const staticRoot = '/static/';

  function get(customerName) {
    return brands[customerName] || null;
  }

  function logoUrl(customerName) {
    const brand = get(customerName);
    return brand ? `${staticRoot}${brand.logo}` : '';
  }

  function createLogo(customerName, variant = 'card') {
    const brand = get(customerName);
    const frame = document.createElement('span');
    frame.className = `customer-logo customer-logo-${variant}${brand ? '' : ' customer-logo-fallback'}`;

    if (!brand) {
      const fallback = document.createElement('span');
      fallback.setAttribute('aria-hidden', 'true');
      fallback.textContent = (customerName || '?').charAt(0);
      frame.appendChild(fallback);
      return frame;
    }

    const image = document.createElement('img');
    image.src = logoUrl(customerName);
    image.alt = `${brand.display_name || customerName} logo`;
    image.loading = 'lazy';
    frame.appendChild(image);
    return frame;
  }

  function createBadge(customerName, compact = false) {
    const badge = document.createElement('span');
    badge.className = `customer-brand-badge${compact ? ' is-compact' : ''}`;
    badge.dataset.customerName = customerName;
    badge.appendChild(createLogo(customerName, 'inline'));

    const name = document.createElement('span');
    name.className = 'customer-brand-name';
    name.textContent = customerName;
    badge.appendChild(name);
    return badge;
  }

  function createBanner(customerName) {
    const brand = get(customerName);
    if (!brand) return null;

    const banner = document.createElement('section');
    banner.className = `customer-banner${brand.banner_tone ? ` customer-banner-${brand.banner_tone}` : ''}`;
    banner.dataset.customerName = customerName;
    banner.setAttribute('aria-label', customerName);

    const image = document.createElement('img');
    image.src = logoUrl(customerName);
    image.alt = `${brand.display_name || customerName} logo`;

    const caption = document.createElement('div');
    caption.className = 'customer-banner-caption';
    const eyebrow = document.createElement('span');
    eyebrow.textContent = 'Customer folder';
    const title = document.createElement('strong');
    title.textContent = customerName;
    caption.append(eyebrow, title);
    banner.append(image, caption);
    return banner;
  }

  function mountBanner(target, customerName) {
    const element = typeof target === 'string' ? document.querySelector(target) : target;
    if (!element) return;
    element.replaceChildren();
    const banner = createBanner(customerName);
    if (banner) element.appendChild(banner);
  }

  function bindSelect(select) {
    if (!select) return;
    if (select.dataset.customerBrandBound === 'true') {
      select._updateCustomerBrand?.();
      return;
    }
    select.dataset.customerBrandBound = 'true';

    const preview = document.createElement('div');
    preview.className = 'customer-select-brand';
    preview.hidden = true;
    select.insertAdjacentElement('afterend', preview);

    const update = () => {
      const customerName = select.value;
      preview.replaceChildren();
      if (!get(customerName)) {
        preview.hidden = true;
        return;
      }
      preview.appendChild(createBadge(customerName, true));
      preview.hidden = false;
    };

    select.addEventListener('change', update);
    select._updateCustomerBrand = update;
    update();
  }

  function init(root = document) {
    root.querySelectorAll('[data-customer-select]').forEach(bindSelect);
  }

  window.CustomerBrand = {
    get,
    logoUrl,
    createLogo,
    createBadge,
    createBanner,
    mountBanner,
    bindSelect,
    init,
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => init());
  } else {
    init();
  }
})();
