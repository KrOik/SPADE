/**
 * Language Selector 增强版组件
 * 基于原有设计优化，保持完全兼容性
 */

class LanguageSelectorEnhanced {
  constructor(options = {}) {
    // 配置选项 - 与原有组件保持一致
    this.options = {
      containerId: 'languageSelectorEnhanced',
      mode: 'dropdown', // 'dropdown' | 'toggle'
      draggable: true,
      autoClose: true,
      supportedLanguages: ['en', 'zh-Hans', 'es', 'de', 'ja'],
      edgeThreshold: 60,
      dragThreshold: 5,
      ...options
    };

    // 状态管理 - 与原有组件保持一致
    this.state = {
      currentLanguage: 'en',
      isOpen: false,
      isDragging: false,
      isLoading: false,
      initialized: false,
      translations: {},
      position: { x: 30, y: 85 }
    };

    // DOM 元素引用
    this.elements = {
      container: null,
      trigger: null,
      dropdown: null,
      options: []
    };

    // 拖拽相关 - 与原有组件保持一致
    this.drag = {
      startX: 0,
      startY: 0,
      initialX: 0,
      initialY: 0,
      hasMoved: false,
      dragStartTime: 0
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
    this.handleMouseDown = this.handleMouseDown.bind(this);
    this.handleMouseMove = this.handleMouseMove.bind(this);
    this.handleMouseUp = this.handleMouseUp.bind(this);
    this.handleTouchStart = this.handleTouchStart.bind(this);
    this.handleTouchMove = this.handleTouchMove.bind(this);
    this.handleTouchEnd = this.handleTouchEnd.bind(this);
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
      
      // 恢复位置
      this.restorePosition();
      
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
   * 加载翻译数据 - 与原有组件保持一致
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
    this.elements.container.className = `language-selector-enhanced ${this.options.mode}-mode`;
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
    this.elements.trigger.className = 'ls-trigger-enhanced';
    this.elements.trigger.setAttribute('type', 'button');
    this.elements.trigger.setAttribute('aria-haspopup', 'listbox');
    this.elements.trigger.setAttribute('aria-expanded', 'false');
    this.elements.trigger.setAttribute('aria-label', '选择语言');

    // 按钮内容 - 显示当前语言代码
    const currentLang = this.getLanguageInfo(this.state.currentLanguage);
    this.elements.trigger.innerHTML = `
      <span class="ls-trigger-content">${currentLang.code.toUpperCase()}</span>
    `;

    // 创建下拉菜单
    this.elements.dropdown = document.createElement('div');
    this.elements.dropdown.className = 'ls-dropdown-enhanced';
    this.elements.dropdown.setAttribute('role', 'listbox');
    this.elements.dropdown.setAttribute('aria-label', '语言选项');

    // 创建滚动容器
    const scrollContainer = document.createElement('div');
    scrollContainer.className = 'ls-dropdown-scroll-enhanced';

    // 创建语言选项
    this.options.supportedLanguages.forEach((langCode) => {
      const langInfo = this.getLanguageInfo(langCode);
      const option = document.createElement('div');
      option.className = `ls-option-enhanced ${langCode === this.state.currentLanguage ? 'active' : ''}`;
      option.setAttribute('role', 'option');
      option.setAttribute('data-lang', langCode);
      option.setAttribute('tabindex', '0');
      option.setAttribute('aria-selected', langCode === this.state.currentLanguage ? 'true' : 'false');

      option.innerHTML = `
        <span class="ls-option-flag" aria-hidden="true">${langInfo.flag}</span>
        <div class="ls-option-text">
          <span class="ls-option-name">${langInfo.name}</span>
          <span class="ls-option-native">${langInfo.nativeName}</span>
        </div>
      `;

      // 绑定点击事件
      option.addEventListener('click', (e) => {
        e.preventDefault();
        this.selectLanguage(langCode);
      });

      // 绑定键盘事件
      option.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          this.selectLanguage(langCode);
        }
      });

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
    toggleContainer.className = 'ls-toggle-mode-enhanced';
    toggleContainer.setAttribute('role', 'radiogroup');
    toggleContainer.setAttribute('aria-label', '语言选择');

    // 创建滑动指示器
    const indicator = document.createElement('div');
    indicator.className = 'ls-toggle-indicator-enhanced';
    toggleContainer.appendChild(indicator);

    // 创建语言选项（只显示前两个）
    this.options.supportedLanguages.slice(0, 2).forEach((langCode, index) => {
      const langInfo = this.getLanguageInfo(langCode);
      const isActive = langCode === this.state.currentLanguage;
      
      const option = document.createElement('div');
      option.className = `ls-toggle-option-enhanced ${isActive ? 'active' : ''}`;
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
      // 触发按钮事件
      this.elements.trigger.addEventListener('click', this.handleTriggerClick);
      this.elements.trigger.addEventListener('keydown', this.handleKeyDown);

      // 拖拽事件
      if (this.options.draggable) {
        this.elements.trigger.addEventListener('mousedown', this.handleMouseDown);
        this.elements.trigger.addEventListener('touchstart', this.handleTouchStart, { passive: false });
      }

      // 外部点击关闭
      if (this.options.autoClose) {
        document.addEventListener('click', this.handleOutsideClick);
      }
    }

    // 全局事件
    document.addEventListener('mousemove', this.handleMouseMove);
    document.addEventListener('mouseup', this.handleMouseUp);
    document.addEventListener('touchmove', this.handleTouchMove, { passive: false });
    document.addEventListener('touchend', this.handleTouchEnd);
  }

  /**
   * 处理触发按钮点击 - 与原有组件保持一致
   */
  handleTriggerClick(e) {
    if (this.drag.hasMoved || this.state.isDragging) {
      e.preventDefault();
      return;
    }
    
    // 检查是否是快速点击（不是拖拽）
    const clickTime = Date.now();
    const isQuickClick = !this.drag.hasMoved && !this.state.isDragging && 
                       (clickTime - (this.drag.dragStartTime || 0)) > 200;
    
    if (isQuickClick) {
      this.toggleDropdown();
    }
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
   * 拖拽相关方法 - 与原有组件完全一致
   */
  handleMouseDown(e) {
    e.preventDefault();
    this.startDragging(e.clientX, e.clientY);
  }

  handleTouchStart(e) {
    if (e.touches.length === 1) {
      const touch = e.touches[0];
      this.startDragging(touch.clientX, touch.clientY);
    }
  }

  startDragging(x, y) {
    this.state.isDragging = false;
    this.drag.hasMoved = false;
    this.drag.startX = x;
    this.drag.startY = y;
    
    const rect = this.elements.container.getBoundingClientRect();
    this.drag.initialX = rect.left;
    this.drag.initialY = rect.top;
    
    this.drag.dragStartTime = Date.now();
  }

  handleMouseMove(e) {
    if (!this.drag.startX || !this.drag.startY) return;
    
    const deltaX = Math.abs(e.clientX - this.drag.startX);
    const deltaY = Math.abs(e.clientY - this.drag.startY);
    
    if (!this.state.isDragging && (deltaX > this.options.dragThreshold || deltaY > this.options.dragThreshold)) {
      this.state.isDragging = true;
      this.drag.hasMoved = true;
      this.elements.container.classList.add('dragging');
      this.closeDropdown();
    }
    
    if (this.state.isDragging) {
      this.updatePosition(e.clientX, e.clientY);
    }
  }

  handleTouchMove(e) {
    if (!this.drag.startX || !this.drag.startY || e.touches.length !== 1) return;
    
    e.preventDefault();
    const touch = e.touches[0];
    const deltaX = Math.abs(touch.clientX - this.drag.startX);
    const deltaY = Math.abs(touch.clientY - this.drag.startY);
    
    if (!this.state.isDragging && (deltaX > this.options.dragThreshold || deltaY > this.options.dragThreshold)) {
      this.state.isDragging = true;
      this.drag.hasMoved = true;
      this.elements.container.classList.add('dragging');
      this.closeDropdown();
    }
    
    if (this.state.isDragging) {
      this.updatePosition(touch.clientX, touch.clientY);
    }
  }

  updatePosition(x, y) {
    const deltaX = x - this.drag.startX;
    const deltaY = y - this.drag.startY;
    
    let newX = this.drag.initialX + deltaX;
    let newY = this.drag.initialY + deltaY;
    
    // 边界限制
    const maxX = window.innerWidth - this.elements.container.offsetWidth;
    const maxY = window.innerHeight - this.elements.container.offsetHeight;
    
    newX = Math.max(0, Math.min(newX, maxX));
    newY = Math.max(0, Math.min(newY, maxY));
    
    this.elements.container.style.left = newX + 'px';
    this.elements.container.style.top = newY + 'px';
    this.elements.container.style.right = 'auto';
    
    // 边缘检测
    this.checkEdgeCollapse(newX, newY);
    
    // 更新状态
    this.state.position = { x: newX, y: newY };
  }

  /**
   * 检查边缘收缩 - 与原有组件保持一致
   */
  checkEdgeCollapse(x, y) {
    const isNearEdge = x <= this.options.edgeThreshold || 
                      x >= window.innerWidth - this.elements.container.offsetWidth - this.options.edgeThreshold ||
                      y <= this.options.edgeThreshold || 
                      y >= window.innerHeight - this.elements.container.offsetHeight - this.options.edgeThreshold;
    
    if (isNearEdge) {
      this.elements.container.classList.add('edge-collapsed');
    } else {
      this.elements.container.classList.remove('edge-collapsed');
    }
  }

  handleMouseUp() {
    this.stopDragging();
  }

  handleTouchEnd() {
    this.stopDragging();
  }

  stopDragging() {
    if (this.state.isDragging) {
      this.state.isDragging = false;
      this.elements.container.classList.remove('dragging');
      this.savePosition();
    }
    
    this.drag.startX = 0;
    this.drag.startY = 0;
    
    // 延迟重置移动标记 - 与原有组件保持一致
    setTimeout(() => {
      this.drag.hasMoved = false;
      this.drag.dragStartTime = 0;
    }, 150);
  }

  /**
   * 下拉菜单控制方法
   */
  toggleDropdown() {
    if (this.state.isOpen) {
      this.closeDropdown();
    } else {
      this.openDropdown();
    }
  }

  openDropdown() {
    if (this.state.isOpen) return;
    
    this.state.isOpen = true;
    this.elements.dropdown.classList.add('show');
    this.elements.trigger.setAttribute('aria-expanded', 'true');
    
    // 添加脉冲效果 - 与原有组件保持一致
    this.elements.container.classList.add('pulse');
    setTimeout(() => {
      this.elements.container.classList.remove('pulse');
    }, 1000);
    
    this.emit('opened');
  }

  closeDropdown() {
    if (!this.state.isOpen) return;
    
    this.state.isOpen = false;
    this.elements.dropdown.classList.remove('show');
    this.elements.trigger.setAttribute('aria-expanded', 'false');
    
    this.emit('closed');
  }

  /**
   * 语言选择方法 - 与原有组件保持一致
   */
  async selectLanguage(langCode) {
    if (langCode === this.state.currentLanguage || this.state.isLoading) return;
    
    this.state.isLoading = true;
    this.elements.container.classList.add('loading');
    
    try {
      // 模拟加载延迟
      await new Promise(resolve => setTimeout(resolve, 300));
      
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
      
      // 添加脉冲效果
      this.elements.container.classList.add('pulse');
      setTimeout(() => {
        this.elements.container.classList.remove('pulse');
      }, 1000);
      
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
      const contentSpan = this.elements.trigger.querySelector('.ls-trigger-content');
      if (contentSpan) {
        contentSpan.textContent = currentLang.code.toUpperCase();
      }
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
    
    const indicator = this.elements.container.querySelector('.ls-toggle-indicator-enhanced');
    const activeOption = this.elements.container.querySelector('.ls-toggle-option-enhanced.active');
    
    if (indicator && activeOption) {
      const rect = activeOption.getBoundingClientRect();
      const containerRect = this.elements.container.getBoundingClientRect();
      
      indicator.style.left = (rect.left - containerRect.left + 4) + 'px';
      indicator.style.width = (rect.width - 8) + 'px';
    }
  }

  /**
   * 获取语言信息 - 与原有组件保持一致
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
   * 语言偏好管理 - 与原有组件保持一致
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
   * 位置管理 - 与原有组件保持一致
   */
  restorePosition() {
    const saved = localStorage.getItem('languageSelectorPosition');
    if (saved) {
      try {
        const position = JSON.parse(saved);
        this.elements.container.style.left = position.x + 'px';
        this.elements.container.style.top = position.y + 'px';
        this.elements.container.style.right = 'auto';
        this.state.position = position;
        this.checkEdgeCollapse(position.x, position.y);
      } catch (e) {
        console.warn('Failed to restore position:', e);
      }
    }
  }

  savePosition() {
    localStorage.setItem('languageSelectorPosition', JSON.stringify(this.state.position));
  }

  /**
   * 翻译功能 - 与原有组件保持一致
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
    document.removeEventListener('click', this.handleOutsideClick);
    document.removeEventListener('mousemove', this.handleMouseMove);
    document.removeEventListener('mouseup', this.handleMouseUp);
    document.removeEventListener('touchmove', this.handleTouchMove);
    document.removeEventListener('touchend', this.handleTouchEnd);

    // 移除DOM元素
    if (this.elements.container && this.elements.container.parentNode) {
      this.elements.container.parentNode.removeChild(this.elements.container);
    }

    // 清理状态
    this.state.initialized = false;
    this.elements = {};
  }
}

// 全局实例管理 - 与原有组件保持兼容
window.SPADE_LANGUAGE_SELECTOR_ENHANCED = {
  instance: null,
  
  /**
   * 初始化语言选择器
   */
  init(options = {}) {
    if (this.instance) {
      this.instance.destroy();
    }
    
    this.instance = new LanguageSelectorEnhanced(options);
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
   * 兼容原有API的方法
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

// 页面加载完成后自动初始化 - 替换原有组件
document.addEventListener('DOMContentLoaded', () => {
  // 隐藏旧版本的语言选择器
  const oldSelector = document.getElementById('languageSelector');
  if (oldSelector) {
    oldSelector.style.display = 'none';
  }
  
  // 初始化增强版本
  window.SPADE_LANGUAGE_SELECTOR_ENHANCED.init({
    mode: 'dropdown',
    draggable: true,
    autoClose: true
  });
  
  console.log('Language Selector Enhanced 已初始化');
});