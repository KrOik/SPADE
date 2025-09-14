
# 分块索引集成指南

## 1. 文件结构
```
IndexJs/chunks/
├── index_chunk_0.json
├── index_chunk_1.json
├── ...
├── index_metadata.json
└── chunked_loader.js
```

## 2. 在HTML中引入
```html
<script src="./IndexJs/chunks/chunked_loader.js"></script>
```

## 3. 使用方法

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
```

## 4. 性能优化建议

1. **按需加载**: 只加载当前页面需要的块
2. **缓存策略**: 使用浏览器缓存或IndexedDB缓存已加载的块
3. **搜索优化**: 对于大数据集，考虑使用Web Workers进行搜索
4. **预加载**: 预加载下一页可能需要的块

## 5. 错误处理

加载器已内置错误处理，会自动跳过失败的块。建议在应用层面也加入相应的错误处理逻辑。
