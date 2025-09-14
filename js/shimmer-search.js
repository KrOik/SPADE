// 搜索框闪光效果控制器 - 简化版
class ShimmerSearchController {
    constructor() {
        this.searchContainer = null;
        this.shimmerElement = null;
        this.isInitialized = false;
        this.init();
    }

    init() {
        // 等待DOM加载完成
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setup());
        } else {
            this.setup();
        }
    }

    setup() {
        // 查找搜索容器
        this.searchContainer = document.getElementById('searchForm');
        
        // 如果没有找到主页搜索表单，查找搜索页面的过滤器
        if (!this.searchContainer) {
            this.searchContainer = document.querySelector('.filter');
        }
        
        if (!this.searchContainer) {
            console.warn('搜索表单或过滤器未找到');
            return;
        }

        this.activateShimmerEffect();
        this.isInitialized = true;
    }

    activateShimmerEffect() {
        // 添加闪光效果类
        this.searchContainer.classList.add('shimmer-effect');
        
        // 只为主页搜索框添加闪光遮罩元素
        if (this.searchContainer.tagName.toLowerCase() === 'form') {
            this.shimmerElement = document.createElement('div');
            this.shimmerElement.className = 'shimmer';
            this.searchContainer.appendChild(this.shimmerElement);
        }
        
        // 搜索页面的过滤器使用CSS伪元素，无需添加DOM元素
        console.log('闪光效果已激活');
    }

    // 手动触发闪光效果
    triggerShimmer() {
        if (!this.isInitialized || !this.searchContainer) return;
        
        // 简单的闪光触发效果
        this.searchContainer.style.animation = 'none';
        setTimeout(() => {
            this.searchContainer.style.animation = '';
        }, 10);
    }

    // 启用/禁用闪光效果
    toggleShimmerEffect(enable = true) {
        if (!this.searchContainer) return;
        
        if (enable) {
            this.searchContainer.classList.add('shimmer-effect');
            // 只为表单添加shimmer元素
            if (this.searchContainer.tagName.toLowerCase() === 'form' && 
                this.shimmerElement && 
                !this.searchContainer.contains(this.shimmerElement)) {
                this.searchContainer.appendChild(this.shimmerElement);
            }
        } else {
            this.searchContainer.classList.remove('shimmer-effect');
            // 移除shimmer元素
            if (this.shimmerElement && this.searchContainer.contains(this.shimmerElement)) {
                this.searchContainer.removeChild(this.shimmerElement);
            }
        }
    }

    // 获取状态
    isActive() {
        return this.isInitialized && this.searchContainer && this.searchContainer.classList.contains('shimmer-effect');
    }
}

// 全局实例
let shimmerSearchController;

// 初始化控制器
document.addEventListener('DOMContentLoaded', () => {
    shimmerSearchController = new ShimmerSearchController();
});

// 导出给全局使用
window.ShimmerSearchController = ShimmerSearchController;
if (typeof shimmerSearchController !== 'undefined') {
    window.shimmerSearchController = shimmerSearchController;
} 