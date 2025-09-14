# Home.html Global Research Network 图表替换

## 修改时间
2025-01-26

## 修改文件
- home.html

## 改动内容

### 主要改进
将 "Global Research Network" 页面的ECharts图表 (`networkChart`) 替换为一张静态图片 (`./source/img/introduce/1.jpg`)。

### 原因
根据用户要求，为了简化页面内容或与其他设计保持一致，将动态生成的图表替换为指定的介绍性图片。

### 具体修改

#### 1. HTML结构修改
- 删除了 `<div id="networkChart" class="chart-container mb-8"></div>`。
- 在原位置插入了 `<img>` 标签：
  ```html
  <img src="./source/img/introduce/1.jpg" alt="Global Research Network" class="w-full h-auto rounded-lg shadow-lg">
  ```
- 为图片添加了 `alt` 文本以提高可访问性，并使用TailwindCSS类来设置样式。

#### 2. JavaScript代码清理
- 从JavaScript代码中完全删除了 `networkChart` 的ECharts初始化和配置代码块。
- 从 `window.resize` 事件监听器中移除了 `networkChart.resize()` 的调用，以避免在调整窗口大小时出现引用错误。

### 总结
这次修改成功地将动态图表替换为静态图片，简化了该部分的内容，并清除了所有相关的JavaScript代码，确保了页面的性能和稳定性。 