/*
 * CarNation Elite — GA4 event tracking
 * Loaded once per page, after the base tag:
 *   <script src="/assets/js/ga4-events.js" defer></script>
 *
 * Events (GA4 names)          Parameters
 *   phone_click               link_url, click_location, page_location
 *   email_click               click_location, page_location
 *   booking_click             click_location, page_location, service_name (service pages only)
 *   calendly_event_scheduled  page_location, service_name
 *   directions_click          link_url, page_location
 *   social_click              platform, click_location, page_location
 *   form_submit               form_id, page_location
 *   car_inquiry               vehicle_name, inquiry_type, page_location   (carsales.html)
 *
 * Rules: one delegated click listener on document; nothing runs if gtag is missing
 * (ad blockers); duplicate taps within 800 ms are ignored; no personal data is sent.
 * Debug: add ?ga_debug=1 to any URL to log events in the browser console for this
 * session (and see them in GA4 DebugView). Normal visitors get no console output.
 */
(function () {
  'use strict';

  if (window.__ceGa4EventsLoaded) return;
  window.__ceGa4EventsLoaded = true;

  var DEBOUNCE_MS = 800;
  var lastSent = {};

  var DEBUG = false;
  try {
    if (/[?&]ga_debug=1(&|$)/.test(location.search)) sessionStorage.setItem('ce_ga_debug', '1');
    DEBUG = sessionStorage.getItem('ce_ga_debug') === '1';
  } catch (e) { DEBUG = /[?&]ga_debug=1(&|$)/.test(location.search); }

  function log() {
    if (DEBUG && window.console) console.log.apply(console, ['[GA4]'].concat([].slice.call(arguments)));
  }

  function pageLocation() {
    return location.origin + location.pathname + location.search; // no #hash
  }

  // Service slug from /services/<slug>.html, e.g. "brake-repair-service".
  function serviceName() {
    var m = location.pathname.match(/\/services\/(?:[^/]+\/)*([^/]+?)(?:\.html)?$/i);
    return m ? m[1].replace(/-dallas$/i, '') : undefined;
  }

  /*
   * send(name, params, key, leavesPage)
   * key: identifies the clicked thing, for the double-tap guard.
   * leavesPage: true for links that take the visitor off this page.
   */
  function send(name, params, key, leavesPage) {
    if (typeof window.gtag !== 'function') { log('gtag missing, skipped', name); return false; }
    var now = Date.now();
    var dk = name + '|' + (key || '');
    if (lastSent[dk] && now - lastSent[dk] < DEBOUNCE_MS) { log('debounced', name); return false; }
    lastSent[dk] = now;

    var p = {};
    for (var k in params) if (params[k] !== undefined && params[k] !== '') p[k] = params[k];
    p.page_location = pageLocation();
    if (leavesPage) p.transport_type = 'beacon';

    try { window.gtag('event', name, p); } catch (e) { return false; }
    log(name, p);
    return true;
  }
  window.ceGa4 = { send: send }; // for future page code; not used by pages today

  // header / hero / footer / body, from the nearest matching ancestor.
  function clickLocation(el) {
    if (el.closest('.main-slider-two, .main-slider, .page-header, .page-hero, .hero, .cne-hero, .banner')) return 'hero';
    if (el.closest('header, .main-header, .main-header-two, .main-menu, .main-menu-two, .sticky-header, .mobile-nav__wrapper')) return 'header';
    if (el.closest('footer, .site-footer, .site-footer-two, .mobile-bottom-nav')) return 'footer';
    return 'body';
  }

  function hostOf(a) {
    try { return new URL(a.href, location.href); } catch (e) { return null; }
  }

  function isCalendly(u) { return !!u && /(^|\.)calendly\.com$/i.test(u.hostname); }
  function isBookingPage(u) { return !!u && u.origin === location.origin && /\/book-appointment\.html$/i.test(u.pathname); }
  function isMaps(u) {
    if (!u) return false;
    var h = u.hostname, p = u.pathname;
    return (/(^|\.)google\.[a-z.]+$/i.test(h) && p.indexOf('/maps') === 0) ||
      /^maps\.google\.[a-z.]+$/i.test(h) || /^maps\.app\.goo\.gl$/i.test(h) || /^maps\.apple\.com$/i.test(h);
  }
  var SOCIAL = { instagram: /(^|\.)instagram\.com$/i, tiktok: /(^|\.)tiktok\.com$/i, yelp: /(^|\.)yelp\.com$/i, facebook: /(^|\.)facebook\.com$/i };

  // "Book Now", "Book Appointment", "Schedule Service" — text that STARTS with the verb.
  // Avoids blog links such as "Car Maintenance Schedule…" and "scheduled maintenance".
  function looksLikeBooking(el) {
    var t = (el.textContent || el.getAttribute('aria-label') || el.value || '').replace(/\s+/g, ' ').trim();
    return /^(book|schedule)\b(?!d)/i.test(t);
  }

  // Car sales cards (built from Airtable on carsales.html).
  function carInquiry(el, kind) {
    var card = el.closest('.cne-card');
    if (!card) return;
    var title = card.querySelector('.cne-title');
    var name = title ? title.textContent.replace(/\s+/g, ' ').trim().slice(0, 80) : '';
    var sold = card.classList.contains('is-sold');
    var type = kind === 'phone' ? (sold ? 'find_similar' : 'call') : 'test_drive';
    send('car_inquiry', { vehicle_name: name, inquiry_type: type }, 'car|' + (card.getAttribute('data-id') || name) + '|' + type, true);
  }

  // ---- one delegated click listener ------------------------------------------
  document.addEventListener('click', function (e) {
    var target = e.target && e.target.closest ? e.target : null;
    if (!target) return;
    var el = target.closest('a[href], button, input[type="submit"], input[type="button"]');
    if (!el) return;

    var where = clickLocation(el);
    var href = el.tagName === 'A' ? (el.getAttribute('href') || '') : '';

    if (/^tel:/i.test(href)) {
      send('phone_click', { link_url: href.split('?')[0], click_location: where }, href + '|' + where, true);
      carInquiry(el, 'phone');
      return;
    }
    if (/^mailto:/i.test(href)) {
      send('email_click', { click_location: where }, href + '|' + where, true);
      return;
    }

    var u = el.tagName === 'A' ? hostOf(el) : null;

    if (isCalendly(u) || isBookingPage(u) || looksLikeBooking(el)) {
      var leaves = isCalendly(u) || (el.tagName === 'A' && !!u && u.origin !== location.origin) || el.target === '_blank';
      send('booking_click', { click_location: where, service_name: serviceName() },
        'book|' + (u ? u.href : el.textContent) + '|' + where, leaves || isBookingPage(u));
      if (isCalendly(u)) carInquiry(el, 'test_drive');
      return;
    }
    if (isMaps(u)) {
      send('directions_click', { link_url: u.href }, u.href, true);
      return;
    }
    if (u) {
      for (var platform in SOCIAL) {
        if (SOCIAL[platform].test(u.hostname)) {
          send('social_click', { platform: platform, click_location: where }, platform + '|' + where, true);
          return;
        }
      }
    }
  }, true);

  // ---- Calendly embeds (inline widget or popup) --------------------------------
  // Bookings made after a link opens calendly.com in a NEW TAB cannot be seen here.
  var seenBookings = {};
  window.addEventListener('message', function (e) {
    if (e.origin !== 'https://calendly.com') return;
    var d = e.data;
    if (!d || d.event !== 'calendly.event_scheduled') return;
    var id = (d.payload && d.payload.event && d.payload.event.uri) || ('t' + Math.floor(Date.now() / 5000));
    if (seenBookings[id]) return;          // fire once per booking
    seenBookings[id] = true;
    // Only our own fields are sent — never the invitee's name or email from the payload.
    send('calendly_event_scheduled', { service_name: serviceName() }, id, false);
  });

  // ---- forms: fire only when the submission is valid ---------------------------
  document.addEventListener('submit', function (e) {
    var f = e.target;
    if (!f || f.tagName !== 'FORM') return;
    if (!f.querySelector('input, textarea, select')) return;      // wrappers around links, not real forms
    if (typeof f.checkValidity === 'function' && !f.checkValidity()) return;
    // Let the page's own handler run first; if it rejects the form (e.g. marks
    // fields invalid with aria-invalid or the jQuery Validate "error" class), skip.
    setTimeout(function () {
      if (f.querySelector('[aria-invalid="true"], .error:not(label)')) return;
      send('form_submit', { form_id: f.id || f.getAttribute('name') || 'form' }, 'form|' + (f.id || ''), false);
    }, 0);
  }, false);

  log('events ready on', pageLocation());
})();
