# Home.html Header和Footer集成修改

## 修改概述
为home.html页面添加了header和footer，参照search页面的样式设计，确保与页面整体风格保持一致。

## 主要修改内容

### 1. Header添加
- **位置**: 在body标签后，fullPage容器前
- **样式**: 采用固定定位，渐变背景，毛玻璃效果
- **功能**: 
  - Logo和网站名称
  - 导航菜单（Home, Search, Tools, Statistics）
  - 移动端响应式菜单切换
  - 当前页面高亮显示

### 2. Footer添加
- **位置**: 作为fullPage的最后一个section，确保可以通过导航访问
- **样式**: 深色背景，三栏布局，毛玻璃效果
- **内容**:
  - About部分：About SPADE, Advertising policy, Attribution & citations
  - Terms & Privacy部分：Terms of use, Editorial policy, Privacy policy
  - Support部分：Help center, Sitemap, Contact us
  - 版权信息

### 3. Language Selector位置调整
- **桌面端**: 调整到header下方（top: 100px）
- **移动端**: 进一步调整位置（top: 80px）并优化样式
- **避免重叠**: 确保与header和其他元素不重叠

### 4. CSS样式调整
- **Header样式**: 
  - 固定定位，z-index: 1000
  - 渐变背景和毛玻璃效果
  - 响应式设计，移动端菜单切换
- **Footer样式**:
  - 深色背景 (#250b53)
  - 三栏布局，响应式设计
  - 链接悬停效果
  - 毛玻璃效果和圆角设计
- **Language Selector样式**:
  - 响应式位置调整
  - 移动端优化

### 5. JavaScript功能
- **移动端导航**: 添加了移动端菜单切换功能
- **fullPage.js调整**: 
  - 添加paddingTop为header留出空间
  - 更新导航工具提示，包含Footer
  - 将footer包装在section中，确保可导航

### 6. 响应式设计
- **桌面端**: 完整显示header和footer
- **平板端**: 调整padding和字体大小
- **移动端**: 
  - 汉堡菜单切换
  - 垂直导航菜单
  - 调整logo和文字大小
  - language-selector位置优化

## 技术细节

### Header结构
```html
<header>
    <div class="logo-container">
        <a href="#" class="logo">
            <img src="./source/img/logo.png">
            SPADE
        </a>
        <div>System for Antimicrobial Peptide<br>Management and Database</div>
    </div>
    <button class="nav-toggle">
        <i class="fas fa-bars"></i>
    </button>
    <ul class="nav-menu">
        <li><a href="home.html" class="active">Home</a></li>
        <li><a href="search.html">Search</a></li>
        <li><a href="tools.html">Tools</a></li>
        <li><a href="statistics.html">Statistics</a></li>
    </ul>
</header>
```

### Footer结构（作为fullPage section）
```html
<!-- 9. Footer Section -->
<div class="section">
    <div class="container mx-auto px-8 h-full flex items-center justify-center">
        <div class="w-full">
            <footer>
                <div class="footer-content">
                    <div class="footer-section">
                        <h4>About</h4>
                        <ul>
                            <li><a href="spade.html#about-spade-footer">About SPADE</a></li>
                            <li><a href="spade.html#advertising-policy-footer">Advertising policy</a></li>
                            <li><a href="spade.html#attribution-citations-footer">Attribution & citations</a></li>
                        </ul>
                    </div>
                    <!-- Terms & Privacy Section -->
                    <!-- Support Section -->
                </div>
                <div class="footer-copyright">
                    &copy; SPADE.
                </div>
            </footer>
        </div>
    </div>
</div>
```

### Language Selector位置调整
```css
.language-selector {
    position: fixed;
    top: 100px; /* 桌面端调整到header下方 */
    right: 20px;
    z-index: 1001;
}

@media (max-width: 767px) {
    .language-selector {
        top: 80px; /* 移动端进一步调整 */
        right: 10px;
        padding: 6px 12px;
        font-size: 0.9em;
    }
}
```

## 兼容性考虑
- 与fullPage.js兼容，添加了paddingTop避免冲突
- 保持原有的动画和交互效果
- 响应式设计确保在各种设备上正常显示
- 与现有的翻译功能兼容
- **修复了导航问题**: footer现在作为fullPage的section，可以通过右侧导航访问

## 问题修复
1. **Language Selector重叠问题**: 调整位置到header下方，避免与header重叠
2. **Footer导航问题**: 将footer包装在fullPage section中，更新导航工具提示
3. **移动端优化**: 针对不同屏幕尺寸优化language-selector位置

## 文件修改
- `home.html`: 
  - 添加header和footer HTML结构
  - 调整language-selector位置
  - 将footer包装在fullPage section中
  - 更新fullPage.js配置
- 添加相应的CSS样式
- 添加JavaScript交互功能

## 效果
- 页面更加完整和专业
- 导航更加便捷，可以访问所有section包括footer
- 与网站其他页面风格统一
- 移动端体验优化
- 解决了元素重叠和导航问题 