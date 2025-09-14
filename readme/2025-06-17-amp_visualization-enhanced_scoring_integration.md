# SPADE 增强评分系统集成说明

**修改时间**: 2025-06-17  
**修改文件**: amp_visualization.html, program/enhanced_scoring.py, program/run_enhanced_scoring.py  
**改动内容**: 集成新的5维度评分系统到可视化页面

## 📊 评分系统升级概述

### 新评分维度 (5个维度)
1. **效力 (Efficacy)** - 35%权重
   - 基于MIC预测和实验数据
   - 考虑净电荷、疏水性、长度因子
   
2. **选择性 (Selectivity)** - 25%权重
   - 溶血活性评估
   - 细胞毒性分析
   - 电荷和多样性奖励
   
3. **稳定性 (Stability)** - 20%权重
   - 二硫键分析
   - 脯氨酸和甘氨酸影响
   - pH和热稳定性
   
4. **合成难度 (Synthesis)** - 12%权重
   - 序列长度评估
   - 稀有氨基酸惩罚
   - 重复性和复杂性
   
5. **新颖性 (Novelty)** - 8%权重
   - 序列相似性分析
   - 功能多样性
   - 组成熵计算

## 🎨 可视化页面新增功能

### 1. 详细评分分析卡片
- **功能**: 展示每个维度的详细计算过程
- **内容**: 
  - 原始分数和加权分数
  - 权重百分比显示
  - 具体影响因子分析
- **样式**: 响应式网格布局，颜色编码评分等级

### 2. 评分特征卡片
- **功能**: 显示氨基酸组成和物理化学性质
- **分组显示**:
  - 氨基酸组成: 疏水性、亲水性、电荷、芳香族等
  - 物理性质: 净电荷、疏水性、两亲性、柔韧性等
- **数据格式**: 自动百分比转换，数值精度控制

### 3. 增强肽信息卡片
- **新增信息**:
  - 总体评分和类别
  - 净电荷和疏水性
  - 二硫键潜力
- **布局优化**: 分组显示基本信息和评分摘要

### 4. 改进的图表系统
- **雷达图**: 5维度评分可视化
- **条形图**: 加权评分对比
- **仪表图**: 总体评分显示

## 🔧 技术实现细节

### 数据结构适配
```json
{
  "total": 7.86,
  "category": "Good",
  "scores": {
    "efficacy": 9.0,
    "selectivity": 7.0,
    "stability": 6.5,
    "synthesis": 7.2,
    "novelty": 10.0
  },
  "weighted_scores": {
    "efficacy": 3.15,
    "selectivity": 1.75,
    "stability": 1.3,
    "synthesis": 0.86,
    "novelty": 0.8
  },
  "features": {
    "hydrophobic_ratio": 0.32,
    "net_charge": 1,
    "cysteine_count": 3,
    // ... 更多特征
  },
  "details": {
    "efficacy": {
      "predicted_score": 9.0,
      "charge_score": 8.0,
      // ... 详细分析
    }
    // ... 其他维度详情
  }
}
```

### CSS样式系统
- **模块化设计**: 每个新功能独立样式模块
- **响应式布局**: 移动端适配
- **颜色编码**: 评分等级视觉区分
- **动画效果**: 悬停和交互反馈

### 多语言支持
- **新增翻译**: 5个评分维度和特征术语
- **语言覆盖**: 英文、简体中文、繁体中文
- **动态切换**: 实时语言切换功能

## 📁 文件修改清单

### 主要修改文件
1. **amp_visualization.html**
   - 新增 `createDetailedScoringAnalysisCard()` 函数
   - 新增 `createScoringFeaturesCard()` 函数
   - 增强 `createPeptideInfoCard()` 函数
   - 添加相应CSS样式和翻译

2. **program/enhanced_scoring.py**
   - 完整的5维度评分系统
   - 实验数据整合
   - 详细分析输出

3. **program/run_enhanced_scoring.py**
   - 批量评分处理脚本
   - 进度显示和错误处理

### 新增文件
1. **test_visualization.html** - 测试页面
2. **program/test_scoring.py** - 测试评分脚本

## 🧪 测试验证

### 测试样本
- SPADE_N_00001: 总分 7.86 (Good)
- SPADE_N_00002: 总分 7.97 (Good)  
- SPADE_N_00003: 总分 8.44 (Good)
- SPADE_UN_00001: 总分 8.01 (Good)

### 测试要点
1. ✅ 新评分卡片正确显示
2. ✅ 5维度雷达图渲染
3. ✅ 特征数据格式化
4. ✅ 多语言切换功能
5. ✅ 响应式设计适配

## 🚀 使用方法

### 运行评分系统
```bash
cd program
python run_enhanced_scoring.py
```

### 查看可视化结果
```
amp_visualization.html?id=SPADE_N_00001
```

### 测试页面
```
test_visualization.html
```

## 📈 性能优化

1. **数据查找优化**: 使用 `DataFinder` 类提高查找效率
2. **并行渲染**: 图表异步加载
3. **缓存机制**: 翻译和数据缓存
4. **响应式加载**: 按需加载组件

## 🔮 未来扩展

1. **实时评分**: WebSocket实时更新
2. **批量对比**: 多肽评分对比功能
3. **导出功能**: PDF/PNG报告导出
4. **高级筛选**: 基于评分维度的筛选器
5. **机器学习**: 评分模型持续优化

---

**注意**: 此次更新完全向后兼容，旧的评分数据仍可正常显示，新功能仅在新评分数据存在时激活。 