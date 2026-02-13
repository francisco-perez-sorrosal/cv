/* === Color Themes === */
var THEMES = {
  'warm-paper': {
    bg: '#f8f6f1', bgCard: '#ffffff', bgNav: 'rgba(248,246,241,0.85)',
    ink: '#1a1a2e', inkMuted: '#6b6b7b',
    accent: '#c45d3e', accentLight: '#e8a490', accentBg: '#fdf0ec',
    divider: '#d4d0c8', shadow: 'rgba(26,26,46,0.06)'
  },
  'cool-white': {
    bg: '#f5f7fa', bgCard: '#ffffff', bgNav: 'rgba(245,247,250,0.85)',
    ink: '#1e293b', inkMuted: '#64748b',
    accent: '#3b82f6', accentLight: '#93c5fd', accentBg: '#eff6ff',
    divider: '#e2e8f0', shadow: 'rgba(30,41,59,0.06)'
  },
  'cream': {
    bg: '#faf3eb', bgCard: '#fffdf8', bgNav: 'rgba(250,243,235,0.85)',
    ink: '#2c1810', inkMuted: '#78716c',
    accent: '#b45309', accentLight: '#fbbf24', accentBg: '#fef3c7',
    divider: '#d6d3d1', shadow: 'rgba(44,24,16,0.06)'
  },
  'slate': {
    bg: '#1e293b', bgCard: '#334155', bgNav: 'rgba(30,41,59,0.85)',
    ink: '#e2e8f0', inkMuted: '#94a3b8',
    accent: '#60a5fa', accentLight: '#93c5fd', accentBg: 'rgba(96,165,250,0.1)',
    divider: '#475569', shadow: 'rgba(0,0,0,0.2)'
  },
  'midnight': {
    bg: '#0f172a', bgCard: '#1e293b', bgNav: 'rgba(15,23,42,0.85)',
    ink: '#e2e8f0', inkMuted: '#94a3b8',
    accent: '#a78bfa', accentLight: '#c4b5fd', accentBg: 'rgba(167,139,250,0.1)',
    divider: '#334155', shadow: 'rgba(0,0,0,0.3)'
  }
};

var SERIF_FONTS = new Set(['Merriweather', 'Libre Baskerville', 'Crimson Text']);

/* === Apply Theme === */
function applyTheme(name) {
  var t = THEMES[name];
  if (!t) return;
  var s = document.documentElement.style;
  s.setProperty('--bg', t.bg);
  s.setProperty('--bg-card', t.bgCard);
  s.setProperty('--ink', t.ink);
  s.setProperty('--ink-muted', t.inkMuted);
  s.setProperty('--accent', t.accent);
  s.setProperty('--accent-light', t.accentLight);
  s.setProperty('--accent-bg', t.accentBg);
  s.setProperty('--divider', t.divider);
  s.setProperty('--shadow', t.shadow);
  document.getElementById('nav').style.backgroundColor = t.bgNav;
  document.querySelectorAll('.color-swatch').forEach(function(sw) {
    sw.classList.toggle('active', sw.dataset.theme === name);
  });
  localStorage.setItem('cv-theme', name);
}

/* === Apply Font === */
function applyFont(fontName) {
  var fallback = SERIF_FONTS.has(fontName) ? 'Georgia, serif' : 'system-ui, sans-serif';
  var encoded = fontName.replace(/ /g, '+');
  if (fontName !== 'DM Sans') {
    var url = 'https://fonts.googleapis.com/css2?family=' + encoded + ':wght@300;400;500;600&display=swap';
    var link = document.getElementById('extra-font');
    if (!link) {
      link = document.createElement('link');
      link.id = 'extra-font';
      link.rel = 'stylesheet';
      document.head.appendChild(link);
    }
    link.href = url;
  }
  document.documentElement.style.setProperty('--font-body', "'" + fontName + "', " + fallback);
  localStorage.setItem('cv-font', fontName);
}

/* === Color Picker === */
document.querySelectorAll('.color-swatch').forEach(function(btn) {
  btn.addEventListener('click', function() { applyTheme(this.dataset.theme); });
});

/* === Font Selector === */
var fontSel = document.getElementById('font-selector');
fontSel.addEventListener('change', function() { applyFont(this.value); });

/* === Restore Saved Preferences === */
var savedTheme = localStorage.getItem('cv-theme');
if (savedTheme && THEMES[savedTheme]) applyTheme(savedTheme);
var savedFont = localStorage.getItem('cv-font');
if (savedFont) { fontSel.value = savedFont; applyFont(savedFont); }

/* === Nav: show on scroll past hero === */
var navEl = document.getElementById('nav');
var heroEl = document.querySelector('.hero');
if (heroEl) {
  new IntersectionObserver(function(entries) {
    navEl.classList.toggle('visible', !entries[0].isIntersecting);
  }, { threshold: 0.1 }).observe(heroEl);
}

/* === Nav: auto-generate links from sections with data-label === */
var navLinksEl = document.getElementById('nav-links');
document.querySelectorAll('section[data-label]').forEach(function(sec) {
  var label = sec.dataset.label;
  sec.id = sec.id || label.toLowerCase().replace(/\s+/g, '-');
  var a = document.createElement('a');
  a.href = '#' + sec.id;
  a.textContent = label;
  navLinksEl.appendChild(a);
});

/* === Section reveal on scroll === */
var secObs = new IntersectionObserver(function(entries) {
  entries.forEach(function(e) { if (e.isIntersecting) e.target.classList.add('in-view'); });
}, { threshold: 0.12 });
document.querySelectorAll('section').forEach(function(s) { secObs.observe(s); });

/* === Expandable Components === */
document.querySelectorAll('.expandable').forEach(function(el) {
  el.addEventListener('click', function(e) {
    if (e.target.closest('a')) return;
    this.classList.toggle('expanded');
  });
});

/* === Stat number animation === */
document.querySelectorAll('.stat-number').forEach(function(el) {
  new IntersectionObserver(function(entries, obs) {
    if (!entries[0].isIntersecting) return;
    var text = el.textContent;
    var match = text.match(/~?(\d+)/);
    if (!match) return;
    var target = parseInt(match[1]);
    var prefix = text.startsWith('~') ? '~' : '';
    var suffix = text.replace(/~?\d+/, '');
    var start = performance.now();
    function tick(now) {
      var p = Math.min((now - start) / 1200, 1);
      var eased = 1 - Math.pow(1 - p, 3);
      el.textContent = prefix + Math.round(eased * target) + suffix;
      if (p < 1) requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
    obs.unobserve(el);
  }, { threshold: 0.5 }).observe(el);
});
