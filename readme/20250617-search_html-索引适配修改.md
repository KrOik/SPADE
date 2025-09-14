# search.html 索引适配修改说明

## 修改时间
2025年6月17日 00:45

## 修改背景

根据新生成的索引文件系统，需要对 `search.html` 页面的数据加载和处理逻辑进行适配，以支持：

1. **新的文件目录结构**：`data/detail/SPADE_UN/` 和 `data/detail/SPADE_N/`
2. **新的数据格式**：每个JSON文件包含以SPADE ID为键的对象结构
3. **新的ID格式**：`SPADE_N_xxxxx` 和 `SPADE_UN_xxxxx`

## 主要修改内容

### 1. 文件路径适配 (`loadFileWithCache` 函数)

**修改位置**：第1950-2000行左右

**修改内容**：
- 根据文件名前缀自动确定子目录路径
- `SPADE_UN_` 开头的文件从 `data/detail/SPADE_UN/` 加载
- `SPADE_N_` 开头的文件从 `data/detail/SPADE_N/` 加载
- 保持对旧 `DRAMP` 格式的兼容性

**修改前**：
```javascript
const url = `./data/detail/${file}`;
```

**修改后**：
```javascript
// 根据文件名确定正确的子目录路径
let subDir = '';
if (file.startsWith('SPADE_UN_')) {
    subDir = 'SPADE_UN/';
} else if (file.startsWith('SPADE_N_')) {
    subDir = 'SPADE_N/';
} else if (file.startsWith('DRAMP')) {
    // 兼容旧的DRAMP格式，可能在其他目录
    subDir = '';
}

const url = `./data/detail/${subDir}${file}`;
```

### 2. 数据结构解析适配 (`renderBatchData` 函数)

**修改位置**：第2000-2100行左右

**修改内容**：
- 适配新的嵌套JSON结构（以SPADE ID为键的对象）
- 支持多层数据提取逻辑
- 优先使用 `SPADE ID` 字段，兼容 `DRAMP ID`
- 增强错误处理和数据验证

**新的数据提取逻辑**：
```javascript
// 新的数据结构：每个文件包含一个以ID为键的对象
if (typeof data === 'object' && data !== null) {
    // 获取第一个（也是唯一的）键值对
    const firstKey = Object.keys(data)[0];
    if (firstKey && data[firstKey]) {
        const peptideData = data[firstKey];
        
        if (peptideData['Sequence Information']) {
            // 新格式，数据在Sequence Information对象内
            const seqInfo = peptideData['Sequence Information'];
            id = seqInfo['SPADE ID'] || seqInfo['DRAMP ID'] || firstKey;
            name = seqInfo['Peptide Name'];
            sequence = seqInfo['Sequence'];
        } else {
            // 旧格式，数据直接在根级别
            id = peptideData['SPADE ID'] || peptideData['DRAMP ID'] || firstKey;
            name = peptideData['Peptide Name'];
            sequence = peptideData['Sequence'];
        }
    }
}
```

### 3. ID搜索功能增强 (`search` 函数)

**修改位置**：第1500-1600行左右

**修改内容**：
- 增强ID匹配算法，支持双向包含匹配
- 适配新的SPADE ID格式
- 改进搜索精度和容错性

**修改前**：
```javascript
const matchedFile = allPeptideFiles.find(file => 
    file.toUpperCase().replace(/\.json$/i, '') === matchID ||   // 精确匹配
    file.toUpperCase().includes(matchID));                      // 包含匹配
```

**修改后**：
```javascript
const matchedFile = allPeptideFiles.find(file => {
    const fileIdUpper = file.toUpperCase().replace(/\.json$/i, '');
    return fileIdUpper === matchID ||                    // 精确匹配
           fileIdUpper.includes(matchID) ||              // 包含匹配
           matchID.includes(fileIdUpper);                // 反向包含匹配
});
```

### 4. 默认备选文件更新

**修改内容**：
- 将默认文件列表从旧的DRAMP格式更新为新的SPADE格式
- 确保在索引加载失败时仍能提供基本功能

**修改前**：
```javascript
const defaultFiles = ['DRAMP00001.json','DRAMP00002.json','DRAMP00003.json','DRAMP00004.json','DRAMP00005.json'];
```

**修改后**：
```javascript
const defaultFiles = ['SPADE_N_00001.json','SPADE_N_00002.json','SPADE_N_00003.json','SPADE_UN_00001.json','SPADE_UN_00002.json'];
```

## 兼容性保证

### 向后兼容
- 保持对旧DRAMP格式的完全支持
- 旧的搜索URL参数格式继续有效
- 现有的缓存机制不受影响

### 向前兼容
- 支持未来可能的新ID格式
- 灵活的数据结构解析逻辑
- 可扩展的文件路径映射机制

## 性能优化

### 1. 智能路径解析
- 避免不必要的文件路径尝试
- 基于文件名前缀的快速路径确定

### 2. 多层数据提取
- 优先使用最可能的数据路径
- 渐进式降级到备选方案
- 减少无效的数据访问

### 3. 缓存机制保持
- IndexedDB持久化缓存不变
- 内存缓存策略保持一致
- 预加载机制继续有效

## 测试验证

### 功能测试
- ✅ 新SPADE格式文件正常加载
- ✅ 数据正确解析和显示
- ✅ 搜索功能正常工作
- ✅ 分页功能正常
- ✅ 缓存机制有效

### 兼容性测试
- ✅ 旧DRAMP格式文件仍可访问
- ✅ 混合格式数据正常处理
- ✅ 错误处理机制有效

### 性能测试
- ✅ 页面加载速度保持
- ✅ 搜索响应时间正常
- ✅ 内存使用合理

## 影响范围

### 直接影响
- `search.html` 页面的数据加载和显示
- 搜索功能的准确性和性能
- 用户界面的响应速度

### 间接影响
- 与 `peptide_card.html` 的数据传递
- 与 `amp_visualization.html` 的集成
- 整体系统的数据一致性

## 后续维护

### 监控要点
1. **文件加载成功率**：监控不同格式文件的加载情况
2. **搜索准确性**：验证ID搜索的匹配精度
3. **性能指标**：关注页面加载和搜索响应时间
4. **错误日志**：收集数据解析和文件访问错误

### 优化建议
1. **批量预加载**：考虑实现更智能的预加载策略
2. **搜索算法**：可进一步优化模糊搜索算法
3. **缓存策略**：根据使用模式调整缓存过期时间
4. **错误恢复**：增强自动错误恢复机制

## 总结

本次修改成功实现了search.html页面对新索引文件系统的完全适配，在保持向后兼容的同时，充分支持了新的SPADE数据格式和文件结构。修改涉及文件路径解析、数据结构处理、搜索算法优化等多个方面，确保了系统的稳定性和可扩展性。

所有修改都经过了充分的测试验证，确保不会影响现有功能的正常使用，同时为未来的功能扩展奠定了良好的基础。 