(function(){
  class SearchIndexLoader {
    constructor(opts){
      this.opts = Object.assign({
        extendedPaths: [
          './data/index/peptide_extended_index.json',
          'data/index/peptide_extended_index.json',
          '/data/index/peptide_extended_index.json'
        ],
        basePaths: [
          './data/index/peptide_index.json',
          'data/index/peptide_index.json',
          '/data/index/peptide_index.json'
        ],
        pagesMetaPath: './data/index/pages/metadata.json',
        pagesDir: './data/index/pages/',
        pagesPreloadCount: 10,
        cacheKey: 'SPADE_SEARCH_INDEX_CACHE',
        cacheTTLms: 24*60*60*1000
      }, opts || {});
      this._index = null;
      this._loading = null;
    }

    async load(){
      if(this._index) return this._index;
      if(this._loading) return this._loading;
      this._loading = this._loadInternal();
      this._index = await this._loading;
      return this._index;
    }

    async _loadInternal(){
      // 1) Try cache
      const cached = this._getCache();
      if (cached) return cached;

      // 2) Try extended index
      const ext = await this._tryPaths(this.opts.extendedPaths);
      if (ext) { this._setCache(ext); return ext; }

      // 3) Try base index
      const base = await this._tryPaths(this.opts.basePaths);
      if (base) { this._setCache(base); return base; }

      // 4) Fallback: paginated pages (preload limited pages)
      try {
        const meta = await this._fetchJSON(this.opts.pagesMetaPath);
        if (meta && meta.total_pages) {
          const preload = await this._loadPages(meta, this.opts.pagesPreloadCount);
          if (preload && Array.isArray(preload) && preload.length) {
            // Do not cache partial pages aggressively
            return preload;
          }
        }
      } catch (err) {
        console.warn('Paged index fallback failed:', err);
      }

      throw new Error('Unable to load peptide index from any source');
    }

    async _tryPaths(paths){
      for (const p of paths){
        try {
          const data = await this._fetchJSON(p);
          if (this._validateArray(data)) return data;
        } catch (err) {
          console.warn('Index path failed:', p, err?.message || err);
        }
      }
      return null;
    }

    async _fetchJSON(url){
      const resp = await fetch(url, { cache: 'no-cache' });
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const ct = resp.headers.get('content-type') || '';
      if (!ct.includes('application/json')) {
        // Some static servers may not set JSON mime correctly, still try
        // but log a warning for debugging.
        console.warn('Non-JSON Content-Type for', url, ct);
      }
      const json = await resp.json();
      return json;
    }

    async _loadPages(meta, count){
      const items = [];
      const limit = Math.min(count, meta.total_pages);
      for (let i = 1; i <= limit; i++){
        const file = meta.page_template.replace('{}', i);
        try {
          const page = await this._fetchJSON(this.opts.pagesDir + file);
          if (Array.isArray(page)) items.push(...page);
        } catch (err) {
          console.warn('Load page failed:', file, err?.message || err);
        }
      }
      return items;
    }

    _validateArray(arr){
      if (!Array.isArray(arr)) return false;
      // Ensure minimal fields for search
      const sample = arr[0];
      if (!sample) return true; // empty ok
      const needed = ['id'];
      return needed.every(k => k in sample);
    }

    _getCache(){
      try {
        const raw = localStorage.getItem(this.opts.cacheKey);
        if (!raw) return null;
        const obj = JSON.parse(raw);
        if (!obj || !obj.data || !obj.ts) return null;
        if (Date.now() - obj.ts > this.opts.cacheTTLms) return null;
        return obj.data;
      } catch (e){
        return null;
      }
    }

    _setCache(data){
      try {
        const obj = { ts: Date.now(), data };
        localStorage.setItem(this.opts.cacheKey, JSON.stringify(obj));
      } catch (e){
        // ignore quota
      }
    }

    // Utility for UI messages via minimal language selector
    t(key, fallback){
      const inst = window.SPADE_LANGUAGE_SELECTOR_MINIMAL?.getInstance?.();
      if (inst && typeof inst.getTranslation === 'function'){
        return inst.getTranslation(key) || fallback || key;
      }
      return fallback || key;
    }
  }

  window.SPADE_SEARCH_INDEX_LOADER = new SearchIndexLoader();
})();