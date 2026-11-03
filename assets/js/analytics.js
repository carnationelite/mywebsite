/*
 * CarNation Elite — Google Analytics 4 (single shared tag + events)
 * Loaded once in the <head> of every page:
 *   <script src="/assets/js/analytics.js"></script>
 *
 * Events sent to GA4:
 *   phone_click               tel: links
 *   booking_click             links to calendly.com
 *   calendly_event_scheduled  Calendly embed reports a completed booking (postMessage)
 *   directions_click          Google / Apple Maps links
 *   social_click              Instagram, TikTok, Yelp, Facebook, X, LinkedIn
 *   form_submit               any <form> submitted on the site
 *
 * To track something new from page code: window.ceTrack('event_name', { ... })
 */
(function () {
  'use strict';

  var GA4_ID = 'G-3HL7JENB2E';

  if (window.__ceAnalyticsLoaded) return; // never load twice
  window.__ceAnalyticsLoaded = true;

  // --- GA4 base tag ---------------------------------------------------------
  window.dataLayer = window.dataLayer || [];
  window.gtag = window.gtag || function () { window.dataLayer.push(arguments); };
  window.gtag('js', new Date());
  window.gtag('config', GA4_ID);

  var tag = document.createElement('script');
  tag.async = true;
  tag.src = 'https://www.googletagmanager.com/gtag/js?id=' + GA4_ID;
  (document.head || document.documentElement).appendChild(tag);

  // --- helpers --------------------------------------------------------------
  function track(name, params) {
    try { window.gtag('event', name, params || {}); } catch (e) { /* never break the page */ }
  }
  window.ceTrack = track;

  function clean(text) {
    return (text || '').replace(/\s+/g, ' ').trim().slice(0, 100);
  }

  // Where on the page the click happened: header, footer, mobile nav, chatbot or body.
  function area(el) {
    if (el.closest('header, .main-header, .main-menu, .main-menu-two')) return 'header';
    if (el.closest('footer, .site-footer, .site-footer-two')) return 'footer';
    if (el.closest('.mobile-nav__wrapper, .mobile-bottom-nav')) return 'mobile_nav';
    if (el.closest('.ai-chatbot-window')) return 'chatbot';
    return 'body';
  }

  var SOCIAL = [
    [/(^|\.)instagram\.com$/i, 'instagram'],
    [/(^|\.)tiktok\.com$/i, 'tiktok'],
    [/(^|\.)yelp\.com$/i, 'yelp'],
    [/(^|\.)facebook\.com$/i, 'facebook'],
    [/(^|\.)(x|twitter)\.com$/i, 'x'],
    [/(^|\.)linkedin\.com$/i, 'linkedin']
  ];

  function isMaps(url) {
    var h = url.hostname, p = url.pathname;
    return (/(^|\.)google\.[a-z.]+$/i.test(h) && p.indexOf('/maps') === 0) ||
      /^maps\.google\./i.test(h) || /^maps\.app\.goo\.gl$/i.test(h) ||
      (/^goo\.gl$/i.test(h) && p.indexOf('/maps') === 0) || /^maps\.apple\.com$/i.test(h);
  }

  // --- link clicks (one delegated listener, capture phase) ------------------
  document.addEventListener('click', function (e) {
    var a = e.target && e.target.closest ? e.target.closest('a[href]') : null;
    if (!a) return;
    var href = a.getAttribute('href') || '';
    var base = { link_text: clean(a.textContent || a.getAttribute('aria-label')), link_location: area(a) };

    if (/^tel:/i.test(href)) {
      base.link_url = href;
      track('phone_click', base);
      return;
    }

    var url;
    try { url = new URL(a.href, location.href); } catch (err) { return; }
    base.link_url = url.href;

    if (/(^|\.)calendly\.com$/i.test(url.hostname)) {
      track('booking_click', base);
      return;
    }
    if (isMaps(url)) {
      track('directions_click', base);
      return;
    }
    for (var i = 0; i < SOCIAL.length; i++) {
      if (SOCIAL[i][0].test(url.hostname)) {
        base.social_platform = SOCIAL[i][1];
        track('social_click', base);
        return;
      }
    }
  }, true);

  // --- Calendly embed: completed booking -----------------------------------
  // Works where the Calendly widget is embedded on our own page (book-appointment.html).
  // Bookings made on calendly.com itself cannot be seen by this site.
  window.addEventListener('message', function (e) {
    if (!/^https:\/\/([a-z0-9-]+\.)?calendly\.com$/i.test(e.origin)) return;
    var data = e.data;
    if (data && data.event === 'calendly.event_scheduled') {
      track('calendly_event_scheduled', { booking_source: 'calendly_embed' });
    }
  });

  // --- forms ----------------------------------------------------------------
  document.addEventListener('submit', function (e) {
    var f = e.target;
    if (!f || f.tagName !== 'FORM') return;
    track('form_submit', {
      form_id: f.id || '',
      form_name: f.getAttribute('name') || '',
      form_class: clean(f.className)
    });
  }, true);
})();
