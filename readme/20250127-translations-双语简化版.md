# SPADE翻译组件简化修改 - 2025年1月27日

## 修改概述

将SPADE网站的翻译组件从多语言支持简化为仅支持中英双语翻译，提高系统性能和维护效率。

## 主要修改

### 1. 移除多语言支持
- 删除了原有的复杂多语言配置
- 移除了日语、韩语、法语、德语、西班牙语、俄语等语言支持
- 仅保留中文（zh-Hans）和英文（en）两种语言

### 2. 简化语言检测逻辑
- 简化了浏览器语言检测逻辑
- 如果浏览器语言以'zh'开头，则设置为中文
- 其他情况默认设置为英文

### 3. 优化翻译组件架构
```javascript
window.SPADETranslations = {
    supportedLanguages: ['zh-Hans', 'en'],  // 仅支持中英双语
    currentLanguage: 'zh-Hans',
    // ... 其他方法
}
```

### 4. 保持向后兼容性
- 保留了原有的全局函数接口
```javascript
window.initializeTranslation = function(lang) { ... };
window.translatePage = function(lang) { ... };
window.getTranslation = function(key, lang) { ... };
```

## 功能特性

### 1. 语言切换器
- 自动生成简洁的中英文切换器
- 显示当前语言状态
- 点击切换语言功能

### 2. 自动初始化
- 页面加载完成后自动初始化翻译系统
- 根据用户偏好或浏览器语言设置默认语言

### 3. 本地存储
- 记住用户的语言选择偏好
- 下次访问时自动应用上次选择的语言

### 4. 翻译功能
- 支持元素文本翻译（data-translate属性）
- 支持属性翻译（placeholder、title、alt等）
- 支持表单元素翻译

## 使用方法

### HTML中使用翻译属性
```html
<!-- 文本翻译 -->
<h1 data-translate="Welcome to SPADE Database">欢迎使用SPADE数据库</h1>

<!-- 占位符翻译 -->
<input type="text" data-translate-placeholder="enter sequence" placeholder="输入序列">

<!-- 标题翻译 -->
<button data-translate-title="Search" title="搜索">搜索</button>
```

### JavaScript中使用翻译函数
```javascript
// 获取翻译文本
const text = window.getTranslation('Home');

// 切换语言
window.SPADETranslations.switchLanguage('en');

// 翻译整个页面
window.translatePage('zh-Hans');
```

## 性能优化

### 1. 代码体积减少
- 删除了大量多语言配置数据
- 简化了语言检测逻辑
- 减少了不必要的依赖

### 2. 加载速度提升
- 不再需要加载多种语言包
- 简化的初始化流程
- 更快的语言切换响应

### 3. 维护成本降低
- 只需维护中英文两种翻译
- 简化的代码结构便于调试
- 减少了潜在的兼容性问题

## 兼容性说明

### 1. 浏览器支持
- 支持所有现代浏览器
- IE11及以上版本兼容

### 2. 向后兼容
- 保持原有API接口不变
- 现有页面无需修改即可使用

### 3. 移动设备支持
- 完整支持移动端浏览器
- 响应式语言切换器

## 文件结构

```
js/translations.js - 简化后的双语翻译组件
├── SPADE_TRANSLATIONS - 中英文翻译数据
├── SPADETranslations - 翻译组件类
└── 兼容性函数 - 保持向后兼容
```

## 未来扩展

如需要添加其他语言支持，可以：
1. 在`SPADE_TRANSLATIONS`中添加新语言配置
2. 在`supportedLanguages`数组中添加语言代码
3. 在`getLanguageDisplayName`中添加显示名称
4. 在`getBrowserLanguage`中添加检测逻辑

## 测试建议

1. 测试中英文切换功能
2. 验证语言偏好保存功能
3. 检查页面元素翻译完整性
4. 测试移动端语言切换器
5. 验证向后兼容性 