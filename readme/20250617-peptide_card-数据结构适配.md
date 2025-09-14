# peptide_card.html 数据结构适配修改说明

## 修改时间
2025年6月17日 01:15

## 修改背景

根据新生成的SPADE数据结构，需要对 `peptide_card.html` 页面进行适配，以支持：

1. **新的SPADE ID格式**：`SPADE_N_xxxxx` 和 `SPADE_UN_xxxxx`
2. **新的文件目录结构**：`data/detail/SPADE_N/` 和 `data/detail/SPADE_UN/`
3. **新增字段**：相似序列、频繁氨基酸、正负电荷残基等
4. **相似抗菌肽功能**：显示相似度、序列信息和跳转链接

## 主要修改内容

### 1. URL参数解析适配

**修改位置**：`getPeptideIdFromUrl()` 函数

**修改内容**：
- 添加对新SPADE ID格式的支持
- 扩展参数名列表：`['DRAMP ID', 'DRAMP_ID', 'SPADE ID', 'SPADE_ID', 'id', 'peptideId', 'DRAMP_OTD']`
- 支持解析 `SPADE_N_00001` 和 `SPADE_UN_00001` 格式

### 2. 文件路径构建逻辑

**修改位置**：`initializeApplication()` 函数

**修改内容**：
```javascript
// 根据peptideId格式确定正确的文件路径
let dataUrl;
if (peptideId.startsWith('SPADE_UN_')) {
    dataUrl = `./data/detail/SPADE_UN/${peptideId}.json`;
} else if (peptideId.startsWith('SPADE_N_')) {
    dataUrl = `./data/detail/SPADE_N/${peptideId}.json`;
} else {
    // 兼容旧的DRAMP格式
    dataUrl = `./data/detail/${peptideId}.json`;
}
```

### 3. 模块配置更新

**修改位置**：`renderPeptide()` 函数中的 `modules` 数组

**新增模块**：
- 添加 `Similar Sequences` 模块，专门显示相似抗菌肽信息

**字段更新**：
- 在 `General Information` 中添加 `SPADE ID` 字段
- 在 `Physico-Chemical Properties` 中添加新字段：
  - `Frequent Amino Acids`（常见氨基酸）
  - `Positive Residues`（正电荷残基）
  - `Negative Residues`（负电荷残基）

### 4. 相似序列显示功能

**新增功能**：完整的相似抗菌肽显示系统

**功能特点**：
- **相似度可视化**：用颜色编码显示相似度百分比
  - 绿色：≥90% 高相似度
  - 蓝色：≥70% 中等相似度
  - 黄色：<70% 低相似度
- **序列对比**：显示完整的氨基酸序列
- **跳转功能**：点击"View Details"按钮跳转到相似肽的详情页
- **响应式设计**：移动端优化显示

**实现代码**：
```javascript
// 特殊处理相似序列字段
else if (field === 'Similar Sequences' && value && Array.isArray(value)) {
    // 创建相似序列列表
    // 显示SPADE ID、相似度、序列
    // 添加跳转按钮
}
```

### 5. 侧边栏导航更新

**修改位置**：HTML侧边栏导航

**新增导航项**：
```html
<li>
    <a href="#similar">
        <span class="icon"><i class="fas fa-search-plus"></i></span>
        <span class="text">Similar Sequences</span>
    </a>
</li>
```

### 6. CSS样式系统

**新增样式类**：
- `.similar-sequences-list`：相似序列列表容器
- `.similar-sequence-item`：单个相似序列项
- `.similar-seq-id`：SPADE ID显示
- `.similarity-score`：相似度标签
- `.similar-sequence`：序列显示
- `.view-similar-btn`：查看详情按钮

**设计特点**：
- 现代卡片式设计
- 悬停动画效果
- 渐变色彩方案
- 移动端响应式适配

### 7. 多语言支持

**新增翻译条目**：
- `Similar Sequences`：相似序列
- `View Details`：查看详情
- `SPADE ID`：SPADE编号
- `Frequent Amino Acids`：常见氨基酸
- `Positive Residues`：正电荷残基
- `Negative Residues`：负电荷残基

**支持语言**：
- 简体中文
- 繁体中文
- 其他语言保持英文

## 技术特点

### 1. 向后兼容性
- 完全支持旧的DRAMP格式数据
- 自动检测ID格式并选择正确的文件路径
- 保持原有功能不变

### 2. 性能优化
- 使用文档片段批量DOM操作
- 智能字段验证，跳过无效数据
- 缓存系统支持新格式

### 3. 用户体验
- 直观的相似度可视化
- 一键跳转到相似肽
- 响应式设计适配各种设备
- 平滑的动画过渡效果

### 4. 数据处理
- 智能字段映射和查找
- 支持嵌套数据结构
- 自动处理数据类型转换

## 测试建议

1. **URL参数测试**：
   - 测试 `?SPADE ID=SPADE_N_00001`
   - 测试 `?SPADE ID=SPADE_UN_00001`
   - 测试旧格式兼容性

2. **相似序列功能测试**：
   - 验证相似度显示正确性
   - 测试跳转链接功能
   - 检查移动端显示效果

3. **多语言测试**：
   - 验证新字段翻译
   - 检查序列不被翻译
   - 测试语言切换功能

## 数据格式支持

**支持的数据结构**：
```json
{
  "SPADE_N_00001": {
    "Sequence Information": {
      "SPADE ID": "SPADE_N_00001",
      "Similar Sequences": [
        {
          "SPADE_ID": "SPADE_N_06161",
          "Similarity": 1.0,
          "Sequence": "MTNAFQALDEVTDAELDAILGGGSGVIPTISHECHMNSFQFVFTCCS"
        }
      ],
      "Frequent Amino Acids": "SCF",
      "Positive Residues": 2,
      "Negative Residues": 1
    }
  }
}
```

这次修改确保了peptide_card.html页面能够完美适配新的SPADE数据结构，同时保持了良好的用户体验和向后兼容性。 