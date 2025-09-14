/**
 * 阅读进度和返回顶部组件
 * 可复用的现代化组件，支持玻璃拟态设计风格
 * 
 * @author SPADE Team
 * @version 1.0.0
 * @date 2025-01-26
 */

class ReadingProgressComponent {
    constructor(options = {}) {
        // 默认配置
        this.config = {
            // 显示阈值（滚动多少像素后显示返回顶部按钮）
            visibilityThreshold: 300,
            
            // 滚动动画时长（毫秒）
            scrollDuration: 800,
            
            // 进度条位置配置
            progressBar: {
                position: 'header-bottom', // 'header-bottom' | 'floating'
                height: 4,
                zIndex: 9999
            },
            
            // 返回顶部按钮配置
            backToTop: {
                position: 'bottom-right', // 'bottom-right' | 'bottom-left'
                size: 50,
                zIndex: 1000
            },
            
            // 颜色主题
            theme: {
                primary: '#00D4FF',
                secondary: '#FF006E',
                success: '#00FF88',
                successSecondary: '#00E676'
            },
            
            // 响应式断点
            breakpoints: {
                mobile: 480,
                tablet: 768
            },
            
            // 自动初始化
            autoInit: true,
            
            // 调试模式
            debug: false
        };

        // 合并用户配置
        this.config = { ...this.config, ...options };
        
        // 组件状态
        this.state = {
            isVisible: false,
            isProgressBarVisible: false,
            ticking: false,
            initialized: false
        };

        // DOM 元素引用
        this.elements = {
            container: null,
            progressBar: null,
            progressFill: null,
            backToTopBtn: null
        };

        // 如果启用自动初始化
        if (this.config.autoInit) {
            this.init();
        }
    }

    /**
     * 初始化组件
     */
    init() {
        if (this.state.initialized) {
            // this.log('组件已经初始化过了');
            return;
        }

        // this.log('开始初始化阅读进度组件');
        
        // 创建组件结构
        this.createElements();
        
        // 注入样式
        this.injectStyles();
        
        // 绑定事件
        this.bindEvents();
        
        // 初始状态检查
        this.updateProgress();
        this.toggleVisibility();
        
        // 确保返回顶部按钮初始状态正确
        if (this.elements.container) {
            this.elements.container.classList.remove('visible');
            this.state.isVisible = false;
        }
        
        this.state.initialized = true;
        // this.log('阅读进度组件初始化完成');
    }

    /**
     * 创建DOM元素
     */
    createElements() {
        // 创建进度条容器
        this.createProgressBar();
        
        // 创建返回顶部按钮
        this.createBackToTopButton();
    }

    /**
     * 创建进度条
     */
    createProgressBar() {
        // 创建进度条容器
        const progressContainer = document.createElement('div');
        progressContainer.id = 'reading-progress-bar-container';
        progressContainer.className = 'reading-progress-bar-container';

        // 创建进度条
        const progressBar = document.createElement('div');
        progressBar.className = 'reading-progress-bar';

        // 创建进度填充
        const progressFill = document.createElement('div');
        progressFill.className = 'reading-progress-fill';
        progressFill.id = 'reading-progress-fill';

        // 组装结构
        progressBar.appendChild(progressFill);
        progressContainer.appendChild(progressBar);

        // 插入到页面中（header下方）
        this.insertProgressBar(progressContainer);

        // 保存引用
        this.elements.progressBar = progressBar;
        this.elements.progressFill = progressFill;
        this.elements.progressContainer = progressContainer;
    }

    /**
     * 插入进度条到合适位置
     */
    insertProgressBar(progressContainer) {
        if (this.config.progressBar.position === 'header-bottom') {
            // 查找header元素
            const header = document.querySelector('header');
            if (header) {
                // 在header后插入，并设置为相对定位
                progressContainer.classList.add('header-positioned');
                header.insertAdjacentElement('afterend', progressContainer);
                
                // 调整样式以确保紧贴header
                progressContainer.style.position = 'sticky';
                progressContainer.style.top = '0';
                progressContainer.style.left = '0';
                progressContainer.style.width = '100%';
                progressContainer.style.zIndex = this.config.progressBar.zIndex;
            } else {
                // 如果没有header，插入到body开头并使用fixed定位
                document.body.insertBefore(progressContainer, document.body.firstChild);
            }
        } else {
            // 浮动模式，插入到body末尾
            document.body.appendChild(progressContainer);
        }
    }

    /**
     * 创建返回顶部按钮
     */
    createBackToTopButton() {
        // 创建按钮容器
        const container = document.createElement('div');
        container.id = 'back-to-top-container';
        container.className = 'back-to-top-container';

        // 创建按钮
        const button = document.createElement('button');
        button.id = 'back-to-top-btn';
        button.className = 'back-to-top-btn';
        button.title = '返回顶部';
        button.setAttribute('aria-label', '返回页面顶部');

        // 创建图标
        const icon = document.createElement('i');
        icon.className = 'fas fa-chevron-up';

        // 组装结构
        button.appendChild(icon);
        container.appendChild(button);

        // 插入到页面中
        document.body.appendChild(container);

        // 保存引用
        this.elements.backToTopBtn = button;
        this.elements.container = container;
    }

    /**
     * 注入样式
     */
    injectStyles() {
        // 检查是否已经注入过样式
        if (document.getElementById('reading-progress-styles')) {
            return;
        }

        const style = document.createElement('style');
        style.id = 'reading-progress-styles';
        style.textContent = this.getStyles();
        document.head.appendChild(style);
    }

    /**
     * 获取组件样式
     */
    getStyles() {
        const { theme, progressBar, backToTop, breakpoints } = this.config;
        
        return `
            /* 阅读进度条样式 */
            .reading-progress-bar-container {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: ${progressBar.height}px;
                z-index: ${progressBar.zIndex};
                pointer-events: none;
                transition: opacity 0.3s ease;
            }

            .reading-progress-bar-container.header-positioned {
                position: relative;
                top: auto;
                left: auto;
            }

                         .reading-progress-bar {
                 width: 100%;
                 height: 100%;
                 background: linear-gradient(135deg, rgba(0, 0, 0, 0.4), rgba(0, 0, 0, 0.2));
                 border-bottom: 1px solid rgba(255, 255, 255, 0.3);
                 backdrop-filter: blur(15px);
                 box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
                 position: relative;
                 overflow: hidden;
             }

            .reading-progress-bar::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 1px;
                background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
            }

                         .reading-progress-fill {
                 height: 100%;
                 width: 0%;
                 background: linear-gradient(90deg, ${theme.primary}, ${theme.secondary}, ${theme.primary});
                 background-size: 200% 100%;
                 transition: width 0.3s ease;
                 animation: progressGlow 2s ease-in-out infinite alternate;
                 position: relative;
                 box-shadow: 0 0 15px rgba(0, 212, 255, 0.6), 0 0 30px rgba(255, 0, 110, 0.4);
                 border-radius: 2px;
             }

                         .reading-progress-fill.complete {
                 background: linear-gradient(90deg, ${theme.success}, ${theme.successSecondary}, ${theme.success});
                 box-shadow: 0 0 20px rgba(0, 255, 136, 0.8), 0 0 40px rgba(0, 230, 118, 0.5);
             }

                         @keyframes progressGlow {
                 0% { 
                     background-position: 0% 50%;
                     box-shadow: 0 0 15px rgba(0, 212, 255, 0.6), 0 0 30px rgba(255, 0, 110, 0.4);
                     filter: brightness(1);
                 }
                 100% { 
                     background-position: 100% 50%;
                     box-shadow: 0 0 25px rgba(0, 212, 255, 0.8), 0 0 50px rgba(255, 0, 110, 0.6);
                     filter: brightness(1.2);
                 }
             }

            /* 返回顶部按钮样式 */
            .back-to-top-container {
                position: fixed;
                bottom: 30px;
                right: 30px;
                z-index: 10001;
                opacity: 0;
                visibility: hidden;
                transform: translateY(20px);
                transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
                pointer-events: none;
            }

            .back-to-top-container.visible {
                opacity: 1;
                visibility: visible;
                transform: translateY(0);
                pointer-events: auto;
            }

            .back-to-top-btn {
                width: ${backToTop.size}px;
                height: ${backToTop.size}px;
                background: linear-gradient(135deg, rgba(255, 255, 255, 0.25), rgba(255, 255, 255, 0.1));
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 50%;
                color: white;
                font-size: 1.2em;
                cursor: pointer;
                transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
                backdrop-filter: blur(20px);
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
                display: flex;
                align-items: center;
                justify-content: center;
                position: relative;
                overflow: hidden;
            }

            .back-to-top-btn::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 1px;
                background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
            }

            .back-to-top-btn:hover {
                background: linear-gradient(135deg, rgba(255, 255, 255, 0.35), rgba(255, 255, 255, 0.2));
                transform: translateY(-3px) scale(1.05);
                box-shadow: 0 12px 35px rgba(0, 0, 0, 0.25), 
                            0 0 20px rgba(102, 126, 234, 0.3);
                border-color: rgba(255, 255, 255, 0.3);
            }

            .back-to-top-btn:active {
                transform: translateY(-1px) scale(1.02);
                transition: all 0.1s ease;
            }

            .back-to-top-btn i {
                transition: transform 0.3s ease;
            }

            .back-to-top-btn:hover i {
                transform: translateY(-2px);
            }

            /* 响应式设计 */
            @media (max-width: ${breakpoints.tablet}px) {
                .back-to-top-container {
                    bottom: 20px;
                    right: 20px;
                }

                .back-to-top-btn {
                    width: 45px;
                    height: 45px;
                    font-size: 1.1em;
                }

                .reading-progress-bar-container {
                    height: 3px;
                }
            }

            @media (max-width: ${breakpoints.mobile}px) {
                .back-to-top-container {
                    bottom: 15px;
                    right: 15px;
                }

                .back-to-top-btn {
                    width: 40px;
                    height: 40px;
                    font-size: 1em;
                }

                .reading-progress-bar-container {
                    height: 3px;
                }
            }
        `;
    }

    /**
     * 绑定事件监听器
     */
    bindEvents() {
        // 滚动事件监听（使用节流）
        window.addEventListener('scroll', () => {
            if (!this.state.ticking) {
                requestAnimationFrame(() => {
                    this.updateProgress();
                    this.toggleVisibility();
                    this.state.ticking = false;
                });
                this.state.ticking = true;
            }
        });

        // 返回顶部按钮点击事件
        this.elements.backToTopBtn.addEventListener('click', (e) => {
            e.preventDefault();
            this.scrollToTop();
        });

        // 窗口大小变化事件
        window.addEventListener('resize', () => {
            this.updateProgress();
        });

        // 键盘事件支持
        this.elements.backToTopBtn.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                this.scrollToTop();
            }
        });
    }

    /**
     * 更新阅读进度
     */
    updateProgress() {
        // 计算滚动进度
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        const scrollHeight = document.documentElement.scrollHeight - window.innerHeight;
        
        if (scrollHeight > 0) {
            const progress = Math.min(Math.max(scrollTop / scrollHeight, 0), 1);
            const percentage = progress * 100;
            
            // 更新进度条
            this.elements.progressFill.style.width = `${percentage}%`;
            
            // 添加完成状态样式
            if (percentage > 90) {
                this.elements.progressFill.classList.add('complete');
            } else {
                this.elements.progressFill.classList.remove('complete');
            }

            // 移除控制台输出，避免频繁的进度日志
            // this.log(`阅读进度: ${percentage.toFixed(1)}%`);
        }
    }

    /**
     * 切换组件可见性
     */
    toggleVisibility() {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        const shouldShow = scrollTop > this.config.visibilityThreshold;

        if (shouldShow && !this.state.isVisible) {
            this.showBackToTop();
        } else if (!shouldShow && this.state.isVisible) {
            this.hideBackToTop();
        }
        
        // 调试信息
    //     this.log(`滚动位置: ${scrollTop}, 阈值: ${this.config.visibilityThreshold}, 应该显示: ${shouldShow}, 当前状态: ${this.state.isVisible}`);
    }

    /**
     * 显示返回顶部按钮
     */
    showBackToTop() {
        this.elements.container.classList.add('visible');
        this.state.isVisible = true;
        // this.log('显示返回顶部按钮');
    }

    /**
     * 隐藏返回顶部按钮
     */
    hideBackToTop() {
        this.elements.container.classList.remove('visible');
        this.state.isVisible = false;
        // this.log('隐藏返回顶部按钮');
    }

    /**
     * 平滑滚动到顶部
     */
    scrollToTop() {
        const startPosition = window.pageYOffset;
        const startTime = performance.now();
        
        // 添加按钮点击反馈
        this.elements.backToTopBtn.style.transform = 'translateY(-1px) scale(0.95)';
        setTimeout(() => {
            this.elements.backToTopBtn.style.transform = '';
        }, 150);

        const animateScroll = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / this.config.scrollDuration, 1);
            
            // 使用缓动函数
            const easeOutCubic = 1 - Math.pow(1 - progress, 3);
            const currentPosition = startPosition * (1 - easeOutCubic);
            
            window.scrollTo(0, currentPosition);
            
            if (progress < 1) {
                requestAnimationFrame(animateScroll);
            } else {
                // this.log('滚动到顶部完成');
            }
        };
        
        requestAnimationFrame(animateScroll);
        // this.log('开始滚动到顶部');
    }

    /**
     * 手动刷新组件状态
     */
    refresh() {
        this.updateProgress();
        this.toggleVisibility();
    }

    /**
     * 设置可见性阈值
     */
    setVisibilityThreshold(threshold) {
        this.config.visibilityThreshold = threshold;
        this.toggleVisibility();
    }

    /**
     * 更新主题颜色
     */
    setTheme(theme) {
        this.config.theme = { ...this.config.theme, ...theme };
        this.injectStyles(); // 重新注入样式
    }

    /**
     * 销毁组件
     */
    destroy() {
        // 移除事件监听器
        window.removeEventListener('scroll', this.updateProgress);
        window.removeEventListener('resize', this.updateProgress);

        // 移除DOM元素
        if (this.elements.container) {
            this.elements.container.remove();
        }
        if (this.elements.progressContainer) {
            this.elements.progressContainer.remove();
        }

        // 移除样式
        const styleElement = document.getElementById('reading-progress-styles');
        if (styleElement) {
            styleElement.remove();
        }

        // 重置状态
        this.state.initialized = false;
        // this.log('组件已销毁');
    }

    /**
     * 日志输出
     */
    log(message) {
        if (this.config.debug) {
            console.log(`[ReadingProgress] ${message}`);
        }
    }
}

// 自动初始化（如果在浏览器环境中）
if (typeof window !== 'undefined') {
    // 页面加载完成后自动初始化
    document.addEventListener('DOMContentLoaded', () => {
        // 检查是否已经有实例
        if (!window.readingProgressComponent) {
            setTimeout(() => {
                window.readingProgressComponent = new ReadingProgressComponent({
                    debug: false // 可以设置为 true 开启调试模式
                });
            }, 100);
        }
    });

    // 为了兼容性，也在window.onload中初始化
    window.addEventListener('load', () => {
        if (!window.readingProgressComponent) {
            window.readingProgressComponent = new ReadingProgressComponent({
                debug: false
            });
        }
    });
}

// 导出类（支持模块化）
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ReadingProgressComponent;
}

// 全局暴露
if (typeof window !== 'undefined') {
    window.ReadingProgressComponent = ReadingProgressComponent;
} 