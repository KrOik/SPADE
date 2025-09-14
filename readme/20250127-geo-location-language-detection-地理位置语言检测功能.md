# 地理位置语言检测功能实现

## 功能概述

为 `language-selector-minimal.js` 添加了基于用户地理位置的语言自动匹配功能，使用 `ipapi.co` API 获取用户所在地信息，并根据国家代码自动设置合适的语言。

## 主要功能

### 1. 地理位置检测
- 使用 `fetch` 调用 `https://ipapi.co/json/` API
- 获取用户的国家代码和地理位置信息
- 异步执行，不阻塞页面初始化

### 2. 语言映射
支持以下国家到语言的映射：

| 国家代码 | 国家名称 | 映射语言 |
|---------|---------|---------|
| CN | 中国 | 中文 (zh-Hans) |
| TW | 台湾 | 中文 (zh-Hans) |
| HK | 香港 | 中文 (zh-Hans) |
| SG | 新加坡 | 中文 (zh-Hans) |
| ES | 西班牙 | Español (es) |
| MX | 墨西哥 | Español (es) |
| AR | 阿根廷 | Español (es) |
| CO | 哥伦比亚 | Español (es) |
| PE | 秘鲁 | Español (es) |
| DE | 德国 | Deutsch (de) |
| AT | 奥地利 | Deutsch (de) |
| CH | 瑞士 | Deutsch (de) |
| JP | 日本 | 日本語 (ja) |
| US | 美国 | English (en) |
| GB | 英国 | English (en) |
| CA | 加拿大 | English (en) |
| AU | 澳大利亚 | English (en) |
| NZ | 新西兰 | English (en) |

### 3. 智能语言设置
- 如果检测到的语言在支持列表中，自动切换到对应语言
- 如果检测到的语言不在支持列表中，显示英文提示并设置为英文

### 4. 通知系统
- 当用户所在地不在支持语言内时，显示英文通知
- 通知透明度设置为 45%，符合要求
- 通知内容："Language has been set to English"
- 通知样式：气泡式设计，位于屏幕下方中央
- 5秒后自动消失
- 使用 `sessionStorage` 避免重复显示

## 技术实现

### 核心方法

#### `detectGeoLocation()`
```javascript
async detectGeoLocation() {
  if (this.state.geoLocationDetected) return;
  
  try {
    const response = await fetch('https://ipapi.co/json/');
    const data = await response.json();
    const countryCode = data.country_code;
    const detectedLanguage = this.mapCountryToLanguage(countryCode);
    
    if (!this.options.supportedLanguages.includes(detectedLanguage)) {
      this.showLanguageNotification();
      // 确保语言选择器状态更新为英文
      if (this.state.currentLanguage !== 'en') {
        this.state.currentLanguage = 'en';
        this.saveLanguagePreference('en');
        this.updateTriggerContent();
        this.updateOptionsState();
        this.translatePage();
      }
      this.state.geoLocationDetected = true;
      return;
    }
    
    if (detectedLanguage !== this.state.currentLanguage) {
      await this.selectLanguage(detectedLanguage);
    }
    
    this.state.geoLocationDetected = true;
  } catch (error) {
    console.warn('Geo-location detection failed:', error);
    this.showLanguageNotification();
  }
}
```

#### `showLanguageNotification()`
```javascript
showLanguageNotification() {
  // 检查是否已经显示过通知
  if (sessionStorage.getItem('language_notification_shown')) {
    return;
  }
  
  // 标记已显示通知
  sessionStorage.setItem('language_notification_shown', 'true');
  
  // 创建通知元素
  const notification = document.createElement('div');
  notification.id = 'language-notification';
  notification.className = 'language-notification';
  notification.innerHTML = `
    <div class="notification-content">
      <span class="notification-icon">🌐</span>
      <span class="notification-text">Language has been set to English</span>
    </div>
  `;
  
  // 添加样式和动画
  // ...样式代码...
  
  document.body.appendChild(notification);
  
  // 5秒后自动移除
  setTimeout(() => {
    if (notification.parentNode) {
      notification.style.animation = 'notificationSlideOut 0.5s ease-in';
      notification.addEventListener('animationend', () => {
        if (notification.parentNode) {
          notification.remove();
        }
      });
    }
  }, 5000);
}
```

### 样式特性

#### 通知样式
- 位置：屏幕下方中央
- 透明度：45%
- 背景：半透明黑色，带模糊效果
- 边框：半透明白色边框
- 动画：滑入和滑出动画
- 响应式：移动端适配

#### 动画效果
```css
@keyframes notificationSlideIn {
  from {
    opacity: 0;
    transform: translateX(-50%) translateY(20px);
  }
  to {
    opacity: 0.45;
    transform: translateX(-50%) translateY(0);
  }
}

@keyframes notificationSlideOut {
  from {
    opacity: 0.45;
    transform: translateX(-50%) translateY(0);
  }
  to {
    opacity: 0;
    transform: translateX(-50%) translateY(20px);
  }
}
```

## 配置选项

在构造函数中可以配置以下选项：

```javascript
const options = {
  enableGeoLocation: true, // 启用地理位置检测
  supportedLanguages: ['en', 'zh-Hans', 'es', 'de', 'ja'], // 支持的语言列表
  // ... 其他选项
};
```

## 事件系统

组件会触发以下事件：

- `languageSelector:initialized` - 初始化完成
- `languageSelector:languageChanged` - 语言切换时

## 测试页面

创建了测试页面 `test/geo-location-language-test.html` 用于验证功能：

- 测试地理位置检测
- 清除通知标记
- 重置语言设置
- 手动显示通知
- 实时状态显示

## 使用方法

### 基本使用
```javascript
// 自动初始化
document.addEventListener('DOMContentLoaded', () => {
  window.SPADE_LANGUAGE_SELECTOR_MINIMAL.init();
});
```

### 手动控制
```javascript
// 清除通知标记
window.SPADE_LANGUAGE_SELECTOR_MINIMAL.clearNotificationMark();

// 获取实例
const instance = window.SPADE_LANGUAGE_SELECTOR_MINIMAL.getInstance();

// 手动显示通知
instance.showLanguageNotification();
```

## 错误处理

- API 调用失败时显示默认语言通知
- 网络错误时优雅降级
- 使用 try-catch 确保功能稳定性

## 性能优化

- 异步执行地理位置检测，不阻塞页面加载
- 延迟1秒执行，确保页面完全加载
- 使用 sessionStorage 避免重复显示通知
- 样式复用，避免重复添加

## 兼容性

- 支持现代浏览器
- 移动端响应式设计
- 优雅降级处理
- 无障碍访问支持

## 更新记录

- 2025-01-27: 初始实现地理位置语言检测功能
- 添加 ipapi.co API 集成
- 实现智能语言映射
- 添加通知系统
- 创建测试页面
- 完善错误处理和性能优化
