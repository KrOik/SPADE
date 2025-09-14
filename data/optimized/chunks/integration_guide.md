
# 分块索引集成指南

## 1. 文件结构
```
chunks/
├── index_chunk_0.json
├── index_chunk_1.json
├── ...
├── index_metadata.json
└── chunked_loader.js
```

## 2. 在HTML中引入
```html
<script src="./chunks/chunked_loader.js"></script>
```

## 3. 使用方法

### 初始化
```javascript
// 初始化加载器并获取元数据
await window.chunkedIndexLoader.init();
```

### 加载单个块
```javascript
const chunk = await window.chunkedIndexLoader.loadChunk(0);
```

### 加载所有数据（适用于小数据集）
```javascript
const allData = await window.chunkedIndexLoader.loadAllChunks();
```

### 搜索功能
```javascript
// 按名称搜索
const results = await window.chunkedIndexLoader.searchInChunks('keyword', 'name');

// 按序列搜索
const results = await window.chunkedIndexLoader.searchInChunks('ACDE', 'sequence');

// 按ID精确查找
const entry = await window.chunkedIndexLoader.getEntryById('SPADE_N_00001');
```

## 4. 性能优化建议

1. **按需加载**: 只加载当前页面需要的块
2. **缓存策略**: 使用浏览器缓存或IndexedDB缓存已加载的块
3. **搜索优化**: 对于大数据集，考虑使用Web Workers进行搜索
4. **预加载**: 预加载下一页可能需要的块

## 5. 错误处理

加载器已内置错误处理，会自动跳过失败的块。建议在应用层面也加入相应的错误处理逻辑。

## 6. 数据结构说明

### 基础数据文件 (basic/SPADE_N_00001.json)
```json
{
  "SPADE_N_00001": {
    "basic": {
      "SPADE ID": "SPADE_N_00001",
      "Peptide Name": "Variacin (Bacteriocin)",
      "Sequence": "GSGVIPTISHECHMNSFQFVFTCCS",
      "Source": "Micrococcus varians (Gram-positive bacteria)",
      "Biological Activity": ["Antimicrobial", "Antibacterial", "Anti-Gram+"],
      "Target Organism": "Gram-positive bacteria...",
      "Linear/Cyclic": "Linear",
      "Sequence Length": 25
    },
    "extended_data_url": "SPADE_N_00001_extended.json"
  }
}
```

### 扩展数据文件 (extended/SPADE_N_00001_extended.json)
包含完整的肽数据信息，与原始数据结构相同。

### 索引块文件 (chunks/index_chunk_0.json)
```json
[
  {
    "id": "SPADE_N_00001",
    "name": "Variacin (Bacteriocin)",
    "sequence": "GSGVIPTISHECHMNSFQFVFTCCS",
    "length": 25,
    "activity": ["Antimicrobial", "Antibacterial", "Anti-Gram+"]
  },
  ...
]
```

### 元数据文件 (chunks/index_metadata.json)
```json
{
  "total_entries": 1000,
  "chunk_size": 100,
  "total_chunks": 10,
  "created_at": "2023-06-01 12:00:00",
  "chunks": ["index_chunk_0.json", ...]
}
```
