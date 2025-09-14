// 修复后的语言选择器组件
window.SPADE_TRANSLATION_UTILS = {
    // 支持的语言
    supportedLanguages: ['en', 'zh-Hans', 'es', 'de', 'ja'],
    
    currentLanguage: 'en',
    initialized: false,
    translations: {},
    
    // 拖拽相关
    isDragging: false,
    startX: 0,
    startY: 0,
    initialX: 0,
    initialY: 0,
    edgeThreshold: 60,
    dragThreshold: 5,
    hasMoved: false,
    hasMoved: false,

    // 加载翻译
    async loadTranslations() {
        try {
            const response = await fetch('data/translation.json');
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            this.translations = await response.json();
        } catch (error) {
            console.error('Failed to load translations:', error);
        }
    },
    
    // 获取语言偏好
    getLanguagePreference() {
        return localStorage.getItem('spade_language') || this.getBrowserLanguage();
    },
    
    // 保存语言偏好
    saveLanguagePreference(lang) {
        localStorage.setItem('spade_language', lang);
    },
    
    // 获取浏览器语言
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
    },
    
    // 获取语言显示名称
    getLanguageDisplayName(langCode) {
        const displayNames = {
            'zh-Hans': '中文',
            'en': 'English',
            'es': 'Español',
            'de': 'Deutsch',
            'ja': '日本語'
        };
        return displayNames[langCode] || langCode;
    },
    
    // 设置语言切换器
    setupLanguageSwitcher() {
        const languageSelector = document.getElementById('languageSelector');
        if (!languageSelector) return;

        // 创建下拉菜单
        const dropdown = document.createElement('div');
        dropdown.className = 'language-dropdown';

        this.supportedLanguages.forEach(lang => {
            const option = document.createElement('div');
            option.className = 'language-option';
            option.setAttribute('data-lang', lang);
            
            if (lang === this.currentLanguage) {
                option.classList.add('active');
            }

            option.textContent = this.getLanguageDisplayName(lang);

            option.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.switchLanguage(lang);
                this.hideDropdown();
            });

            dropdown.appendChild(option);
        });

        languageSelector.appendChild(dropdown);

        // 点击切换下拉菜单
        languageSelector.addEventListener('click', (e) => {
            e.stopPropagation();
            // 检查是否是快速点击（不是拖拽）
            const clickTime = Date.now();
            const isQuickClick = !this.hasMoved && !this.isDragging && 
                               (clickTime - (this.dragStartTime || 0)) > 200;
            
            if (isQuickClick) {
                this.toggleDropdown();
            }
        });

        // 点击外部关闭
        document.addEventListener('click', () => {
            this.hideDropdown();
        });

        // 点击处理
        languageSelector.addEventListener('click', this.onClick.bind(this));

        // 设置拖拽
        this.setupDragging(languageSelector);
    },

    // 设置拖拽功能
    setupDragging(selector) {
        const element = selector.querySelector('.language-current');
        if (!element) return;

        // 鼠标事件
        element.addEventListener('mousedown', this.onMouseDown.bind(this));
        document.addEventListener('mousemove', this.onMouseMove.bind(this));
        document.addEventListener('mouseup', this.onMouseUp.bind(this));

        // 触摸事件
        element.addEventListener('touchstart', this.onTouchStart.bind(this));
        document.addEventListener('touchmove', this.onTouchMove.bind(this));
        document.addEventListener('touchend', this.onTouchEnd.bind(this));

        // 防止拖拽时触发点击
        element.addEventListener('click', this.onClick.bind(this));
    },

    // 鼠标按下
    onMouseDown(e) {
        e.preventDefault();
        this.startDragging(e.clientX, e.clientY);
    },

    // 触摸开始
    onTouchStart(e) {
        if (e.touches.length === 1) {
            const touch = e.touches[0];
            this.startDragging(touch.clientX, touch.clientY);
        }
    },

    // 开始拖拽
    startDragging(x, y) {
        this.isDragging = false;
        this.hasMoved = false;
        this.startX = x;
        this.startY = y;
        
        const selector = document.getElementById('languageSelector');
        const rect = selector.getBoundingClientRect();
        this.initialX = rect.left;
        this.initialY = rect.top;
        
        // 添加拖拽开始标记
        this.dragStartTime = Date.now();
    },

    // 鼠标移动
    onMouseMove(e) {
        if (!this.startX && !this.startY) return;
        
        const deltaX = Math.abs(e.clientX - this.startX);
        const deltaY = Math.abs(e.clientY - this.startY);
        
        if (!this.isDragging && (deltaX > this.dragThreshold || deltaY > this.dragThreshold)) {
            this.isDragging = true;
            this.hasMoved = true;
            const selector = document.getElementById('languageSelector');
            selector.classList.add('dragging');
        }
        
        if (this.isDragging) {
            this.updatePosition(e.clientX, e.clientY);
        }
    },

    // 触摸移动
    onTouchMove(e) {
        if (!this.startX && !this.startY || e.touches.length !== 1) return;
        e.preventDefault();
        
        const touch = e.touches[0];
        const deltaX = Math.abs(touch.clientX - this.startX);
        const deltaY = Math.abs(touch.clientY - this.startY);
        
        if (!this.isDragging && (deltaX > this.dragThreshold || deltaY > this.dragThreshold)) {
            this.isDragging = true;
            this.hasMoved = true;
            const selector = document.getElementById('languageSelector');
            selector.classList.add('dragging');
        }
        
        if (this.isDragging) {
            this.updatePosition(touch.clientX, touch.clientY);
        }
    },

    // 更新位置
    updatePosition(x, y) {
        const selector = document.getElementById('languageSelector');
        const deltaX = x - this.startX;
        const deltaY = y - this.startY;
        
        let newX = this.initialX + deltaX;
        let newY = this.initialY + deltaY;
        
        // 边界限制
        const maxX = window.innerWidth - selector.offsetWidth;
        const maxY = window.innerHeight - selector.offsetHeight;
        
        newX = Math.max(0, Math.min(newX, maxX));
        newY = Math.max(0, Math.min(newY, maxY));
        
        selector.style.left = newX + 'px';
        selector.style.top = newY + 'px';
        selector.style.right = 'auto';
        
        // 边缘检测
        this.checkEdgeCollapse(newX, newY);
    },

    // 检查边缘收缩
    checkEdgeCollapse(x, y) {
        const selector = document.getElementById('languageSelector');
        const isNearEdge = x <= this.edgeThreshold || 
                          x >= window.innerWidth - selector.offsetWidth - this.edgeThreshold ||
                          y <= this.edgeThreshold || 
                          y >= window.innerHeight - selector.offsetHeight - this.edgeThreshold;
        
        if (isNearEdge) {
            selector.classList.add('edge-collapsed');
        } else {
            selector.classList.remove('edge-collapsed');
        }
    },

    // 鼠标释放
    onMouseUp() {
        this.stopDragging();
    },

    // 触摸结束
    onTouchEnd() {
        this.stopDragging();
    },

    // 停止拖拽
    stopDragging() {
        if (!this.isDragging) {
            this.startX = 0;
            this.startY = 0;
            this.hasMoved = false;
            this.dragStartTime = 0;
            return;
        }
        
        this.isDragging = false;
        const selector = document.getElementById('languageSelector');
        selector.classList.remove('dragging');
        
        // 保存位置
        const rect = selector.getBoundingClientRect();
        localStorage.setItem('languageSelectorPosition', JSON.stringify({
            x: rect.left,
            y: rect.top
        }));
        
        this.startX = 0;
        this.startY = 0;
        
        // 延迟重置hasMoved，避免拖拽后立即触发点击
        setTimeout(() => {
            this.hasMoved = false;
            this.dragStartTime = 0;
        }, 150);
    },

    // 点击处理
    onClick(e) {
        if (this.isDragging || this.hasMoved) {
            e.preventDefault();
            e.stopPropagation();
            return false;
        }
        // 允许点击事件继续传播到父元素
        return true;
    },

    // 切换下拉菜单
    toggleDropdown() {
        const dropdown = document.querySelector('.language-dropdown');
        if (!dropdown) return;
        
        const isVisible = dropdown.classList.contains('show');
        if (isVisible) {
            this.hideDropdown();
        } else {
            this.showDropdown();
        }
    },

    // 显示下拉菜单
    showDropdown() {
        const dropdown = document.querySelector('.language-dropdown');
        if (!dropdown) return;
        
        // 重置动画状态
        dropdown.style.display = 'block';
        dropdown.style.transform = 'translateY(-10px)';
        dropdown.style.opacity = '0';
        
        // 强制重绘
        dropdown.offsetHeight;
        
        // 添加显示动画
        dropdown.classList.add('show');
        
        // 添加脉冲效果
        const selector = document.getElementById('languageSelector');
        selector.classList.add('pulse');
        
        setTimeout(() => {
            selector.classList.remove('pulse');
        }, 1000);
    },

    // 隐藏下拉菜单
    hideDropdown() {
        const dropdown = document.querySelector('.language-dropdown');
        if (!dropdown) return;
        
        dropdown.classList.remove('show');
        
        // 动画结束后隐藏元素
        setTimeout(() => {
            if (!dropdown.classList.contains('show')) {
                dropdown.style.display = 'none';
            }
        }, 300);
    },

    // 切换语言
    switchLanguage(lang) {
        if (!this.supportedLanguages.includes(lang) || lang === this.currentLanguage) {
            return;
        }

        this.currentLanguage = lang;
        this.saveLanguagePreference(lang);

        this.translatePage(this.currentLanguage);
        
        // 更新活动状态
        const options = document.querySelectorAll('.language-option');
        options.forEach(option => {
            option.classList.remove('active');
        });
        
        const activeOption = document.querySelector(`.language-option[data-lang="${lang}"]`);
        if (activeOption) {
            activeOption.classList.add('active');
        }

        // 添加切换动画
        const selector = document.getElementById('languageSelector');
        selector.classList.add('pulse');
        
        setTimeout(() => {
            selector.classList.remove('pulse');
        }, 1000);
    },
    
    // 初始化
    async initialize() {
        if (this.initialized) return;
        
        await this.loadTranslations();
        
        this.currentLanguage = this.getLanguagePreference();
        this.saveLanguagePreference(this.currentLanguage);

        this.setupLanguageSwitcher();
        this.translatePage(this.currentLanguage);
        
        // 恢复位置
        this.restorePosition();
        
        this.initialized = true;
    },

    // 恢复位置
    restorePosition() {
        const saved = localStorage.getItem('languageSelectorPosition');
        if (saved) {
            try {
                const position = JSON.parse(saved);
                const selector = document.getElementById('languageSelector');
                selector.style.left = position.x + 'px';
                selector.style.top = position.y + 'px';
                selector.style.right = 'auto';
                
                this.checkEdgeCollapse(position.x, position.y);
            } catch (e) {
                console.warn('Failed to restore language selector position:', e);
            }
        }
    },

    // 获取翻译
    getTranslation(key, lang) {
        lang = lang || this.currentLanguage;
        return this.translations[lang]?.[key] || key;
    },

    // 翻译元素
    translateElement(element, lang) {
        lang = lang || this.currentLanguage;
        const key = element.dataset.translate;
        if (!key) return;
        
        const translation = this.getTranslation(key, lang);
        if (translation && translation !== key) {
            element.innerHTML = translation;
        }
    },

    // 翻译页面
    translatePage(lang) {
        lang = lang || this.currentLanguage;

        const elements = document.querySelectorAll('[data-translate]');
        console.log(`Translating ${elements.length} elements to ${lang}`);
        
        elements.forEach(element => {
            this.translateElement(element, lang);
        });

        this.translateAttributes(lang);
    },

    // 翻译属性
    translateAttributes(lang) {
        lang = lang || this.currentLanguage;
        
        const elements = document.querySelectorAll('[data-translate-placeholder]');
        elements.forEach(element => {
            const key = element.dataset.translatePlaceholder;
            const translation = this.getTranslation(key, lang);
            if (translation) {
                element.placeholder = translation;
            }
        });
    }
};

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    window.SPADE_TRANSLATION_UTILS.initialize();
}); 