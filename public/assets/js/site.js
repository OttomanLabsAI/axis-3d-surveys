/* Axis 3D Surveys — site behaviour: mobile navigation, carousels, animated
   counters and the demo contact form. No dependencies. */
(function () {
  'use strict';

  // Mobile navigation toggle
  var toggle = document.querySelector('.nav-toggle');
  var panel = document.getElementById('mobile-nav');
  if (toggle && panel) {
    var setOpen = function (open) {
      if (open) { panel.removeAttribute('hidden'); } else { panel.setAttribute('hidden', ''); }
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      toggle.classList.toggle('is-open', open);
    };
    toggle.addEventListener('click', function () { setOpen(panel.hasAttribute('hidden')); });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && !panel.hasAttribute('hidden')) { setOpen(false); toggle.focus(); }
    });
  }

  // Desktop dropdown: Escape closes an open submenu and returns focus to its parent link
  Array.prototype.forEach.call(document.querySelectorAll('.main-nav .has-sub'), function (li) {
    li.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') { var top = li.querySelector(':scope > a'); if (top) { top.focus(); } }
    });
  });

  // Scroll-snap carousels: the buttons scroll by one item
  Array.prototype.forEach.call(document.querySelectorAll('[data-carousel]'), function (c) {
    var track = c.querySelector('.track');
    if (!track) { return; }
    Array.prototype.forEach.call(c.querySelectorAll('[data-dir]'), function (btn) {
      btn.addEventListener('click', function () {
        var item = track.querySelector('.item');
        var step = item ? item.getBoundingClientRect().width + 30 : track.clientWidth;
        track.scrollBy({ left: (btn.getAttribute('data-dir') === 'next' ? 1 : -1) * step, behavior: 'smooth' });
      });
    });
  });

  // Counters count up once they scroll into view (skipped for reduced motion)
  var counters = document.querySelectorAll('[data-count]');
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (counters.length && 'IntersectionObserver' in window && !reduce) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) { return; }
        var el = entry.target, target = parseInt(el.getAttribute('data-count'), 10) || 0;
        var start = null, duration = 1400;
        io.unobserve(el);
        var step = function (now) {
          if (start === null) { start = now; }
          var p = Math.min(1, (now - start) / duration);
          el.textContent = String(Math.round(target * (1 - Math.pow(1 - p, 3))));
          if (p < 1) { window.requestAnimationFrame(step); }
        };
        window.requestAnimationFrame(step);
      });
    }, { threshold: 0.4 });
    Array.prototype.forEach.call(counters, function (el) { io.observe(el); });
  }

  // Demo contact form: validates, then explains it is not wired up yet
  var form = document.querySelector('form[data-demo-form]');
  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (typeof form.reportValidity === 'function' && !form.reportValidity()) { return; }
      var note = form.querySelector('.form-note');
      if (note) {
        note.hidden = false;
        note.textContent = 'Thanks — this is a demo, so nothing has been sent. On the live site your enquiry would be emailed to the team straight away.';
        note.setAttribute('tabindex', '-1');
        note.focus();
      }
      form.reset();
    });
  }
})();
