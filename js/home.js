<script>
    // 修复图片加载问题
    document.addEventListener('DOMContentLoaded', function() {
        // 处理可能不存在的背景图片
        const bgImages = document.querySelectorAll('img[src$="particles-bg.png"]');
        bgImages.forEach(img => {
            img.onerror = function() {
                // 移除不存在的背景图片元素或替换为纯色背景
                this.style.display = 'none';
                if (this.parentElement) {
                    this.parentElement.style.backgroundColor = 'rgba(43, 16, 85, 0.8)';
                }
            };
        });
        
        // 初始化移动端横屏提示
        initOrientationModal();
        
        // 初始化新的页面进度指示器
        initPageProgressIndicator();
        
        // 增强搜索表单功能
        enhanceSearchForm();
    });
    
    // 增强搜索表单功能
    function enhanceSearchForm() {
        const searchForm = document.getElementById('searchForm');
        if (!searchForm) return;
        
        searchForm.addEventListener('submit', function(e) {
            const input = document.querySelector('.search-input');
            const categorySelect = document.querySelector('.search-category');
            const searchButton = document.querySelector('.search-button');
            
            if (!input || !categorySelect || !searchButton) return;
            
            const query = input.value.trim();
            const category = categorySelect.value;
            
            if (query) {
                // 添加动画效果
                searchButton.classList.add('searching');
                
                // 存储最近搜索到localStorage
                try {
                    const recentSearches = JSON.parse(localStorage.getItem('recentSearches') || '[]');
                    recentSearches.unshift({ 
                        query, 
                        category, 
                        timestamp: Date.now() 
                    });
                    // 只保留最近5次搜索
                    localStorage.setItem('recentSearches', JSON.stringify(recentSearches.slice(0, 5)));
                } catch (err) {
                    console.warn('无法保存搜索历史', err);
                }
                
                // 不阻止表单提交，让默认行为继续
            } else {
                // 如果输入为空，阻止提交
                e.preventDefault();
                input.focus();
                // 添加抖动动画反馈
                input.classList.add('shake');
                setTimeout(() => input.classList.remove('shake'), 500);
            }
        });
    }
    
    // 移动端横屏提示功能
    function initOrientationModal() {
        const orientationModal = document.getElementById('orientationModal');
        
        if (!orientationModal) {
            console.warn('横屏提示模态框未找到');
            return;
        }
        
        // 检测是否为移动设备
        function isMobileDevice() {
            // 检测多种移动设备标识
            const userAgent = navigator.userAgent.toLowerCase();
            const mobileKeywords = [
                'mobile', 'android', 'iphone', 'ipad', 'ipod', 
                'blackberry', 'windows phone', 'webos'
            ];
            
            const isMobileUserAgent = mobileKeywords.some(keyword => 
                userAgent.includes(keyword)
            );
            
            // 如果UserAgent明确表示是移动设备，直接返回true
            if (isMobileUserAgent) {
                return true;
            }
            
            // 排除明确的桌面环境
            const desktopKeywords = ['windows nt', 'macintosh', 'linux x86'];
            const isDesktopUserAgent = desktopKeywords.some(keyword => 
                userAgent.includes(keyword)
            );
            
            // 如果是桌面操作系统，即使有触摸支持也不认为是移动设备
            if (isDesktopUserAgent) {
                return false;
            }
            
            // 检测指针精度（移动设备通常是粗糙指针）
            const hasCoarsePointer = window.matchMedia && 
                window.matchMedia('(pointer: coarse)').matches;
            
            // 检测触摸支持
            const hasTouch = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
            
            // 检测屏幕尺寸和像素比
            const isSmallScreen = window.innerWidth <= 768; // 更严格的尺寸限制
            const hasHighDPR = window.devicePixelRatio > 1.5; // 移动设备通常有较高的像素比
            
            // 综合判断：需要同时满足多个条件
            return hasCoarsePointer && hasTouch && isSmallScreen && hasHighDPR;
        }
        
                 // 检测屏幕方向
         function getOrientation() {
             // 优先使用screen.orientation API
             if (screen.orientation) {
                 return screen.orientation.angle === 0 || screen.orientation.angle === 180 
                     ? 'portrait' : 'landscape';
             }
             
             // 备用方案：比较宽高（添加一定的容差值以避免边界情况）
             const aspectRatio = window.innerWidth / window.innerHeight;
             return aspectRatio > 1.2 ? 'landscape' : 'portrait';
         }
        
        // 显示/隐藏弹窗
        function toggleOrientationModal(show) {
            if (show) {
                orientationModal.classList.add('show');
                // 防止背景滚动
                document.body.style.overflow = 'hidden';
                
                // 添加进入动画延迟
                setTimeout(() => {
                    const content = orientationModal.querySelector('.orientation-content');
                    if (content) {
                        content.style.animation = 'modalSlideIn 0.6s cubic-bezier(0.34, 1.56, 0.64, 1)';
                    }
                }, 100);
                
                console.log('横屏提示弹窗已显示');
            } else {
                orientationModal.classList.remove('show');
                // 恢复背景滚动
                document.body.style.overflow = '';
                console.log('横屏提示弹窗已隐藏');
            }
        }
        
                 // 检查是否需要显示横屏提示
         function checkOrientationNeed() {
             const isMobile = isMobileDevice();
             const isPortrait = getOrientation() === 'portrait';
             const isLandscape = getOrientation() === 'landscape';
             const isDismissed = sessionStorage.getItem('orientationTipDismissed') === 'true';
             
             console.log('设备检测结果:', { 
                 isMobile, 
                 orientation: getOrientation(),
                 screenSize: `${window.innerWidth}x${window.innerHeight}`,
                 userAgent: navigator.userAgent,
                 isDismissed
             });
             
             // 更新关闭按钮的显示状态
             const closeBtn = document.getElementById('orientationCloseBtn');
             if (closeBtn) {
                 closeBtn.style.display = isLandscape ? 'flex' : 'none';
             }
             
             // 只在移动设备且竖屏时显示提示，且用户未手动关闭
             if (isMobile && isPortrait && !isDismissed) {
                 // 添加小延迟，确保页面完全加载
                 setTimeout(() => {
                     toggleOrientationModal(true);
                 }, 500);
             } else {
                 toggleOrientationModal(false);
             }
         }
        
        // 防抖函数，避免方向变化时频繁触发
        function debounce(func, wait) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        }
        
        // 创建防抖的检查函数
        const debouncedCheck = debounce(checkOrientationNeed, 300);
        
        // 监听屏幕方向变化
        function setupOrientationListeners() {
            // 现代浏览器的方向变化事件
            if (screen.orientation) {
                screen.orientation.addEventListener('change', debouncedCheck);
            }
            
            // 备用事件监听器
            window.addEventListener('orientationchange', debouncedCheck);
            window.addEventListener('resize', debouncedCheck);
            
            // 监听页面可见性变化（用户切换应用后回来）
            document.addEventListener('visibilitychange', () => {
                if (!document.hidden) {
                    // 页面重新可见时检查方向
                    setTimeout(debouncedCheck, 100);
                }
            });
        }
        
        // 添加键盘事件监听（ESC键关闭弹窗，仅在横屏时）
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && orientationModal.classList.contains('show')) {
                // 只有在横屏状态下才允许ESC关闭
                if (getOrientation() === 'landscape') {
                    toggleOrientationModal(false);
                }
            }
        });
        
        // 添加弹窗内容点击事件（点击内容区域不关闭）
        const orientationContent = orientationModal.querySelector('.orientation-content');
        if (orientationContent) {
            orientationContent.addEventListener('click', (e) => {
                e.stopPropagation(); // 阻止事件冒泡
            });
        }
        
                 // 点击弹窗背景关闭（仅在横屏时）
         orientationModal.addEventListener('click', (e) => {
             if (e.target === orientationModal && getOrientation() === 'landscape') {
                 toggleOrientationModal(false);
             }
         });
         
         // 关闭按钮事件
         const orientationCloseBtn = document.getElementById('orientationCloseBtn');
         if (orientationCloseBtn) {
             orientationCloseBtn.addEventListener('click', () => {
                 toggleOrientationModal(false);
                 // 设置会话存储，在当前会话中不再显示提示
                 sessionStorage.setItem('orientationTipDismissed', 'true');
             });
         }
        
        // 初始化检查
        checkOrientationNeed();
        
        // 设置事件监听器
        setupOrientationListeners();
        
        // 添加额外的保险检查 - 每隔5秒检查一次
        setInterval(() => {
            // 只在弹窗可见时才进行检查
            if (orientationModal.classList.contains('show')) {
                const currentOrientation = getOrientation();
                if (currentOrientation === 'landscape') {
                    toggleOrientationModal(false);
                }
            }
        }, 5000);
        
        // 在页面完全加载后再次检查
        window.addEventListener('load', () => {
            setTimeout(checkOrientationNeed, 1000);
        });
        
        console.log('横屏提示模块已初始化');
    }
    
    // 页面进度指示器功能
    function initPageProgressIndicator() {
        // 获取所有章节和指示点
        const sections = [
            document.querySelector('.search-section'),
            document.querySelector('.info-cards-section'),
            document.querySelector('.research-map-section'),
            document.querySelector('.stats-section'),
            document.querySelector('.team-section')
        ];
        
        const sectionDots = document.querySelectorAll('.section-dot');
        const progressFill = document.querySelector('.progress-fill');
        
        // 设置激活状态的函数
        function setActiveDot(index) {
            sectionDots.forEach(dot => dot.classList.remove('active'));
            if (index >= 0 && index < sectionDots.length) {
                sectionDots[index].classList.add('active');
            }
        }
        
        // 初始激活第一个点
        setActiveDot(0);
        
        // 使用节流函数优化滚动性能
        let scrollTimeout = null;
        
        // 监听滚动事件
        window.addEventListener('scroll', () => {
            // 立即更新进度条，无延迟
            const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            const scrollHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
            const scrollPercentage = Math.min(100, Math.max(0, (scrollTop / scrollHeight) * 100));
            
            // 更新进度条填充高度
            if (progressFill) {
                progressFill.style.height = `${scrollPercentage}%`;
            }
            
            // 使用节流限制章节检测频率
            if (scrollTimeout) return;
            
            scrollTimeout = setTimeout(() => {
                // 确定当前可见章节
                let currentSectionIndex = -1;
                
                sections.forEach((section, index) => {
                    if (!section) return;
                    
                    const rect = section.getBoundingClientRect();
                    const windowHeight = window.innerHeight;
                    
                    // 当章节位于视口中央或上方时激活对应点
                    if (rect.top <= windowHeight * 0.4 && rect.bottom > windowHeight * 0.2) {
                        currentSectionIndex = index;
                    }
                });
                
                // 设置当前激活点
                setActiveDot(currentSectionIndex);
                
                scrollTimeout = null;
            }, 50);
        }, { passive: true });
        
        // 添加点击导航功能
        sectionDots.forEach((dot, index) => {
            dot.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                
                if (sections[index]) {
                    // 立即设置活跃状态提供视觉反馈
                    setActiveDot(index);
                    
                    // 添加即时点击效果
                    dot.style.transform = 'scale(1.4)';
                    dot.style.background = 'var(--accent-color)';
                    
                    // 平滑滚动到对应章节
                    sections[index].scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                    
                    // 恢复样式
                    setTimeout(() => {
                        dot.style.transform = '';
                        dot.style.background = '';
                    }, 150);
                }
            });
            
            // 添加鼠标悬停效果增强响应性
            dot.addEventListener('mouseenter', () => {
                dot.style.transform = 'scale(1.1)';
            });
            
            dot.addEventListener('mouseleave', () => {
                if (!dot.classList.contains('active')) {
                    dot.style.transform = '';
                }
            });
            
            // 添加触摸设备支持
            dot.addEventListener('touchstart', (e) => {
                e.preventDefault();
                dot.style.transform = 'scale(1.2)';
                dot.style.background = 'var(--accent-color)';
            });
            
            dot.addEventListener('touchend', (e) => {
                e.preventDefault();
                setTimeout(() => {
                    dot.style.transform = '';
                    dot.style.background = '';
                }, 100);
            });
        });
        
        // 初始检查滚动位置
        window.dispatchEvent(new Event('scroll'));
    }
</script>
