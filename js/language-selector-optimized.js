/**
 * Language Selector 优化版组件
 * 简约现代风格，单击展开交互
 */

class LanguageSelectorOptimized {
  constructor(options = {}) {
    // 配置选项
    this.options = {
      containerId: 'languageSelectorOptimized',
      mode: 'dropdown', // 'dropdown' | 'toggle'
      autoClose: true,
      closeOnOutsideClick: true,
      animationDuration: 250,
      supportedLanguages: ['en', 'zh-Hans', 'es', 'de', 'ja'],
      showNativeNames: true,
      showFlags: true,
      ...options
    };

    // 状态管理
    this.state = {
      currentLanguage: 'en',
      isOpen: false,
      isLoading: false,
      initialized: false,
      translations: {}
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
    this.elements.container.className = `language-selector-optimized ${this.options.mode}-mode`;
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
    this.elements.trigger.className = 'ls-trigger-optimized';
    this.elements.trigger.setAttribute('type', 'button');
    this.elements.trigger.setAttribute('aria-haspopup', 'listbox');
    this.elements.trigger.setAttribute('aria-expanded', 'false');
    this.elements.trigger.setAttribute('aria-label', '选择语言');

    // 按钮内容
    const currentLang = this.getLanguageInfo(this.state.currentLanguage);
    this.elements.trigger.innerHTML = `
      <div class="ls-trigger-content-optimized">
        <span class="ls-trigger-icon">${currentLang.flag}</span>
        <span class="ls-current-lang-text">${currentLang.name}</span>
        <svg class="ls-dropdown-arrow" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
        </svg>
      </div>
    `;

    // 创建下拉菜单
    this.elements.dropdown = document.createElement('div');
    this.elements.dropdown.className = 'ls-dropdown-optimized';
    this.elements.dropdown.setAttribute('role', 'listbox');
    this.elements.dropdown.setAttribute('aria-label', '语言选项');

    // 创建滚动容器
    const scrollContainer = document.createElement('div');
    scrollContainer.className = 'ls-dropdown-scroll-optimized';

    // 创建语言选项
    this.options.supportedLanguages.forEach((langCode, index) => {
      const langInfo = this.getLanguageInfo(langCode);
      const option = document.createElement('div');
      option.className = `ls-option-optimized ${langCode === this.state.currentLanguage ? 'active' : ''}`;
      option.setAttribute('role', 'option');
      option.setAttribute('data-lang', langCode);
      option.setAttribute('tabindex', '0');
      option.setAttribute('aria-selected', langCode === this.state.currentLanguage ? 'true' : 'false');

      option.innerHTML = `
        ${this.options.showFlags ? `<span class="ls-option-flag-optimized" aria-hidden="true">${langInfo.flag}</span>` : ''}
        <div class="ls-option-text-optimized">
          <span class="ls-option-name-optimized">${langInfo.name}</span>
          ${this.options.showNativeNames ? `<span class="ls-option-native-optimized">${langInfo.nativeName}</span>` : ''}
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

      // 添加分隔线（除了最后一个）
      if (index < this.options.supportedLanguages.length - 1) {
        const divider = document.createElement('div');
        divider.className = 'ls-option-divider';
        scrollContainer.appendChild(divider);
      }
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
    toggleContainer.className = 'ls-toggle-mode-optimized';
    toggleContainer.setAttribute('role', 'radiogroup');
    toggleContainer.setAttribute('aria-label', '语言选择');

    // 创建滑动指示器
    const indicator = document.createElement('div');
    indicator.className = 'ls-toggle-indicator-optimized';
    toggleContainer.appendChild(indicator);

    // 创建语言选项（只显示前两个）
    this.options.supportedLanguages.slice(0, 2).forEach((langCode) => {
      const langInfo = this.getLanguageInfo(langCode);
      const isActive = langCode === this.state.currentLanguage;
      
      const option = document.createElement('div');
      option.className = `ls-toggle-option-optimized ${isActive ? 'active' : ''}`;
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
    
    // 更新指示器位置
    setTimeout(() => this.updateToggleIndicator(), 0);
  }

  /**
   * 绑定事件监听器
   */
  bindEvents() {
    if (this.options.mode === 'dropdown') {
      // 触发按钮事件 - 单击展开
      this.elements.trigger.addEventListener('click', this.handleTriggerClick);
      this.elements.trigger.addEventListener('keydown', this.handleKeyDown);

      // 外部点击关闭
      if (this.options.closeOnOutsideClick) {
        document.addEventListener('click', this.handleOutsideClick);
      }
    }
  }

  /**
   * 处理触发按钮点击 - 单击展开逻辑
   */
  handleTriggerClick(e) {
    e.preventDefault();
    e.stopPropagation();
    
    // 添加点击波纹效果
    this.createRippleEffect(e);
    
    // 切换下拉菜单
    this.toggleDropdown();
  }

  /**
   * 创建点击波纹效果
   */
  createRippleEffect(e) {
    const button = e.currentTarget;
    const rect = button.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = e.clientX - rect.left - size / 2;
    const y = e.clientY - rect.top - size / 2;
    
    const ripple = document.createElement('span');
    ripple.className = 'ls-ripple';
    ripple.style.width = ripple.style.height = size + 'px';
    ripple.style.left = x + 'px';
    ripple.style.top = y + 'px';
    
    button.appendChild(ripple);
    
    // 移除波纹元素
    setTimeout(() => {
      if (button.contains(ripple)) {
        button.removeChild(ripple);
      }
    }, 600);
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
    e.preventDefault();
    e.stopPropagation();
    
    const langCode = e.currentTarget.getAttribute('data-lang');
    this.selectLanguage(langCode);
  }

  /**
   * 处理选项键盘事件
   */
  handleOptionKeyDown(e) {
    const option = e.currentTarget;
    const langCode = option.getAttribute('data-lang');
    
    switch (e.key) {
      case 'Enter':
      case ' ':
        e.preventDefault();
        this.selectLanguage(langCode);
        break;
      case 'ArrowDown':
        e.preventDefault();
        this.focusNextOption();
        break;
      case 'ArrowUp':
        e.preventDefault();
        this.focusPreviousOption();
        break;
      case 'Escape':
        e.preventDefault();
        this.closeDropdown();
        this.elements.trigger.focus();
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
    if (this.state.isOpen) return;
    
    this.state.isOpen = true;
    this.elements.container.classList.add('active');
    this.elements.dropdown.classList.add('show');
    this.elements.trigger.setAttribute('aria-expanded', 'true');
    
    // 聚焦到当前选中的选项
    const activeOption = this.elements.dropdown.querySelector('.ls-option-optimized.active');
    if (activeOption) {
      setTimeout(() => activeOption.focus(), 100);
    }
    
    this.emit('opened');
  }

  /**
   * 关闭下拉菜单
   */
  closeDropdown() {
    if (!this.state.isOpen) return;
    
    this.state.isOpen = false;
    this.elements.container.classList.remove('active');
    this.elements.dropdown.classList.remove('show');
    this.elements.trigger.setAttribute('aria-expanded', 'false');
    
    this.emit('closed');
  }

  /**
   * 选择语言
   */
  async selectLanguage(langCode) {
    if (langCode === this.state.currentLanguage || this.state.isLoading) return;
    
    this.state.isLoading = true;
    this.elements.container.classList.add('loading');
    
    try {
      // 模拟加载延迟
      await new Promise(resolve => setTimeout(resolve, 200));
      
      // 更新状态
      const oldLanguage = this.state.currentLanguage;
      this.state.currentLanguage = langCode;
      
      // 保存偏好
      this.saveLanguagePreference(langCode);
      
      // 更新UI
      this.updateCurrentLanguageDisplay();
      this.updateActiveOption();
      
      // 翻译页面
      this.translatePage();
      
      // 关闭下拉菜单
      this.closeDropdown();
      
      // 触发事件
      this.emit('languageChanged', { from: oldLanguage, to: langCode });
      
    } catch (error) {
      console.error('Language change failed:', error);
    } finally {
      this.state.isLoading = false;
      this.elements.container.classList.remove('loading');
    }
  }

  /**
   * 更新当前语言显示
   */
  updateCurrentLanguageDisplay() {
    if (this.options.mode === 'dropdown') {
      const currentLang = this.getLanguageInfo(this.state.currentLanguage);
      const iconSpan = this.elements.trigger.querySelector('.ls-trigger-icon');
      const textSpan = this.elements.trigger.querySelector('.ls-current-lang-text');
      
      if (iconSpan) iconSpan.textContent = currentLang.flag;
      if (textSpan) textSpan.textContent = currentLang.name;
    } else {
      this.updateToggleIndicator();
    }
  }

  /**
   * 更新活动选项
   */
  updateActiveOption() {
    this.elements.options.forEach(option => {
      const langCode = option.getAttribute('data-lang');
      const isActive = langCode === this.state.currentLanguage;
      
      option.classList.toggle('active', isActive);
      option.setAttribute('aria-selected', isActive ? 'true' : 'false');
    });
  }

  /**
   * 更新切换指示器
   */
  updateToggleIndicator() {
    if (this.options.mode !== 'toggle') return;
    
    const indicator = this.elements.container.querySelector('.ls-toggle-indicator-optimized');
    const activeOption = this.elements.container.querySelector('.ls-toggle-option-optimized.active');
    
    if (indicator && activeOption) {
      const rect = activeOption.getBoundingClientRect();
      const containerRect = this.elements.container.getBoundingClientRect();
      
      indicator.style.left = (rect.left - containerRect.left + 2) + 'px';
      indicator.style.width = (rect.width - 4) + 'px';
    }
  }

  /**
   * 获取语言信息
   */
  getLanguageInfo(langCode) {
    const languageMap = {
      'en': { code: 'en', name: 'English', nativeName: 'English', flag: '🇺🇸' },
      'zh-Hans': { code: 'zh', name: '中文', nativeName: '简体中文', flag: '🇨🇳' },
      'es': { code: 'es', name: 'Español', nativeName: 'Español', flag: '🇪🇸' },
      'de': { code: 'de', name: 'Deutsch', nativeName: 'Deutsch', flag: '🇩🇪' },
      'ja': { code: 'ja', name: '日本語', nativeName: '日本語', flag: '🇯🇵' }
    };
    
    return languageMap[langCode] || languageMap['en'];
  }

  /**
   * 语言偏好管理
   */
  getLanguagePreference() {
    return localStorage.getItem('spade_language') || this.getBrowserLanguage();
  }

  saveLanguagePreference(langCode) {
    localStorage.setItem('spade_language', langCode);
  }

  getBrowserLanguage() {
    const browserLang = navigator.language || navigator.userLanguage;
    
    if (browserLang.startsWith('zh')) {
      return 'zh-Hans';
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
   * 翻译功能
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

  getTranslation(key, lang = this.state.currentLanguage) {
    return this.state.translations[lang]?.[key] || key;
  }

  /**
   * 键盘导航支持
   */
  focusNextOption() {
    const currentFocus = document.activeElement;
    const currentIndex = this.elements.options.indexOf(currentFocus);
    const nextIndex = (currentIndex + 1) % this.elements.options.length;
    this.elements.options[nextIndex].focus();
  }

  focusPreviousOption() {
    const currentFocus = document.activeElement;
    const currentIndex = this.elements.options.indexOf(currentFocus);
    const prevIndex = currentIndex <= 0 ? this.elements.options.length - 1 : currentIndex - 1;
    this.elements.options[prevIndex].focus();
  }

  /**
   * 事件发射器
   */
  emit(eventName, data = null) {
    const event = new CustomEvent(`languageSelector:${eventName}`, {
      detail: data,
      bubbles: true
    });
    this.elements.container.dispatchEvent(event);
  }

  /**
   * 销毁组件
   */
  destroy() {
    // 移除事件监听器
    if (this.options.closeOnOutsideClick) {
      document.removeEventListener('click', this.handleOutsideClick);
    }

    // 移除DOM元素
    if (this.elements.container && this.elements.container.parentNode) {
      this.elements.container.parentNode.removeChild(this.elements.container);
    }

    // 清理状态
    this.state.initialized = false;
    this.elements = {};
  }
}

// 全局实例管理
window.SPADE_LANGUAGE_SELECTOR_OPTIMIZED = {
  instance: null,
  
  /**
   * 初始化语言选择器
   */
  init(options = {}) {
    if (this.instance) {
      this.instance.destroy();
    }
    
    this.instance = new LanguageSelectorOptimized(options);
    return this.instance;
  },
  
  /**
   * 获取当前实例
   */
  getInstance() {
    return this.instance;
  },
  
  /**
   * 销毁实例
   */
  destroy() {
    if (this.instance) {
      this.instance.destroy();
      this.instance = null;
    }
  },

  /**
   * 兼容API方法
   */
  switchLanguage(lang) {
    if (this.instance) {
      this.instance.selectLanguage(lang);
    }
  },

  getCurrentLanguage() {
    return this.instance ? this.instance.state.currentLanguage : 'en';
  },

  getTranslation(key, lang) {
    return this.instance ? this.instance.getTranslation(key, lang) : key;
  }
};

// 页面加载完成后自动初始化
document.addEventListener('DOMContentLoaded', () => {
  // 隐藏旧版本的语言选择器
  const oldSelectors = [
    document.getElementById('languageSelector'),
    document.getElementById('languageSelectorEnhanced')
  ];
  
  oldSelectors.forEach(selector => {
    if (selector) {
      selector.style.display = 'none';
    }
  });
  
  // 初始化优化版本
  window.SPADE_LANGUAGE_SELECTOR_OPTIMIZED.init({
    mode: 'dropdown',
    autoClose: true,
    closeOnOutsideClick: true,
    showNativeNames: true,
    showFlags: true
  });
  
  console.log('Language Selector Optimized 已初始化');
});