/**
 * Language Selector 极简版组件
 * 专注核心功能，无炫光特效，极简设计
 */

class LanguageSelectorMinimal {
  constructor(options = {}) {
    // 配置选项
    this.options = {
      containerId: 'languageSelectorMinimal',
      mode: 'dropdown', // 'dropdown' | 'toggle'
      autoClose: true,
      closeOnOutsideClick: true,
      supportedLanguages: ['en', 'zh-Hans', 'fr', 'pt', 'de', 'es', 'ja'],
      showNativeNames: true,
      showFlags: true,
      enableGeoLocation: true, // 启用地理位置检测
      forceReloadOnAutoSwitch: false,
      ...options
    };

    // 状态管理
    this.state = {
      currentLanguage: 'en',
      isOpen: false,
      isLoading: false,
      initialized: false,
      translations: {},
      geoLocationDetected: false
    };

    // DOM 元素引用
    this.elements = {
      container: null,
      trigger: null,
      dropdown: null,
      options: []
    };

    // 绑定方法上下文
    this.bindMethods();

    // 初始化
    this.init();
  }

  /**
   * 绑定方法上下文
   */
  bindMethods() {
    this.handleTriggerClick = this.handleTriggerClick.bind(this);
    this.handleKeyDown = this.handleKeyDown.bind(this);
    this.handleOutsideClick = this.handleOutsideClick.bind(this);
    this.handleOptionClick = this.handleOptionClick.bind(this);
    this.handleOptionKeyDown = this.handleOptionKeyDown.bind(this);
  }

  /**
   * 初始化组件
   */
  async init() {
    if (this.state.initialized) return;

    try {
      // 加载翻译数据
      await this.loadTranslations();
      
      // 获取语言偏好
      this.state.currentLanguage = this.getLanguagePreference();
      
      // 创建DOM结构
      this.createDOM();
      
      // 绑定事件
      this.bindEvents();
      
      // 翻译页面
      this.translatePage();
      
      // 地理位置检测（异步执行，不阻塞初始化）
      if (this.options.enableGeoLocation) {
        // 延迟执行地理位置检测，确保页面已完全加载
        setTimeout(async () => {
          await this.detectGeoLocation();
        }, 1000);
      }
      
      this.state.initialized = true;
      
      // 触发初始化完成事件
      this.emit('initialized');
      
    } catch (error) {
      console.error('Language selector initialization failed:', error);
    }
  }

  /**
   * 加载翻译数据
   */
  async loadTranslations() {
    try {
      const response = await fetch('data/translation.json');
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      this.state.translations = await response.json();
    } catch (error) {
      console.error('Failed to load translations:', error);
      // 使用默认翻译数据
      this.state.translations = {
        'en': { 'language_selector': 'Language' },
        'zh-Hans': { 'language_selector': '语言' }
      };
    }
  }

  /**
   * 创建DOM结构
   */
  createDOM() {
    // 创建主容器
    this.elements.container = document.createElement('div');
    this.elements.container.id = this.options.containerId;
    this.elements.container.className = `language-selector-minimal ${this.options.mode}-mode`;
    this.elements.container.setAttribute('role', 'region');
    this.elements.container.setAttribute('aria-label', '语言选择器');

    if (this.options.mode === 'dropdown') {
      this.createDropdownMode();
    } else {
      this.createToggleMode();
    }

    // 添加到页面
    document.body.appendChild(this.elements.container);
  }

  /**
   * 创建下拉菜单模式
   */
  createDropdownMode() {
    // 创建触发按钮
    this.elements.trigger = document.createElement('button');
    this.elements.trigger.className = 'ls-trigger-minimal';
    this.elements.trigger.setAttribute('type', 'button');
    this.elements.trigger.setAttribute('aria-haspopup', 'listbox');
    this.elements.trigger.setAttribute('aria-expanded', 'false');
    this.elements.trigger.setAttribute('aria-label', '选择语言');

    // 按钮内容
    const currentLang = this.getLanguageInfo(this.state.currentLanguage);
    this.elements.trigger.innerHTML = `
      <div class="ls-trigger-content-minimal">
        ${this.options.showFlags ? `<span class="ls-trigger-flag">${currentLang.flag}</span>` : ''}
        <span class="ls-current-lang-text">${currentLang.name}</span>
      </div>
      <svg class="ls-dropdown-arrow" viewBox="0 0 20 20" fill="currentColor">
        <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
      </svg>
    `;

    // 创建下拉菜单
    this.elements.dropdown = document.createElement('div');
    this.elements.dropdown.className = 'ls-dropdown-minimal';
    this.elements.dropdown.setAttribute('role', 'listbox');
    this.elements.dropdown.setAttribute('aria-label', '语言选项');

    // 创建滚动容器
    const scrollContainer = document.createElement('div');
    scrollContainer.className = 'ls-dropdown-scroll-minimal';

    // 防止滚动事件冒泡到页面
    scrollContainer.addEventListener('wheel', (e) => {
      e.stopPropagation();
      
      // 检查是否已经滚动到顶部或底部
      const { scrollTop, scrollHeight, clientHeight } = scrollContainer;
      const isAtTop = scrollTop === 0;
      const isAtBottom = scrollTop + clientHeight >= scrollHeight;
      
      // 如果在顶部向上滚动或在底部向下滚动，阻止默认行为
      if ((isAtTop && e.deltaY < 0) || (isAtBottom && e.deltaY > 0)) {
        e.preventDefault();
      }
    }, { passive: false });

    // 防止触摸滚动事件冒泡（移动端）
    scrollContainer.addEventListener('touchmove', (e) => {
      e.stopPropagation();
    }, { passive: true });

    // 创建语言选项
    this.options.supportedLanguages.forEach((langCode) => {
      const langInfo = this.getLanguageInfo(langCode);
      const option = document.createElement('div');
      option.className = `ls-option-minimal ${langCode === this.state.currentLanguage ? 'active' : ''}`;
      option.setAttribute('role', 'option');
      option.setAttribute('data-lang', langCode);
      option.setAttribute('tabindex', '0');
      option.setAttribute('aria-selected', langCode === this.state.currentLanguage ? 'true' : 'false');

      option.innerHTML = `
        ${this.options.showFlags ? `<span class="ls-option-flag-minimal">${langInfo.flag}</span>` : ''}
        <div class="ls-option-text-minimal">
          <span class="ls-option-name-minimal">${langInfo.name}</span>
          ${this.options.showNativeNames ? `<span class="ls-option-native-minimal">${langInfo.nativeName}</span>` : ''}
        </div>
        <svg class="ls-option-check" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
        </svg>
      `;

      // 绑定事件
      option.addEventListener('click', this.handleOptionClick);
      option.addEventListener('keydown', this.handleOptionKeyDown);

      scrollContainer.appendChild(option);
      this.elements.options.push(option);
    });

    this.elements.dropdown.appendChild(scrollContainer);
    this.elements.container.appendChild(this.elements.trigger);
    this.elements.container.appendChild(this.elements.dropdown);
  }

  /**
   * 创建切换按钮模式
   */
  createToggleMode() {
    const toggleContainer = document.createElement('div');
    toggleContainer.className = 'ls-toggle-mode-minimal';
    toggleContainer.setAttribute('role', 'radiogroup');
    toggleContainer.setAttribute('aria-label', '语言选择');

    // 创建语言选项（只显示前两个）
    this.options.supportedLanguages.slice(0, 2).forEach((langCode) => {
      const langInfo = this.getLanguageInfo(langCode);
      const isActive = langCode === this.state.currentLanguage;
      
      const option = document.createElement('div');
      option.className = `ls-toggle-option-minimal ${isActive ? 'active' : ''}`;
      option.setAttribute('role', 'radio');
      option.setAttribute('data-lang', langCode);
      option.setAttribute('tabindex', isActive ? '0' : '-1');
      option.setAttribute('aria-checked', isActive ? 'true' : 'false');
      option.textContent = langInfo.name;

      // 绑定事件
      option.addEventListener('click', () => this.selectLanguage(langCode));
      option.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          this.selectLanguage(langCode);
        }
      });

      toggleContainer.appendChild(option);
    });

    this.elements.container.appendChild(toggleContainer);
  }

  /**
   * 绑定事件监听器
   */
  bindEvents() {
    if (this.options.mode === 'dropdown') {
      // 触发按钮事件
      this.elements.trigger.addEventListener('click', this.handleTriggerClick);
      this.elements.trigger.addEventListener('keydown', this.handleKeyDown);

      // 外部点击关闭
      if (this.options.closeOnOutsideClick) {
        document.addEventListener('click', this.handleOutsideClick);
      }
    }
  }

  /**
   * 处理触发按钮点击
   */
  handleTriggerClick(e) {
    e.preventDefault();
    e.stopPropagation();
    this.toggleDropdown();
  }

  /**
   * 处理键盘事件
   */
  handleKeyDown(e) {
    switch (e.key) {
      case 'Escape':
        this.closeDropdown();
        break;
      case 'Enter':
      case ' ':
        e.preventDefault();
        this.toggleDropdown();
        break;
      case 'ArrowDown':
        e.preventDefault();
        if (!this.state.isOpen) {
          this.openDropdown();
        } else {
          this.focusNextOption();
        }
        break;
      case 'ArrowUp':
        e.preventDefault();
        if (this.state.isOpen) {
          this.focusPreviousOption();
        }
        break;
    }
  }

  /**
   * 处理外部点击
   */
  handleOutsideClick(e) {
    if (!this.elements.container.contains(e.target)) {
      this.closeDropdown();
    }
  }

  /**
   * 处理选项点击
   */
  handleOptionClick(e) {
    const langCode = e.currentTarget.getAttribute('data-lang');
    this.selectLanguage(langCode);
  }

  /**
   * 处理选项键盘事件
   */
  handleOptionKeyDown(e) {
    switch (e.key) {
      case 'Enter':
      case ' ':
        e.preventDefault();
        const langCode = e.currentTarget.getAttribute('data-lang');
        this.selectLanguage(langCode);
        break;
      case 'Escape':
        this.closeDropdown();
        this.elements.trigger.focus();
        break;
      case 'ArrowDown':
        e.preventDefault();
        this.focusNextOption();
        break;
      case 'ArrowUp':
        e.preventDefault();
        this.focusPreviousOption();
        break;
    }
  }

  /**
   * 切换下拉菜单
   */
  toggleDropdown() {
    if (this.state.isOpen) {
      this.closeDropdown();
    } else {
      this.openDropdown();
    }
  }

  /**
   * 打开下拉菜单
   */
  openDropdown() {
    this.state.isOpen = true;
    
    // 检查下拉菜单位置，决定是否向上展开
    this.adjustDropdownPosition();
    
    this.elements.dropdown.classList.add('show');
    this.elements.trigger.setAttribute('aria-expanded', 'true');
    
    // 聚焦到当前选中的选项
    const activeOption = this.elements.dropdown.querySelector('.ls-option-minimal.active');
    if (activeOption) {
      activeOption.focus();
    }
  }

  /**
   * 调整下拉菜单位置
   */
  adjustDropdownPosition() {
    const triggerRect = this.elements.trigger.getBoundingClientRect();
    const dropdownHeight = this.elements.dropdown.scrollHeight || 200; // 估算高度
    const viewportHeight = window.innerHeight;
    const spaceBelow = viewportHeight - triggerRect.bottom;
    const spaceAbove = triggerRect.top;

    // 如果下方空间不足且上方空间充足，则向上展开
    if (spaceBelow < dropdownHeight && spaceAbove > dropdownHeight) {
      this.elements.dropdown.classList.add('show-upward');
    } else {
      this.elements.dropdown.classList.remove('show-upward');
    }
  }

  /**
   * 关闭下拉菜单
   */
  closeDropdown() {
    this.state.isOpen = false;
    this.elements.dropdown.classList.remove('show');
    this.elements.trigger.setAttribute('aria-expanded', 'false');
  }

  /**
   * 聚焦下一个选项
   */
  focusNextOption() {
    const options = this.elements.dropdown.querySelectorAll('.ls-option-minimal');
    const currentIndex = Array.from(options).findIndex(option => option === document.activeElement);
    const nextIndex = (currentIndex + 1) % options.length;
    options[nextIndex].focus();
  }

  /**
   * 聚焦上一个选项
   */
  focusPreviousOption() {
    const options = this.elements.dropdown.querySelectorAll('.ls-option-minimal');
    const currentIndex = Array.from(options).findIndex(option => option === document.activeElement);
    const prevIndex = currentIndex <= 0 ? options.length - 1 : currentIndex - 1;
    options[prevIndex].focus();
  }

  /**
   * 选择语言
   */
  async selectLanguage(langCode, isAutoSwitch = false) {
    if (langCode === this.state.currentLanguage || this.state.isLoading) {
      this.closeDropdown();
      return;
    }

    this.state.isLoading = true;
    this.elements.trigger.classList.add('loading');

    try {
      // 更新状态
      const oldLanguage = this.state.currentLanguage;
      this.state.currentLanguage = langCode;
      
      // 保存偏好（无论是自动切换还是手动切换都保存）
      this.saveLanguagePreference(langCode);
      
      // 如果是手动切换，标记页面已访问，防止后续自动切换
      if (!isAutoSwitch) {
        this.markPageVisited();
      }
      
      // 更新UI
      this.updateTriggerContent();
      this.updateOptionsState();
      
      // 翻译页面
      this.translatePage();
      
      // 关闭下拉菜单
      this.closeDropdown();
      
      // 触发语言切换事件
      this.emit('languageChanged', {
        from: oldLanguage,
        to: langCode,
        isAutoSwitch: isAutoSwitch
      });
      
      // 自动切换时可选择刷新；手动切换不刷新
      if (isAutoSwitch && this.options.forceReloadOnAutoSwitch) {
        setTimeout(() => {
          location.reload();
        }, 100);
      }
      
    } catch (error) {
      console.error('Language switch failed:', error);
    } finally {
      this.state.isLoading = false;
      this.elements.trigger.classList.remove('loading');
    }
  }

  /**
   * 更新触发按钮内容
   */
  updateTriggerContent() {
    const currentLang = this.getLanguageInfo(this.state.currentLanguage);
    const content = this.elements.trigger.querySelector('.ls-trigger-content-minimal');
    
    content.innerHTML = `
      ${this.options.showFlags ? `<span class="ls-trigger-flag">${currentLang.flag}</span>` : ''}
      <span class="ls-current-lang-text">${currentLang.name}</span>
    `;
  }

  /**
   * 更新选项状态
   */
  updateOptionsState() {
    this.elements.options.forEach(option => {
      const langCode = option.getAttribute('data-lang');
      const isActive = langCode === this.state.currentLanguage;
      
      option.classList.toggle('active', isActive);
      option.setAttribute('aria-selected', isActive ? 'true' : 'false');
    });
  }

  /**
   * 获取语言信息
   */
  getLanguageInfo(langCode) {
    const languageMap = {
      'en': { name: 'English', nativeName: 'English', flag: '🇺🇸', code: 'en' },
      'zh-Hans': { name: '中文', nativeName: '简体中文', flag: '🇨🇳', code: 'zh' },
      'fr': { name: 'Français', nativeName: 'Français', flag: '🇫🇷', code: 'fr' },
      'pt': { name: 'Português', nativeName: 'Português', flag: '🇵🇹', code: 'pt' },
      'de': { name: 'Deutsch', nativeName: 'Deutsch', flag: '🇩🇪', code: 'de' },
      'es': { name: 'Español', nativeName: 'Español', flag: '🇪🇸', code: 'es' },
      'ja': { name: '日本語', nativeName: '日本語', flag: '🇯🇵', code: 'ja' }
    };
    
    return languageMap[langCode] || languageMap['en'];
  }

  /**
   * 获取语言偏好
   */
  getLanguagePreference() {
    // 检查是否有用户手动设置的语言偏好
    const userLanguage = localStorage.getItem('spade_language');
    if (userLanguage) {
      return userLanguage;
    }
    
    // 如果没有用户偏好，返回浏览器语言作为初始语言
    return this.getBrowserLanguage();
  }

  /**
   * 保存语言偏好
   */
  saveLanguagePreference(lang) {
    localStorage.setItem('spade_language', lang);
  }

  /**
   * 检查页面是否首次访问
   */
  isFirstVisit() {
    const currentPage = window.location.pathname;
    const visitKey = `spade_page_visited_${currentPage}`;
    return !sessionStorage.getItem(visitKey);
  }

  /**
   * 标记页面已访问
   */
  markPageVisited() {
    const currentPage = window.location.pathname;
    const visitKey = `spade_page_visited_${currentPage}`;
    sessionStorage.setItem(visitKey, 'true');
  }

  /**
   * 检测地理位置并设置语言
   */
  async detectGeoLocation() {
    if (this.state.geoLocationDetected) return;
    
    // 检查是否为首次访问当前页面
    const isFirstVisit = this.isFirstVisit();
    
    // 如果不是首次访问，不进行自动语言切换
    if (!isFirstVisit) {
      this.state.geoLocationDetected = true;
      return;
    }
    
    try {
      const response = await fetch('https://ipapi.co/json/');
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      const countryCode = data.country_code;
      const detectedLanguage = this.mapCountryToLanguage(countryCode);
      
      // 如果检测到的语言不在支持列表中，显示提示并设置默认语言
      if (!this.options.supportedLanguages.includes(detectedLanguage)) {
        this.showLanguageNotification();
        // 确保语言选择器状态更新为英文
        if (this.state.currentLanguage !== 'en') {
          this.state.currentLanguage = 'en';
          this.saveLanguagePreference('en');
          this.updateTriggerContent();
          this.updateOptionsState();
          this.translatePage();
        }
        // 标记页面已访问
        this.markPageVisited();
        this.state.geoLocationDetected = true;
        return;
      }
      
      // 如果检测到的语言与当前语言不同，更新语言（标记为自动切换）
      if (detectedLanguage !== this.state.currentLanguage) {
        await this.selectLanguage(detectedLanguage, true);
      }
      
      // 标记页面已访问
      this.markPageVisited();
      this.state.geoLocationDetected = true;
      
    } catch (error) {
      console.warn('Geo-location detection failed:', error);
      // 网络错误时也显示默认语言提示
      this.showLanguageNotification();
      // 标记页面已访问
      this.markPageVisited();
    }
  }

  /**
   * 将国家代码映射到语言代码
   */
  mapCountryToLanguage(countryCode) {
    const countryLanguageMap = {
      'CN': 'zh-Hans', // 中国
      'TW': 'zh-Hans', // 台湾
      'HK': 'zh-Hans', // 香港
      'SG': 'zh-Hans', // 新加坡
      'ES': 'es',      // 西班牙
      'MX': 'es',      // 墨西哥
      'AR': 'es',      // 阿根廷
      'CO': 'es',      // 哥伦比亚
      'PE': 'es',      // 秘鲁
      'DE': 'de',      // 德国
      'AT': 'de',      // 奥地利
      'CH': 'de',      // 瑞士
      'JP': 'ja',      // 日本
      'US': 'en',      // 美国
      'GB': 'en',      // 英国
      'CA': 'en',      // 加拿大
      'AU': 'en',      // 澳大利亚
      'NZ': 'en'       // 新西兰
    };
    
    return countryLanguageMap[countryCode] || 'en';
  }

  /**
   * 显示语言设置通知
   */
  showLanguageNotification() {
    // 检查是否已经显示过通知（避免重复显示）
    if (sessionStorage.getItem('language_notification_shown')) {
      return;
    }
    
    // 标记已显示通知
    sessionStorage.setItem('language_notification_shown', 'true');
    
    // 移除已存在的通知
    const existingNotification = document.getElementById('language-notification');
    if (existingNotification) {
      existingNotification.remove();
    }
    
    // 创建通知元素
    const notification = document.createElement('div');
    notification.id = 'language-notification';
    notification.className = 'language-notification';
    notification.innerHTML = `
      <div class="notification-content">
        <span class="notification-icon">🌐</span>
        <span class="notification-text">Language has been set to English</span>
      </div>
    `;
    
    // 添加样式
    const style = document.createElement('style');
    style.textContent = `
      .language-notification {
        position: fixed;
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%);
        background: rgba(0, 0, 0, 0.8);
        color: white;
        padding: 12px 20px;
        border-radius: 25px;
        font-size: 14px;
        font-weight: 500;
        z-index: 10000;
        opacity: 0.45;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        animation: notificationSlideIn 0.5s ease-out;
        pointer-events: none;
        user-select: none;
      }
      
      .notification-content {
        display: flex;
        align-items: center;
        gap: 8px;
      }
      
      .notification-icon {
        font-size: 16px;
      }
      
      .notification-text {
        white-space: nowrap;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      }
      
      @keyframes notificationSlideIn {
        from {
          opacity: 0;
          transform: translateX(-50%) translateY(20px);
        }
        to {
          opacity: 0.45;
          transform: translateX(-50%) translateY(0);
        }
      }
      
      @keyframes notificationSlideOut {
        from {
          opacity: 0.45;
          transform: translateX(-50%) translateY(0);
        }
        to {
          opacity: 0;
          transform: translateX(-50%) translateY(20px);
        }
      }
      
      @media (max-width: 768px) {
        .language-notification {
          bottom: 15px;
          padding: 10px 16px;
          font-size: 13px;
          max-width: 90vw;
        }
        
        .notification-text {
          font-size: 12px;
        }
      }
    `;
    
    // 检查样式是否已存在，避免重复添加
    if (!document.getElementById('language-notification-style')) {
      style.id = 'language-notification-style';
      document.head.appendChild(style);
    }
    
    document.body.appendChild(notification);
    
    // 5秒后自动移除通知
    setTimeout(() => {
      if (notification.parentNode) {
        notification.style.animation = 'notificationSlideOut 0.5s ease-in';
        notification.addEventListener('animationend', () => {
          if (notification.parentNode) {
            notification.remove();
          }
        });
      }
    }, 5000);
  }

  /**
   * 获取浏览器语言
   */
  getBrowserLanguage() {
    const browserLang = navigator.language || navigator.userLanguage;
    
    if (browserLang.startsWith('zh')) {
      return 'zh-Hans';
    } else if (browserLang.startsWith('fr')) {
      return 'fr';
    } else if (browserLang.startsWith('pt')) {
      return 'pt';
    } else if (browserLang.startsWith('es')) {
      return 'es';
    } else if (browserLang.startsWith('de')) {
      return 'de';
    } else if (browserLang.startsWith('ja')) {
      return 'ja';
    }
    
    return 'en';
  }

  /**
   * 获取翻译
   */
  getTranslation(key, lang) {
    lang = lang || this.state.currentLanguage;
    const t = this.state.translations || {};
    return (t[lang] && t[lang][key]) || (t['en'] && t['en'][key]) || key;
  }

  /**
   * 翻译页面
   */
  translatePage() {
    const elements = document.querySelectorAll('[data-translate]');
    elements.forEach(element => {
      const key = element.dataset.translate;
      const translation = this.getTranslation(key);
      if (translation && translation !== key) {
        element.innerHTML = translation;
      }
    });

    // 翻译属性
    const placeholderElements = document.querySelectorAll('[data-translate-placeholder]');
    placeholderElements.forEach(element => {
      const key = element.dataset.translatePlaceholder;
      const translation = this.getTranslation(key);
      if (translation) {
        element.placeholder = translation;
      }
    });
  }

  /**
   * 触发事件
   */
  emit(eventName, data = {}) {
    const event = new CustomEvent(`languageSelector:${eventName}`, {
      detail: data,
      bubbles: true
    });
    document.dispatchEvent(event);
  }

  /**
   * 清除通知标记（允许重新显示通知）
   */
  clearNotificationMark() {
    sessionStorage.removeItem('language_notification_shown');
  }

  /**
   * 清除页面访问标记（允许重新进行首次访问检测）
   */
  clearPageVisitMark() {
    const currentPage = window.location.pathname;
    const visitKey = `spade_page_visited_${currentPage}`;
    sessionStorage.removeItem(visitKey);
  }

  /**
   * 清除所有页面访问标记
   */
  clearAllPageVisitMarks() {
    const keys = Object.keys(sessionStorage);
    keys.forEach(key => {
      if (key.startsWith('spade_page_visited_')) {
        sessionStorage.removeItem(key);
      }
    });
  }

  /**
   * 销毁组件
   */
  destroy() {
    if (this.elements.container && this.elements.container.parentNode) {
      this.elements.container.parentNode.removeChild(this.elements.container);
    }
    
    // 移除事件监听器
    document.removeEventListener('click', this.handleOutsideClick);
    
    this.state.initialized = false;
  }
}

// 全局实例
window.SPADE_LANGUAGE_SELECTOR_MINIMAL = {
  instance: null,
  
  init(options = {}) {
    if (this.instance) {
      this.instance.destroy();
    }
    this.instance = new LanguageSelectorMinimal(options);
    return this.instance;
  },
  
  getInstance() {
    return this.instance;
  },
  
  switchLanguage(langCode) {
    if (this.instance) {
      this.instance.selectLanguage(langCode);
    }
  },
  
  clearNotificationMark() {
    if (this.instance) {
      this.instance.clearNotificationMark();
    }
  },

  clearPageVisitMark() {
    if (this.instance) {
      this.instance.clearPageVisitMark();
    }
  },

  clearAllPageVisitMarks() {
    if (this.instance) {
      this.instance.clearAllPageVisitMarks();
    }
  },
  
  destroy() {
    if (this.instance) {
      this.instance.destroy();
      this.instance = null;
    }
  }
};

// 页面加载完成后自动初始化
document.addEventListener('DOMContentLoaded', () => {
  window.SPADE_LANGUAGE_SELECTOR_MINIMAL.init();
});