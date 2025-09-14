// 简化的抽屉式展示功能
let drawerChosenSlideNumber = 1;
let drawerOffset = 0;
let drawerBarOffset = 0;
let drawerIntervalID = null;
let isInView = false;

// 初始化抽屉轮播
function initDrawerCarousel() {
    // 设置可见性监听，只有在视口内时才自动轮播
    setupIntersectionObserver();
    
    // 点击功能
    const drawerBtns = Array.from(document.querySelectorAll(".drawer-btn"));
    drawerBtns.forEach((btn, index) => {
        btn.addEventListener("click", (e) => {
            e.preventDefault();
            clearInterval(drawerIntervalID);
            drawerSlideTo(index + 1);
            // 重启自动轮播
            if (isInView) {
                startAutoSlide();
            }
        });
    });

    // 鼠标悬停控制
    const drawerSlideSection = document.querySelector(".drawer-slide-section");
    if (drawerSlideSection) {
        drawerSlideSection.addEventListener("mouseenter", () => {
            clearInterval(drawerIntervalID);
        });

        drawerSlideSection.addEventListener("mouseleave", () => {
            if (isInView) {
                startAutoSlide();
            }
        });
    }

    // 添加滚动控制
    setupDrawerScrollControl();
}

// 设置可见性监听
function setupIntersectionObserver() {
    const drawerSection = document.querySelector('.drawer-showcase-section');
    if (!drawerSection) return;

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && entry.intersectionRatio > 0.3) {
                // 当section充分可见时启动自动轮播
                isInView = true;
                startAutoSlide();
            } else {
                // 当section不可见时停止自动轮播
                isInView = false;
                clearInterval(drawerIntervalID);
            }
        });
    }, {
        threshold: [0.1, 0.3, 0.5]
    });

    observer.observe(drawerSection);
}

// 启动自动轮播
function startAutoSlide() {
    clearInterval(drawerIntervalID);
    drawerIntervalID = setInterval(() => {
        const nextSlide = drawerChosenSlideNumber >= 4 ? 1 : drawerChosenSlideNumber + 1;
        drawerSlideTo(nextSlide);
    }, 4000);
}

// 切换到指定编号的幻灯片
function drawerSlideTo(slideNumber) {
    drawerBoxToggle(slideNumber);
    drawerBtnToggle(slideNumber);
    
    let previousSlideNumber = drawerChosenSlideNumber;
    drawerChosenSlideNumber = slideNumber;
    drawerOffset += (drawerChosenSlideNumber - previousSlideNumber) * (-100);
    drawerBarOffset += (drawerChosenSlideNumber - previousSlideNumber) * (100);
    
    drawerBarSlide(drawerBarOffset);
    
    const drawerSlides = document.querySelectorAll(".drawer-card");
    Array.from(drawerSlides).forEach(slide => {
        slide.style.transform = `translateY(${drawerOffset}%)`;
    });
}

// 切换抽屉面板状态
function drawerBoxToggle(drawerboxNumber) {
    let prevDrawerboxNumber = drawerChosenSlideNumber;
    const drawerboxes = document.querySelectorAll(".drawer-box");
    if (drawerboxes[prevDrawerboxNumber - 1]) {
        drawerboxes[prevDrawerboxNumber - 1].classList.toggle("active");
    }
    if (drawerboxes[drawerboxNumber - 1]) {
        drawerboxes[drawerboxNumber - 1].classList.toggle("active");
    }
}

// 切换抽屉按钮状态
function drawerBtnToggle(drawerBtnNumber) {
    let prevDrawerBtnNumber = drawerChosenSlideNumber;
    const drawerBtns = document.querySelectorAll(".drawer-btn");
    if (drawerBtns[prevDrawerBtnNumber - 1]) {
        drawerBtns[prevDrawerBtnNumber - 1].classList.toggle("active");
    }
    if (drawerBtns[drawerBtnNumber - 1]) {
        drawerBtns[drawerBtnNumber - 1].classList.toggle("active");
    }
}

// 移动导航条
function drawerBarSlide(barOffset) {
    const drawerBar = document.querySelector(".drawer-bar");
    if (drawerBar) {
        drawerBar.style.transform = `translateY(${barOffset}%)`;
    }
}

// 页面可见性API控制
document.addEventListener('visibilitychange', function() {
    if (document.hidden) {
        clearInterval(drawerIntervalID);
    } else if (isInView) {
        startAutoSlide();
    }
});

// 窗口失焦时暂停轮播
window.addEventListener('blur', function() {
    clearInterval(drawerIntervalID);
});

window.addEventListener('focus', function() {
    if (isInView) {
        startAutoSlide();
    }
});

// 导出函数以供外部调用
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        initDrawerCarousel,
        drawerSlideTo,
        startAutoSlide
    };
}

// 添加滚动控制功能
function setupDrawerScrollControl() {
    const drawerSection = document.querySelector('.drawer-showcase-section');
    if (!drawerSection) return;
    
    let isInDrawerSection = false;
    let isScrolling = false;
    
    // 检测是否在抽屉区域
    function checkIfInDrawerSection() {
        if (!drawerSection) return false;
        
        const rect = drawerSection.getBoundingClientRect();
        return (
            rect.top <= 0 &&
            rect.bottom >= window.innerHeight
        );
    }
    
    // 滚轮事件处理
    window.addEventListener('wheel', function(e) {
        isInDrawerSection = checkIfInDrawerSection();
        
        if (isInDrawerSection) {
            if (isScrolling) return;
            
            e.preventDefault();
            isScrolling = true;
            
            if (e.deltaY > 0) {
                // 向下滚动，切换到下一个抽屉
                const nextSlide = drawerChosenSlideNumber >= 4 ? 4 : drawerChosenSlideNumber + 1;
                
                if (nextSlide === 4) {
                    // 最后一个抽屉，播放完成后允许继续滚动
                    setTimeout(() => {
                        document.body.style.overflow = '';
                        window.scrollBy(0, 100); // 向下滚动一点
                    }, 500);
                } else {
                    drawerSlideTo(nextSlide);
                }
            } else {
                // 向上滚动，切换到上一个抽屉
                const prevSlide = drawerChosenSlideNumber <= 1 ? 1 : drawerChosenSlideNumber - 1;
                
                if (prevSlide === 1 && drawerChosenSlideNumber === 1) {
                    // 第一个抽屉，允许继续向上滚动
                    setTimeout(() => {
                        document.body.style.overflow = '';
                        window.scrollBy(0, -100); // 向上滚动一点
                    }, 500);
                } else {
                    drawerSlideTo(prevSlide);
                }
            }
            
            setTimeout(() => {
                isScrolling = false;
            }, 800);
        } else {
            document.body.style.overflow = '';
        }
    }, { passive: false });
    
    // 滚动事件处理
    window.addEventListener('scroll', function() {
        isInDrawerSection = checkIfInDrawerSection();
        
        if (isInDrawerSection) {
            document.body.style.overflow = 'hidden';
        }
    });
}