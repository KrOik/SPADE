# AMP Visualization 数据加载分析：Amino Acid Frequency Analysis 和 Target Organism Activity

## 概述

本文档详细分析了 `amp_visualization.html` 中两个关键功能模块的数据加载方法和数据结构：
- **Amino Acid Frequency Analysis（氨基酸频率分析）**
- **Target Organism Activity（目标生物活性）**

## 1. Target Organism Activity（目标生物活性）

### 1.1 数据来源

```javascript
// 主要数据提取位置（第2013行）
const targetOrganisms = findValueInObject(data, "target_organisms") || {};
```

### 1.2 数据结构期望格式

```json
{
  "target_organisms": {
    "Antibacterial": [
      {
        "name": "E. coli",
        "activity": "+++"
      },
      {
        "name": "S. aureus", 
        "activity": "MIC: 2.5 μg/ml"
      }
    ],
    "Antifungal": [
      {
        "name": "C. albicans",
        "activity": "++"
      }
    ],
    "Note": [
      {
        "name": "Additional notes about activity"
      }
    ]
  }
}
```

### 1.3 数据处理逻辑

#### 1.3.1 空数据处理
```javascript
// 检查是否为空对象或没有有效数据
if (!targetOrganisms || Object.keys(targetOrganisms).length === 0) {
    // 显示"数据不可用"提示
    return;
}
```

#### 1.3.2 活性数据格式识别

代码支持多种活性数据格式：

1. **加号模式（+号越多活性越强）**
   ```javascript
   if (org.activity.includes('+')) {
       activityLevel = getActivityLevel(org.activity);
       // 渲染彩色圆点指示器
   }
   ```

2. **MIC值格式**
   ```javascript
   else if (org.activity.toLowerCase().includes('mic') || 
            org.activity.includes('μg/ml') || 
            org.activity.includes('ug/ml')) {
       // 特殊样式显示MIC值
   }
   ```

3. **其他格式**
   ```javascript
   else {
       // 普通文本显示
   }
   ```

#### 1.3.3 活性等级可视化

```javascript
// 活性等级计算
function getActivityLevel(activity) {
    const plusCount = (activity.match(/\+/g) || []).length;
    return plusCount;
}

// 颜色编码
// 1个+: 黄色 (#FFC107)
// 2个+: 蓝色 (#2196F3) 
// 3个+及以上: 绿色 (#4CAF50)
```

### 1.4 表格渲染

遍历每个类别（category）和生物体（organisms），生成HTML表格：

```javascript
for (const [category, organisms] of Object.entries(targetOrganisms)) {
    // 跳过Note类别的特殊处理
    if (category === 'Note') continue;
    
    // 为每个类别创建表格
    organisms.forEach(org => {
        // 处理活性数据并生成表格行
    });
}
```

## 2. Amino Acid Frequency Analysis（氨基酸频率分析）

### 2.1 序列数据获取策略

代码使用**多层级回退策略**获取序列数据：

#### 2.1.1 优先级1：detail数据
```javascript
if (data._detailData) {
    sequence = findValueInObject(data._detailData, "Sequence") || 
              findValueInObject(data._detailData, "sequence") || 
              findValueInObject(data._detailData, "seq") || "";
}
```

#### 2.1.2 优先级2：主数据
```javascript
if (!sequence) {
    sequence = findValueInObject(data, "Sequence") || 
              findValueInObject(data, "sequence") || 
              findValueInObject(data, "seq") || "";
}
```

#### 2.1.3 优先级3：序列信息对象
```javascript
if (!sequence) {
    const sequenceInfo = findValueInObject(data, "Sequence Information");
    if (sequenceInfo) {
        sequence = findValueInObject(sequenceInfo, "Sequence") || 
                  findValueInObject(sequenceInfo, "sequence") || "";
    }
}
```

#### 2.1.4 备用验证：features长度检查
```javascript
if (!sequence) {
    const features = findValueInObject(data, "features") || {};
    const sequenceLength = features.length || features.sequence_length;
    
    if (sequenceLength && sequenceLength > 0) {
        // 显示"检测到序列长度但序列数据未加载"提示
    }
}
```

### 2.2 detail数据加载机制

当主数据中没有序列时，系统会尝试从detail目录加载：

#### 2.2.1 智能路径识别
```javascript
function determineDataPath(peptideId) {
    const upperPeptideId = peptideId.toUpperCase();
    
    if (upperPeptideId.startsWith('SPADE_UN_')) {
        return [
            `data/detail/SPADE_UN/${peptideId}.json`,
            `data/detail/SPADE_UN/${upperPeptideId}.json`,
            `data/detail/${peptideId}.json`
        ];
    } else if (upperPeptideId.startsWith('SPADE_N_')) {
        return [
            `data/detail/SPADE_N/${peptideId}.json`,
            `data/detail/SPADE_N/${upperPeptideId}.json`,
            `data/detail/${peptideId}.json`
        ];
    } else {
        // 通用路径，支持所有可能的位置
        return [
            `data/detail/${peptideId}.json`,
            `data/detail/SPADE_N/${peptideId}.json`,
            `data/detail/SPADE_UN/${peptideId}.json`,
            // ... 更多路径
        ];
    }
}
```

#### 2.2.2 带缓存的数据加载
```javascript
async function loadDataWithCache(url) {
    if (dataCache.has(url)) {
        return dataCache.get(url);
    }
    
    const data = await loadData(url);
    dataCache.set(url, data);
    
    // 限制缓存大小（最多10个文件）
    if (dataCache.size > 10) {
        const firstKey = dataCache.keys().next().value;
        dataCache.delete(firstKey);
    }
    
    return data;
}
```

### 2.3 氨基酸频率计算

#### 2.3.1 初始化计数器
```javascript
const aminoAcidCounts = {};
const aminoAcids = 'ACDEFGHIKLMNPQRSTVWY'.split('');

// 初始化所有氨基酸计数为0
aminoAcids.forEach(aa => {
    aminoAcidCounts[aa] = 0;
});
```

#### 2.3.2 序列分析
```javascript
// 计算每种氨基酸在序列中的数量
for (let i = 0; i < sequence.length; i++) {
    const aa = sequence[i].toUpperCase();
    if (aminoAcidCounts.hasOwnProperty(aa)) {
        aminoAcidCounts[aa]++;
    }
}

// 计算频率（百分比）
const aminoAcidFrequencies = {};
aminoAcids.forEach(aa => {
    aminoAcidFrequencies[aa] = (aminoAcidCounts[aa] / sequence.length) * 100;
});
```

#### 2.3.3 可视化配置
```javascript
// 定义氨基酸颜色映射
const aaColors = {
    'A': '#FF5252', 'C': '#FF9800', 'D': '#FFEB3B', 'E': '#8BC34A', 
    'F': '#4CAF50', 'G': '#009688', 'H': '#00BCD4', 'I': '#03A9F4', 
    'K': '#3F51B5', 'L': '#673AB7', 'M': '#9C27B0', 'N': '#E91E63', 
    'P': '#F44336', 'Q': '#FF5722', 'R': '#FFC107', 'S': '#8BC34A', 
    'T': '#4CAF50', 'V': '#009688', 'W': '#00BCD4', 'Y': '#2196F3'
};

// Chart.js条形图配置
new Chart(ctx, {
    type: 'bar',
    data: {
        labels: aminoAcids,
        datasets: [{
            data: aminoAcids.map(aa => aminoAcidFrequencies[aa]),
            backgroundColor: aminoAcids.map(aa => aaColors[aa]),
            borderRadius: 5
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        // ... 详细配置
    }
});
```

## 3. 数据查找辅助机制

### 3.1 高效数据查找器
代码使用了专门的 `DataFinder` 类来优化数据查找：

```javascript
class DataFinder {
    constructor(data) {
        this.data = data;
        this.cache = new Map();
        this.pathCache = new Map();
        this.initializeFieldMap();
    }
    
    // 预计算字段路径，建立映射表
    initializeFieldMap() {
        this.fieldPaths = new Map();
        this.flattenData(this.data, []);
    }
    
    // 高效查找字段值，支持缓存
    findValue(targetKey) {
        if (this.cache.has(targetKey)) {
            return this.cache.get(targetKey);
        }
        // ... 查找逻辑
    }
}
```

### 3.2 兼容性查找函数
```javascript
function findValueInObject(data, targetKey) {
    if (!globalDataFinder || globalDataFinder.data !== data) {
        globalDataFinder = new DataFinder(data);
    }
    return globalDataFinder.findValue(targetKey);
}
```

## 4. 错误处理和用户体验

### 4.1 加载状态指示
两个功能都提供了加载状态指示：

```javascript
card.innerHTML = `
    <h3>${title}</h3>
    <div class="loading-indicator">
        <i class="fas fa-spinner fa-spin"></i>
        <p>${loadingText}</p>
    </div>
`;
```

### 4.2 数据缺失处理
- **目标生物活性**：显示"数据不可用"并提示可能在其他部分有数据
- **氨基酸频率**：显示"序列数据不可用"并尝试从detail数据加载

### 4.3 多语言支持
两个功能都集成了多语言翻译系统，支持动态语言切换。

## 5. 性能优化

### 5.1 分阶段加载
- **阶段1**：立即创建核心卡片（包括这两个功能）
- **阶段2**：延迟加载需要额外数据的卡片

### 5.2 缓存机制
- 数据缓存：`dataCache` Map，最多缓存10个文件
- 字段查找缓存：`DataFinder` 类内部缓存机制

### 5.3 并行处理
使用 `Promise.allSettled()` 并行处理多个异步卡片的加载。

## 6. 总结

这两个功能模块展现了良好的软件设计实践：

1. **容错性**：多层级数据获取策略，优雅的错误处理
2. **性能**：缓存机制、分阶段加载、高效数据查找
3. **用户体验**：加载指示器、多语言支持、直观的数据可视化
4. **维护性**：模块化设计、清晰的数据流、完善的日志记录

主要数据文件位置：
- 主数据：`data/result/scored_${peptideId}.json`
- 详细数据：`data/detail/SPADE_N/${peptideId}.json` 或 `data/detail/SPADE_UN/${peptideId}.json` 