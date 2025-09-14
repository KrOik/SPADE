/**
 * SPADE Quick Notes - 现代简约版
 * 轻量级悬浮笔记组件
 */
class QuickNotes {
    constructor() {
        this.isVisible = false;
        this.isMinimized = false;
        this.isDragging = false;
        this.dragStart = { x: 0, y: 0 };
        this.noteContainer = null;
        this.textarea = null;
        
        // 存储键
        this.storageKeys = {
            content: 'quick-notes-content',
            position: 'quick-notes-position',
            minimized: 'quick-notes-minimized'
        };
        
        this.init();
    }

    init() {
        this.createContainer();
        this.loadState();
        this.setupEvents();
        console.log('🗒️ Quick Notes initialized');
    }

    createContainer() {
        this.noteContainer = document.createElement('div');
        this.noteContainer.className = 'qn-container';
        this.noteContainer.innerHTML = `
            <div class="qn-header">
                <span class="qn-title">Quick Notes</span>
                <div class="qn-controls">
                    <button class="qn-btn qn-minimize" title="Minimize">_</button>
                    <button class="qn-btn qn-download" title="Download">⬇</button>
                    <button class="qn-btn qn-clear" title="Clear">🗑</button>
                    <button class="qn-btn qn-close" title="Close">×</button>
                </div>
            </div>
            <div class="qn-body">
                <textarea class="qn-textarea" placeholder="Write your thoughts..."></textarea>
                <div class="qn-footer">
                    <span class="qn-status">local storage only</span>
                    <span class="qn-count">0 characters</span>
                </div>
            </div>
        `;

        this.addStyles();
        document.body.appendChild(this.noteContainer);
        this.textarea = this.noteContainer.querySelector('.qn-textarea');
        this.noteContainer.style.display = 'none';
    }

    addStyles() {
        if (document.getElementById('qn-styles')) return;

        const style = document.createElement('style');
        style.id = 'qn-styles';
        style.textContent = `
            .qn-container {
                position: fixed;
                top: 100px;
                right: 30px;
                width: 320px;
                background: #ffffff;
                border-radius: 12px;
                box-shadow: 0 8px 40px rgba(0, 0, 0, 0.15);
                z-index: 9999;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                border: 1px solid rgba(255, 255, 255, 0.1);
                overflow: hidden;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                backdrop-filter: blur(10px);
            }

            .qn-container.minimized .qn-body {
                display: none;
            }

            .qn-container.minimized {
                width: 300px;
            }

            .qn-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 16px 20px;
                background: linear-gradient(to bottom, rgba(43, 16, 85, 0.98) 0%, rgba(43, 16, 85, 0.9) 100%);
                color: white;
                cursor: move;
                user-select: none;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            }

            .qn-title {
                font-weight: 600;
                font-size: 14px;
                letter-spacing: -0.2px;
            }

            .qn-controls {
                display: flex;
                gap: 8px;
            }

            .qn-btn {
                width: 28px;
                height: 28px;
                border: none;
                border-radius: 6px;
                background: rgba(255, 255, 255, 0.2);
                color: white;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 12px;
                font-weight: 600;
                transition: all 0.3s ease;
                backdrop-filter: blur(10px);
            }

            .qn-btn:hover {
                background: rgba(255, 255, 255, 0.3);
                transform: scale(1.05);
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
            }

            .qn-btn:active {
                transform: scale(0.95);
            }

            .qn-close:hover {
                background: rgba(239, 68, 68, 0.8);
            }

            .qn-body {
                display: flex;
                flex-direction: column;
                height: 280px;
            }

            .qn-textarea {
                flex: 1;
                border: none;
                outline: none;
                padding: 20px;
                font-family: inherit;
                font-size: 14px;
                line-height: 1.6;
                resize: none;
                background: transparent;
                color: #1f2937;
            }

            .qn-textarea::placeholder {
                color: #9ca3af;
            }

            .qn-textarea:focus {
                background: #fafafa;
            }

            .qn-footer {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 12px 20px;
                background: #f9fafb;
                border-top: 1px solid #f3f4f6;
                font-size: 12px;
                color: #6b7280;
            }

            .qn-status {
                display: flex;
                align-items: center;
                gap: 6px;
            }

            .qn-status::before {
                content: '●';
                color: #10b981;
                font-size: 8px;
            }

            .qn-count {
                font-weight: 500;
                color: #374151;
            }

            /* 响应式 */
            @media (max-width: 768px) {
                .qn-container {
                    right: 15px;
                    left: 15px;
                    width: auto;
                    top: 90px;
                }

                .qn-container.minimized {
                    width: auto;
                }

                .qn-body {
                    height: 200px;
                }
            }

            /* 自定义滚动条 */
            .qn-textarea::-webkit-scrollbar {
                width: 4px;
            }

            .qn-textarea::-webkit-scrollbar-track {
                background: transparent;
            }

            .qn-textarea::-webkit-scrollbar-thumb {
                background: #d1d5db;
                border-radius: 2px;
            }

            .qn-textarea::-webkit-scrollbar-thumb:hover {
                background: #9ca3af;
            }
        `;

        document.head.appendChild(style);
    }

    setupEvents() {
        const header = this.noteContainer.querySelector('.qn-header');
        const minimizeBtn = this.noteContainer.querySelector('.qn-minimize');
        const downloadBtn = this.noteContainer.querySelector('.qn-download');
        const clearBtn = this.noteContainer.querySelector('.qn-clear');
        const closeBtn = this.noteContainer.querySelector('.qn-close');

        // 拖拽
        header.addEventListener('mousedown', this.startDrag.bind(this));
        document.addEventListener('mousemove', this.onDrag.bind(this));
        document.addEventListener('mouseup', this.endDrag.bind(this));

        // 按钮事件
        minimizeBtn.addEventListener('click', this.toggleMinimize.bind(this));
        downloadBtn.addEventListener('click', this.download.bind(this));
        clearBtn.addEventListener('click', this.clear.bind(this));
        closeBtn.addEventListener('click', this.hide.bind(this));

        // 内容变化
        this.textarea.addEventListener('input', this.onInput.bind(this));

        // 快捷键
        document.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'N') {
                e.preventDefault();
                this.toggle();
            }
        });

        // 窗口大小变化
        window.addEventListener('resize', this.handleResize.bind(this));
    }

    startDrag(e) {
        if (e.target.closest('.qn-btn')) return;
        
        this.isDragging = true;
        const rect = this.noteContainer.getBoundingClientRect();
        this.dragStart.x = e.clientX - rect.left;
        this.dragStart.y = e.clientY - rect.top;
        
        this.noteContainer.style.transition = 'none';
        e.preventDefault();
    }

    onDrag(e) {
        if (!this.isDragging) return;

        const x = e.clientX - this.dragStart.x;
        const y = e.clientY - this.dragStart.y;

        // 边界限制
        const maxX = window.innerWidth - this.noteContainer.offsetWidth - 20;
        const maxY = window.innerHeight - this.noteContainer.offsetHeight - 20;

        const boundedX = Math.max(20, Math.min(x, maxX));
        const boundedY = Math.max(20, Math.min(y, maxY));

        this.noteContainer.style.left = boundedX + 'px';
        this.noteContainer.style.top = boundedY + 'px';
        this.noteContainer.style.right = 'auto';
    }

    endDrag() {
        if (!this.isDragging) return;
        
        this.isDragging = false;
        this.noteContainer.style.transition = '';
        this.savePosition();
    }

    toggleMinimize() {
        this.isMinimized = !this.isMinimized;
        this.noteContainer.classList.toggle('minimized', this.isMinimized);
        
        const btn = this.noteContainer.querySelector('.qn-minimize');
        btn.textContent = this.isMinimized ? '□' : '_';
        
        localStorage.setItem(this.storageKeys.minimized, this.isMinimized);
    }

    download() {
        const content = this.textarea.value.trim();
        if (!content) {
            this.showToast('没有内容可下载');
            return;
        }

        const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `笔记_${new Date().toISOString().slice(0, 10)}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        this.showToast('下载完成');
    }

    clear() {
        if (!this.textarea.value.trim()) return;
        
        if (confirm('确定要清空所有内容吗？')) {
            this.textarea.value = '';
            this.updateCount();
            this.saveContent();
            this.showToast('内容已清空');
        }
    }

    onInput() {
        this.updateCount();
        this.saveContent();
    }

    updateCount() {
        const count = this.textarea.value.length;
        const countEl = this.noteContainer.querySelector('.qn-count');
        countEl.textContent = `${count} 字符`;
    }

    saveContent() {
        localStorage.setItem(this.storageKeys.content, this.textarea.value);
    }

    savePosition() {
        const rect = this.noteContainer.getBoundingClientRect();
        const position = {
            top: rect.top,
            left: rect.left
        };
        localStorage.setItem(this.storageKeys.position, JSON.stringify(position));
    }

    loadState() {
        // 加载内容
        const content = localStorage.getItem(this.storageKeys.content);
        if (content) {
            this.textarea.value = content;
            this.updateCount();
        }

        // 加载位置
        const position = localStorage.getItem(this.storageKeys.position);
        if (position) {
            try {
                const pos = JSON.parse(position);
                if (pos.left >= 0 && pos.top >= 0) {
                    this.noteContainer.style.left = pos.left + 'px';
                    this.noteContainer.style.top = pos.top + 'px';
                    this.noteContainer.style.right = 'auto';
                }
            } catch (e) {
                console.warn('Failed to load position');
            }
        }

        // 加载最小化状态
        const minimized = localStorage.getItem(this.storageKeys.minimized) === 'true';
        if (minimized) {
            this.isMinimized = true;
            this.noteContainer.classList.add('minimized');
            this.noteContainer.querySelector('.qn-minimize').textContent = '□';
        }
    }

    handleResize() {
        const rect = this.noteContainer.getBoundingClientRect();
        if (rect.right > window.innerWidth || rect.bottom > window.innerHeight) {
            this.noteContainer.style.right = '30px';
            this.noteContainer.style.left = 'auto';
            this.noteContainer.style.top = '120px';
        }
    }

    showToast(message) {
        const toast = document.createElement('div');
        toast.textContent = message;
        toast.style.cssText = `
            position: fixed;
            top: 30px;
            right: 30px;
            background: #1f2937;
            color: white;
            padding: 12px 16px;
            border-radius: 8px;
            font-size: 14px;
            z-index: 10000;
            opacity: 0;
            transform: translateY(-10px);
            transition: all 0.3s ease;
        `;
        
        document.body.appendChild(toast);
        
        requestAnimationFrame(() => {
            toast.style.opacity = '1';
            toast.style.transform = 'translateY(0)';
        });
        
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateY(-10px)';
            setTimeout(() => document.body.removeChild(toast), 300);
        }, 2000);
    }

    // 公共 API
    show() {
        this.isVisible = true;
        this.noteContainer.style.display = 'block';
        setTimeout(() => this.textarea.focus(), 100);
    }

    hide() {
        this.isVisible = false;
        this.noteContainer.style.display = 'none';
    }

    toggle() {
        this.isVisible ? this.hide() : this.show();
    }

    getContent() {
        return this.textarea.value;
    }

    setContent(content) {
        this.textarea.value = content;
        this.updateCount();
        this.saveContent();
    }

    appendContent(content) {
        this.textarea.value += content;
        this.updateCount();
        this.saveContent();
    }

    isShown() {
        return this.isVisible;
    }
}

// 自动初始化
(function() {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    function init() {
        if (!window.quickNotes) {
            window.quickNotes = new QuickNotes();
        }
    }
})(); 