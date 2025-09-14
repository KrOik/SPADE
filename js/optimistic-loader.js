/**
 * 乐观加载器 - 优化页面资源加载
 * 实现渐进式加载策略，优先加载关键资源，提高用户体验
 */

class OptimisticLoader {
    constructor() {
        this.resourceQueue = [];
        this.loadedResources = new Set();
        this.criticalResources = new Set();
        this.nonCriticalResources = [];
        this.observer = null;
        this.initialized = false;
    }

    /**
     * 初始化加载器
     */
    init() {
        if (this.initialized) return;
        
        console.log('乐观加载器初始化中...');
        
        // 拦截资源加载
        this._interceptResourceLoading();
        
        // 设置交叉观察器用于懒加载
        this._setupIntersectionObserver();
        
        // 分类资源
        this._categorizeCriticalResources();
        
        // 优先加载关键资源
        this._loadCriticalResources();
        
        // 监听DOM内容加载完成事件
        document.addEventListener('DOMContentLoaded', () => {
            console.log('DOM内容已加载，开始加载非关键资源');
            this._loadNonCriticalResources();
        });
        
        // 监听页面完全加载事件
        window.addEventListener('load', () => {
            console.log('页面完全加载完成');
            this._handlePageFullyLoaded();
        });
        
        this.initialized = true;
        console.log('乐观加载器初始化完成');
    }

    /**
     * 拦截资源加载
     * 拦截CSS和JS的加载，实现按优先级加载
     */
    _interceptResourceLoading() {
        // 保存原始的createElement方法
        const originalCreateElement = document.createElement.bind(document);
        
        // 重写createElement方法以拦截资源创建
        document.createElement = (tagName) => {
            const element = originalCreateElement(tagName);
            
            if (tagName.toLowerCase() === 'link' || tagName.toLowerCase() === 'script') {
                // 拦截设置src和href属性
                const originalSetAttribute = element.setAttribute.bind(element);
                element.setAttribute = (name, value) => {
                    if ((name === 'href' && element.rel === 'stylesheet') || name === 'src') {
                        // 检查是否为非关键资源
                        if (this._isNonCriticalResource(value)) {
                            console.log(`延迟加载资源: ${value}`);
                            this.nonCriticalResources.push({
                                element: element,
                                attributeName: name,
                                attributeValue: value
                            });
                            return element;
                        }
                    }
                    return originalSetAttribute(name, value);
                };
            }
            
            return element;
        };
    }

    /**
     * 设置交叉观察器用于懒加载
     */
    _setupIntersectionObserver() {
        this.observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const target = entry.target;
                    if (target.dataset.src) {
                        target.src = target.dataset.src;
                        target.removeAttribute('data-src');
                        this.observer.unobserve(target);
                    }
                    if (target.dataset.backgroundSrc) {
                        target.style.backgroundImage = `url(${target.dataset.backgroundSrc})`;
                        target.removeAttribute('data-background-src');
                        this.observer.unobserve(target);
                    }
                }
            });
        }, {
            rootMargin: '100px',
            threshold: 0.1
        });
    }

    /**
     * 分类关键资源
     */
    _categorizeCriticalResources() {
        // 定义关键CSS文件
        const criticalCssFiles = [
            'css/tailwind.min.css',
            'css/design-system.css',
            'css/home.css'
        ];
        
        // 将关键资源添加到集合中
        criticalCssFiles.forEach(file => this.criticalResources.add(file));
        
        // 添加自定义字体文件到关键资源
        this.criticalResources.add('css/custom-fonts.css');
    }

    /**
     * 检查是否为非关键资源
     * @param {string} url - 资源URL
     * @returns {boolean} - 是否为非关键资源
     */
    _isNonCriticalResource(url) {
        // 如果是关键资源，返回false
        if (this.criticalResources.has(url)) return false;
        
        // 检查是否为非关键类型的资源
        const nonCriticalPatterns = [
            /\.jpg$/i,
            /\.png$/i,
            /\.svg$/i,
            /font-awesome/i,
            /googleapis\.com\/css/i,
            /language-selector/i
        ];
        
        return nonCriticalPatterns.some(pattern => pattern.test(url));
    }

    /**
     * 加载关键资源
     */
    _loadCriticalResources() {
        console.log('加载关键资源...');
        // 关键资源已在HTML中直接加载
    }

    /**
     * 加载非关键资源
     */
    _loadNonCriticalResources() {
        console.log(`开始加载${this.nonCriticalResources.length}个非关键资源`);
        
        // 使用requestIdleCallback或setTimeout分批加载非关键资源
        const loadBatch = (startIndex, batchSize) => {
            const endIndex = Math.min(startIndex + batchSize, this.nonCriticalResources.length);
            
            for (let i = startIndex; i < endIndex; i++) {
                const resource = this.nonCriticalResources[i];
                if (resource && resource.element) {
                    const { element, attributeName, attributeValue } = resource;
                    console.log(`加载资源: ${attributeValue}`);
                    element.setAttribute(attributeName, attributeValue);
                }
            }
            
            // 如果还有资源需要加载，安排下一批
            if (endIndex < this.nonCriticalResources.length) {
                if (window.requestIdleCallback) {
                    window.requestIdleCallback(() => loadBatch(endIndex, batchSize));
                } else {
                    setTimeout(() => loadBatch(endIndex, batchSize), 50);
                }
            }
        };
        
        // 开始加载第一批，每批5个资源
        loadBatch(0, 5);
    }

    /**
     * 处理页面完全加载事件
     */
    _handlePageFullyLoaded() {
        // 移除加载指示器
        const loadingIndicator = document.querySelector('.loading-indicator');
        if (loadingIndicator) {
            loadingIndicator.classList.add('fade-out');
            setTimeout(() => {
                loadingIndicator.style.display = 'none';
            }, 500);
        }
        
        // 应用页面完全加载后的动画效果
        document.body.classList.add('fully-loaded');
    }

    /**
     * 懒加载图片
     */
    lazyLoadImages() {
        // 选择所有带有data-src属性的图片
        const lazyImages = document.querySelectorAll('img[data-src]');
        lazyImages.forEach(img => this.observer.observe(img));
        
        // 选择所有带有data-background-src属性的元素
        const lazyBackgrounds = document.querySelectorAll('[data-background-src]');
        lazyBackgrounds.forEach(el => this.observer.observe(el));
        
        console.log(`设置了${lazyImages.length}张图片和${lazyBackgrounds.length}个背景进行懒加载`);
    }
}

// 创建并初始化乐观加载器实例
const optimisticLoader = new OptimisticLoader();
document.addEventListener('DOMContentLoaded', () => {
    optimisticLoader.init();
    optimisticLoader.lazyLoadImages();
});