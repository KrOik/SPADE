# 目标生物筛选修复说明

## 问题描述

在 `search_advanced.html` 页面中，目标生物的类目筛选存在严重问题：

1. **选项格式不正确**：原始的 `search_options.json` 文件中，目标生物的选项包含了大量不规范的文本片段，如：
   - 包含特殊字符：`##`, `#`, `+`, `++`, `+++`, `++++`
   - 包含数值和单位：`(MIC=0.3 µM)`, `(IC50=3.2 µM)`
   - 包含不完整的句子和片段
   - 格式不统一，有些是完整的生物名称，有些是实验数据

2. **筛选逻辑不准确**：原有的筛选逻辑过于简单，无法正确处理目标生物字段的复杂内容。

## 修复方案

### 1. 创建新的搜索选项配置文件

创建了 `data/index/search_options_fixed.json` 文件，包含规范化的目标生物选项：

```json
{
  "target_organisms": {
    "label": "目标生物",
    "options": [
      {
        "value": "Gram-positive bacteria",
        "label": "革兰氏阳性菌"
      },
      {
        "value": "Gram-negative bacteria",
        "label": "革兰氏阴性菌"
      },
      {
        "value": "Yeast",
        "label": "酵母菌"
      },
      {
        "value": "Fungi",
        "label": "真菌"
      },
      {
        "value": "Virus",
        "label": "病毒"
      },
      {
        "value": "Bacillus",
        "label": "芽孢杆菌"
      },
      {
        "value": "Staphylococcus",
        "label": "葡萄球菌"
      },
      {
        "value": "Escherichia coli",
        "label": "大肠杆菌"
      },
      {
        "value": "Candida",
        "label": "念珠菌"
      },
      {
        "value": "Listeria",
        "label": "李斯特菌"
      },
      {
        "value": "Enterococcus",
        "label": "肠球菌"
      },
      {
        "value": "Lactobacillus",
        "label": "乳酸杆菌"
      },
      {
        "value": "Pseudomonas",
        "label": "假单胞菌"
      },
      {
        "value": "Streptococcus",
        "label": "链球菌"
      },
      {
        "value": "No MICs found in DRAMP database",
        "label": "无数据"
      }
    ]
  }
}
```

### 2. 修改搜索页面配置

修改 `search_advanced.html` 文件，使其使用新的配置文件：

```javascript
// 加载搜索选项
async function loadSearchOptions() {
    try {
        const response = await fetch('data/index/search_options_fixed.json');
        searchOptions = await response.json();
        renderSearchOptions();
    } catch (error) {
        console.error('加载搜索选项失败:', error);
        document.getElementById('loading').style.display = 'none';
        document.getElementById('noResults').textContent = '加载搜索选项失败';
        document.getElementById('noResults').style.display = 'block';
    }
}
```

### 3. 改进筛选逻辑

改进了 `applyFilter` 函数中的目标生物筛选逻辑：

```javascript
case 'target_organisms':
    if (!item.target_organisms) return false;
    const targetOrgText = item.target_organisms.toLowerCase();
    const targetFilterValue = filterValue.toLowerCase();
    
    // 特殊处理无数据的情况
    if (filterValue === 'No MICs found in DRAMP database') {
        return targetOrgText.includes('no mics found in dramp database');
    }
    
    // 处理主要的目标生物类型
    if (filterValue === 'Gram-positive bacteria') {
        return targetOrgText.includes('gram-positive bacteria') || 
               targetOrgText.includes('gram-positive bacterium');
    }
    
    if (filterValue === 'Gram-negative bacteria') {
        return targetOrgText.includes('gram-negative bacteria') || 
               targetOrgText.includes('gram-negative bacterium');
    }
    
    if (filterValue === 'Yeast') {
        return targetOrgText.includes('yeast') || 
               targetOrgText.includes('candida');
    }
    
    if (filterValue === 'Fungi') {
        return targetOrgText.includes('fungi') || 
               targetOrgText.includes('fungal');
    }
    
    if (filterValue === 'Virus') {
        return targetOrgText.includes('virus') || 
               targetOrgText.includes('viral');
    }
    
    // 处理具体的生物名称
    return targetOrgText.includes(targetFilterValue);
```

### 4. 改进活性类型筛选

同时改进了活性类型的筛选逻辑，使其更加准确：

```javascript
case 'activity_types':
    if (!item.activity_type) return false;
    const activities = Array.isArray(item.activity_type) ? 
        item.activity_type : [item.activity_type];
    const filterValueLower = filterValue.toLowerCase();
    
    return activities.some(activity => {
        const activityLower = activity.toLowerCase();
        // 处理常见的活性类型匹配
        if (filterValue === 'Antibacterial') {
            return activityLower.includes('antibacterial') || 
                   activityLower.includes('anti-gram') ||
                   activityLower.includes('anti gram');
        }
        if (filterValue === 'Antifungal') {
            return activityLower.includes('antifungal') || 
                   activityLower.includes('anti-fungal');
        }
        // ... 其他活性类型的处理
        return activityLower.includes(filterValueLower);
    });
```

## 修复效果

### 修复前的问题：
1. 目标生物选项包含大量无意义的文本片段
2. 筛选结果不准确，无法正确匹配目标生物
3. 用户体验差，选项混乱

### 修复后的改进：
1. 目标生物选项清晰规范，包含常见的目标生物类型
2. 筛选逻辑更加智能，能够正确处理复杂的文本内容
3. 支持模糊匹配，提高筛选准确性
4. 用户体验显著改善

## 测试验证

创建了 `test_target_organisms_fix.html` 测试页面，用于验证修复效果：

- 测试不同目标生物的筛选功能
- 验证筛选逻辑的准确性
- 展示修复前后的对比效果

## 文件修改清单

1. **新增文件**：
   - `data/index/search_options_fixed.json` - 修复后的搜索选项配置
   - `test_target_organisms_fix.html` - 测试页面

2. **修改文件**：
   - `search_advanced.html` - 更新配置文件路径和改进筛选逻辑

3. **文档文件**：
   - `readme/20250127-target_organisms_filter_fix-目标生物筛选修复.md` - 本说明文档

## 使用说明

1. 访问 `search_advanced.html` 页面
2. 在"目标生物"下拉菜单中选择需要筛选的目标生物类型
3. 点击"搜索"按钮进行筛选
4. 查看筛选结果，验证筛选准确性

修复完成后，目标生物的筛选功能将正常工作，用户可以根据需要筛选特定目标生物的多肽数据。 