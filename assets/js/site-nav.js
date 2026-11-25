/*
 * CarNation Elite: accessible mobile menu for pages without the theme's jQuery menu
 * (blog, services, vehicles, pricing pages).
 *   <script src="/assets/js/site-nav.js" defer></script>
 *
 * - Below 1200px the theme hides .main-menu__list and shows .mobile-nav__toggler.
 *   On these pages nothing handled that tap, so the menu never opened.
 * - Uses #ce-mobile-menu if the page has one; otherwise builds it from .main-menu__list.
 * - Turns the toggler into a real button (aria-expanded, aria-controls), closes on Esc
 *   and returns focus to the button, closes when resized to desktop.
 * - Does nothing on pages that have the theme menu (.mobile-nav__wrapper) and never
 *   runs twice.
 */
(function () {
  'use strict';
  if (window.__ceSiteNavLoaded) return;
  window.__ceSiteNavLoaded = true;

  function init() {
    if (document.querySelector('.mobile-nav__wrapper')) return; // theme menu handles it

    var toggler = document.querySelector('.mobile-nav__toggler');
    var list = document.querySelector('.main-menu__list');
    if (!toggler || !list) return;

    injectStyles();

    // Use an existing menu, or build one from the desktop links.
    var menu = document.getElementById('ce-mobile-menu');
    if (!menu) {
      menu = document.createElement('nav');
      menu.id = 'ce-mobile-menu';
      menu.className = 'ce-mobile-menu';
      menu.setAttribute('aria-label', 'Mobile');
      var ul = document.createElement('ul');
      var links = list.querySelectorAll('a[href]');
      for (var i = 0; i < links.length; i++) {
        var li = document.createElement('li');
        var a = links[i].cloneNode(true);
        li.appendChild(a);
        ul.appendChild(li);
      }
      menu.appendChild(ul);
      var actions = document.createElement('div');
      actions.className = 'ce-mm-actions';
      actions.innerHTML =
        '<a class="ce-mm-call" href="tel:+12145974922">Call +1 (214) 597-4922</a>' +
        '<a class="ce-mm-book" href="https://calendly.com/carnationelite/schedule-your-appointment" target="_blank" rel="noopener">Book Now<span class="ce-vh"> (opens in a new tab)</span></a>';
      menu.appendChild(actions);
      var navEl = toggler.closest('nav') || toggler.closest('header');
      (navEl && navEl.parentNode ? navEl.parentNode : document.body)
        .insertBefore(menu, navEl ? navEl.nextSibling : null);
    }
    menu.hidden = true;

    // Make the toggler a real, labelled button.
    var btn = toggler;
    if (btn.tagName !== 'BUTTON') {
      var b = document.createElement('button');
      b.type = 'button';
      b.className = btn.className;
      b.innerHTML = btn.innerHTML;
      btn.parentNode.replaceChild(b, btn);
      btn = b;
    }
    btn.classList.add('ce-menu-btn');
    if (!btn.id) btn.id = 'ce-menu-toggle';
    btn.setAttribute('aria-controls', 'ce-mobile-menu');
    btn.setAttribute('aria-expanded', 'false');
    btn.setAttribute('aria-label', 'Open menu');
    // Inline icon, so the button never depends on the icon-font CDN loading.
    if (!btn.querySelector('svg')) {
      btn.innerHTML = '<svg width="26" height="26" viewBox="0 0 24 24" focusable="false"><path d="M3 6h18M3 12h18M3 18h18" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/></svg>';
    }
    var icons = btn.querySelectorAll('i, svg');
    for (var j = 0; j < icons.length; j++) icons[j].setAttribute('aria-hidden', 'true');

    function setOpen(open) {
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
      btn.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
      menu.hidden = !open;
    }
    btn.addEventListener('click', function () {
      setOpen(btn.getAttribute('aria-expanded') !== 'true');
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && btn.getAttribute('aria-expanded') === 'true') {
        setOpen(false);
        btn.focus();
      }
    });
    window.addEventListener('resize', function () {
      if (window.innerWidth >= 1200) setOpen(false);
    });
  }

  function injectStyles() {
    if (document.getElementById('ce-site-nav-css')) return;
    var css =
      '.ce-menu-btn{background:transparent;border:0;padding:9px;min-width:48px;min-height:48px;color:#0F172A;display:inline-flex;align-items:center;justify-content:center;cursor:pointer;font-size:1.4rem;}' +
      '.ce-menu-btn:focus-visible{outline:3px solid #2563eb;outline-offset:2px;}' +
      '.ce-mobile-menu{background:#0F172A;padding:6px 20px 18px;}' +
      '.ce-mobile-menu[hidden]{display:none !important;}' +
      '.ce-mobile-menu ul{list-style:none;margin:0;padding:0;}' +
      '.ce-mobile-menu li a{display:flex;align-items:center;min-height:48px;color:#fff;text-decoration:none;border-bottom:1px solid rgba(255,255,255,.12);font-weight:600;}' +
      '.ce-mobile-menu li a[aria-current]{color:#F97316;}' +
      '.ce-mobile-menu a:focus-visible{outline:3px solid #93c5fd;outline-offset:2px;}' +
      '.ce-mm-actions{display:flex;flex-wrap:wrap;gap:10px;margin-top:14px;}' +
      '.ce-mm-actions a{display:inline-flex;align-items:center;justify-content:center;min-height:48px;padding:0 18px;border-radius:6px;font-weight:600;text-decoration:none;}' +
      '.ce-mm-call{background:#F97316;color:#0F172A !important;}' +
      '.ce-mm-book{border:2px solid #fff;color:#fff !important;}' +
      '.ce-vh{position:absolute !important;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0;}' +
      '@media(min-width:1200px){.ce-menu-btn,.ce-mobile-menu{display:none !important;}}';
    var s = document.createElement('style');
    s.id = 'ce-site-nav-css';
    s.appendChild(document.createTextNode(css));
    document.head.appendChild(s);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
