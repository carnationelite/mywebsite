/*
 * CarNation Elite — Google Analytics 4 base tag (G-3HL7JENB2E)
 * Exactly one per page, in the <head>:
 *   <script src="/assets/js/analytics.js"></script>
 * Event tracking lives in /assets/js/ga4-events.js.
 */
(function () {
  'use strict';

  var GA4_ID = 'G-3HL7JENB2E';

  if (window.__ceGa4TagLoaded) return; // never load the tag twice
  window.__ceGa4TagLoaded = true;

  window.dataLayer = window.dataLayer || [];
  window.gtag = window.gtag || function () { window.dataLayer.push(arguments); };
  window.gtag('js', new Date());

  // ?ga_debug=1 also sends events to GA4 DebugView for this browser session.
  var debug = false;
  try {
    if (/[?&]ga_debug=1(&|$)/.test(location.search)) sessionStorage.setItem('ce_ga_debug', '1');
    debug = sessionStorage.getItem('ce_ga_debug') === '1';
  } catch (e) { /* storage blocked */ }

  window.gtag('config', GA4_ID, debug ? { debug_mode: true } : {});

  var tag = document.createElement('script');
  tag.async = true;
  tag.src = 'https://www.googletagmanager.com/gtag/js?id=' + GA4_ID;
  (document.head || document.documentElement).appendChild(tag);
})();
