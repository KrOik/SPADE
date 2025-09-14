# Peptide Card页面修复：SPADE ID显示和阅读进度组件

**时间**: 2025年1月26日  
**文件**: peptide_card.html  
**改动内容**: 修复SPADE ID显示优先级和阅读进度组件加载问题

## 问题描述

1. **页面标题问题**: 页面标题和浏览器标签仍显示DRAMP ID，需要优先显示SPADE ID
2. **阅读进度组件问题**: 阅读进度组件未能成功加载和初始化

## 解决方案

### 1. SPADE ID优先显示修复

#### 页面标题逻辑更新
```javascript
// 优先使用SPADE ID，然后是Peptide Name
const spadeId = findFieldValue(peptide, 'SPADE ID');
const peptideName = findFieldValue(peptide, 'Peptide Name');

// 更新页面标题和浏览器标签
const displayTitle = spadeId || peptideName || 'Unknown Peptide';
pageTitle.textContent = displayTitle;

// 更新浏览器标签标题
if (spadeId) {
    document.title = `${spadeId} - SPADE Peptide Details`;
} else if (peptideName) {
    document.title = `${peptideName} - SPADE Peptide Details`;
} else {
    document.title = 'SPADE Peptide Details';
}
```

#### 优先级设置
1. **第一优先级**: SPADE ID（如 SPADE_N_00001）
2. **第二优先级**: Peptide Name（肽名称）
3. **默认值**: 'Unknown Peptide'

### 2. 阅读进度组件加载修复

#### 改进的初始化策略
```javascript
function initReadingProgress() {
    // 等待DOM完全加载和组件可用
    const tryInitialize = () => {
        if (window.ReadingProgress && typeof window.ReadingProgress === 'function') {
            try {
                const readingProgress = new window.ReadingProgress({
                    theme: 'default',
                    visibilityThreshold: 0.1,
                    scrollDuration: 300,
                    position: 'below-header',
                    headerSelector: '.top-nav' // 明确指定导航栏选择器
                });
                
                // 保存实例到全局变量以便调试
                window.readingProgressInstance = readingProgress;
                return true;
            } catch (error) {
                console.error('Failed to initialize Reading Progress:', error);
                return false;
            }
        }
        return false;
    };
    
    // 立即尝试初始化，失败则重试
    if (!tryInitialize()) {
        let retryCount = 0;
        const maxRetries = 10;
        const retryInterval = setInterval(() => {
            retryCount++;
            if (tryInitialize() || retryCount >= maxRetries) {
                clearInterval(retryInterval);
            }
        }, 500);
    }
}
```

#### 脚本加载优化
```javascript
// 特殊处理阅读进度脚本
if (src === 'js/reading-progress.js') {
    script.onload = function() {
        console.log('Reading Progress script loaded successfully');
        console.log('window.ReadingProgress:', window.ReadingProgress);
        // 等待DOM完全准备好后初始化
        if (document.readyState === 'complete') {
            setTimeout(initReadingProgress, 200);
        } else {
            window.addEventListener('load', () => {
                setTimeout(initReadingProgress, 200);
            });
        }
    };
    script.onerror = function(error) {
        console.error('Reading Progress script failed to load:', error);
    };
}
```

## 技术改进

### 1. 错误处理增强
- 添加详细的错误日志输出
- 实现重试机制（最多10次，每次间隔500ms）
- 提供调试信息（保存组件实例到全局变量）

### 2. 加载时序优化
- 等待DOM完全加载后再初始化组件
- 增加脚本加载成功的详细日志
- 明确指定导航栏选择器（`.top-nav`）

### 3. 兼容性改进
- 检查组件构造函数的有效性
- 提供多种初始化时机的处理
- 确保组件加载失败不影响页面其他功能

## 预期效果

### 页面标题显示
- 对于SPADE_N_00001：
  - 页面标题：`SPADE_N_00001`
  - 浏览器标签：`SPADE_N_00001 - SPADE Peptide Details`

### 阅读进度组件
- 位置：导航栏正下方
- 样式：霓虹青色-粉色渐变
- 功能：实时显示页面滚动进度
- 触发：滚动10%后显示

## 调试方法

### 检查SPADE ID显示
```javascript
// 在浏览器控制台检查
console.log('页面标题:', document.getElementById('peptide-name').textContent);
console.log('浏览器标签:', document.title);
```

### 检查阅读进度组件
```javascript
// 在浏览器控制台检查
console.log('组件构造函数:', window.ReadingProgress);
console.log('组件实例:', window.readingProgressInstance);
console.log('进度条元素:', document.querySelector('.reading-progress'));
```

## 后续维护

1. **监控加载状态**: 定期检查组件是否正常加载
2. **性能优化**: 根据实际使用情况调整重试策略
3. **用户反馈**: 收集用户对新标题显示方式的反馈
4. **扩展应用**: 将相同的修复方案应用到其他页面 