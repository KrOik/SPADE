/*
 * SPADE Tranzy Integration
 * - Loads Tranzy UMD and wires it to SPADE's minimal language selector
 * - Uses a Netlify proxy to call Microsoft Translator securely
 *
 * Docs reference: Tranzy usage and options [0]
 * CDN: https://unpkg.com/tranzy/dist/tranzy.umd.js
 */
(function () {
  const DEFAULT_IGNORE_SELECTORS = [
    'style', 'script', 'noscript', 'kbd', 'code', 'pre', 'input', 'textarea',
    '[contenteditable="true"]', '.tranzy-ignore'
  ];

  const LOCAL_IGNORE_SELECTORS = [
    '[data-translate]',
    '[data-translate-placeholder]'
  ];

  const CONFIG = {
    proxyUrl: '/.netlify/functions/translator-proxy',
    defaultToLang: 'zh-Hans',
    defaultFromLang: '',
  };

  const state = {
    tranzy: null,
    proxyConfigured: false,
    initialized: false
  };

  async function checkProxyConfigured() {
    try {
      const res = await fetch(`${CONFIG.proxyUrl}?ping=1`);
      if (!res.ok) return false;
      const data = await res.json();
      return Boolean(data && data.configured);
    } catch (e) {
      return false;
    }
  }

  async function customTranslateFn(text, toLang, fromLang) {
    // If proxy not configured, no remote translation. Return original.
    if (!state.proxyConfigured) return text;

    const payload = {
      mode: 'translate',
      texts: [String(text || '')],
      to: toLang || CONFIG.defaultToLang,
      from: fromLang || CONFIG.defaultFromLang
    };

    try {
      const res = await fetch(CONFIG.proxyUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (!res.ok || !data.success) {
        return text;
      }
      const first = Array.isArray(data.translations) ? data.translations[0] : null;
      return (first && first.text) ? first.text : text;
    } catch (err) {
      console.warn('Remote translate failed, fallback to original text:', err);
      return text;
    }
  }

  function getCurrentLanguage() {
    try {
      const inst = window.SPADE_LANGUAGE_SELECTOR_MINIMAL && window.SPADE_LANGUAGE_SELECTOR_MINIMAL.getInstance();
      if (inst && inst.state && inst.state.currentLanguage) return inst.state.currentLanguage;
      // fallback to browser
      const browserLang = navigator.language || navigator.userLanguage || 'en';
      if (browserLang.startsWith('zh')) return 'zh-Hans';
      if (browserLang.startsWith('fr')) return 'fr';
      if (browserLang.startsWith('pt')) return 'pt';
      if (browserLang.startsWith('es')) return 'es';
      if (browserLang.startsWith('de')) return 'de';
      if (browserLang.startsWith('ja')) return 'ja';
      return 'en';
    } catch (e) {
      return CONFIG.defaultToLang;
    }
  }

  async function initTranzy() {
    if (state.initialized) return;

    if (!window.Tranzy || !Tranzy.Translator) {
      console.warn('Tranzy UMD not loaded. Ensure CDN script is included.');
      return;
    }

    state.proxyConfigured = await checkProxyConfigured();

    const toLang = getCurrentLanguage();
    const translator = new Tranzy.Translator({
      toLang: toLang,
      fromLang: '', // let service detect if provided
      ignore: [...DEFAULT_IGNORE_SELECTORS, ...LOCAL_IGNORE_SELECTORS],
      translateFn: customTranslateFn,
      beforeTranslate: () => console.debug('[Tranzy] start translate ->', toLang),
      afterTranslate: () => console.debug('[Tranzy] done')
    });

    state.tranzy = translator;
    state.initialized = true;

    try {
      translator.translatePage();
      translator.startObserver();
    } catch (e) {
      console.warn('Tranzy translatePage/startObserver failed:', e);
    }
  }

  function reconfigureTranzy(toLang) {
    try {
      if (!window.Tranzy || !Tranzy.Translator) return;
      state.tranzy = new Tranzy.Translator({
        toLang: toLang,
        fromLang: '',
        ignore: [...DEFAULT_IGNORE_SELECTORS, ...LOCAL_IGNORE_SELECTORS],
        translateFn: customTranslateFn
      });
      state.tranzy.translatePage();
      state.tranzy.startObserver();
    } catch (e) {
      console.warn('Tranzy reconfigure failed:', e);
    }
  }

  // Wire to SPADE minimal selector lifecycle
  document.addEventListener('languageSelector:initialized', () => {
    initTranzy();
  });

  document.addEventListener('languageSelector:languageChanged', (evt) => {
    const to = (evt && evt.detail && evt.detail.to) ? evt.detail.to : getCurrentLanguage();
    reconfigureTranzy(to);
  });

  // Fallback init in case minimal selector fires later
  if (document.readyState === 'complete' || document.readyState === 'interactive') {
    setTimeout(initTranzy, 0);
  } else {
    document.addEventListener('DOMContentLoaded', () => initTranzy());
  }

  // Expose a small API for debugging
  window.SPADE_TRANSLATION = {
    get state() { return state; },
    initTranzy,
    reconfigureTranzy
  };
})();