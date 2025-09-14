# SPADE 数据优化指南

本文档提供了 SPADE 数据库优化的详细说明，包括数据结构优化、分块加载策略以及使用方法。

## 1. 优化背景

原始 SPADE 数据库存在以下问题：

- **数据冗余**：每个肽数据文件包含大量可能不会立即使用的信息
- **文件过多**：大量独立的 JSON 文件导致 HTTP 请求过多
- **索引文件过大**：单一的大型索引文件（`peptide_index.json`）加载缓慢
- **分块加载不足**：现有的分块策略未充分优化

## 2. 优化方案

### 2.1 数据分离策略

将肽数据分为两部分：

- **基础数据**：包含最常用的字段（ID、名称、序列、活性等）
- **扩展数据**：包含完整的详细信息

### 2.2 分块索引优化

- 增加分块数量，减小每个块的大小
- 优化索引结构，仅包含必要字段
- 提供高效的块加载和搜索机制

### 2.3 延迟加载策略

- 首先加载基础数据和索引
- 仅在用户请求时加载扩展数据

## 3. 使用方法

### 3.1 数据优化处理

运行以下命令生成优化后的数据：

```bash
python program/optimize_data.py --input data/detail --output data/optimized --workers 4 --chunk-size 1000
```

参数说明：
- `--input`：原始数据目录
- `--output`：优化后数据输出目录
- `--workers`：并行处理线程数
- `--chunk-size`：索引分块大小

### 3.2 优化后的数据结构

```
data/optimized/
├── basic/                # 基础数据
│   ├── SPADE_N_00001.json
│   ├── SPADE_N_00002.json
│   └── ...
├── extended/            # 扩展数据
│   ├── SPADE_N_00001_extended.json
│   ├── SPADE_N_00002_extended.json
│   └── ...
└── chunks/              # 分块索引
    ├── index_chunk_0.json
    ├── index_chunk_1.json
    ├── ...
    ├── index_metadata.json
    ├── chunked_loader.js
    └── integration_guide.md
```

### 3.3 演示页面

提供了一个演示页面 `optimized_loader_demo.html` 用于展示优化后的数据加载效果：

1. 启动本地服务器：
   ```bash
   python -m http.server 8000
   ```

2. 在浏览器中访问：
   ```
   http://localhost:8000/optimized_loader_demo.html
   ```

3. 演示页面功能：
   - 肽搜索（按名称、序列或ID）
   - 肽详情查看（基础数据和扩展数据）
   - 性能测试（加载时间、搜索速度）

## 4. 前端集成指南

### 4.1 引入分块加载器

```html
<script src="./data/optimized/chunks/chunked_loader.js"></script>
```

### 4.2 初始化加载器

```javascript
// 初始化加载器
const chunkedIndexLoader = window.chunkedIndexLoader;
await chunkedIndexLoader.init();
```

### 4.3 使用示例

```javascript
// 搜索肽
const results = await chunkedIndexLoader.searchInChunks('antimicrobial', 'name');

// 按ID查找
const peptide = await chunkedIndexLoader.getEntryById('SPADE_N_00001');

// 加载基础数据
const response = await fetch(`./data/optimized/basic/${peptideId}.json`);
const basicData = await response.json();

// 加载扩展数据
const extendedUrl = basicData[peptideId].extended_data_url;
const extendedResponse = await fetch(`./data/optimized/extended/${extendedUrl}`);
const extendedData = await extendedResponse.json();
```

## 5. 性能优化建议

### 5.1 缓存策略

- 使用浏览器缓存（设置适当的 Cache-Control 头）
- 实现 IndexedDB 本地缓存
- 使用 Service Worker 缓存静态资源

### 5.2 预加载策略

- 预加载第一个索引块
- 根据用户行为预测并预加载可能需要的数据

### 5.3 压缩策略

- 启用服务器端 Gzip/Brotli 压缩
- 考虑使用二进制格式（如 MessagePack）代替 JSON

## 6. 进一步优化方向

### 6.1 数据库方案

考虑使用 NEON 数据库或其他数据库解决方案，优势包括：

- 更高效的查询性能
- 更好的数据组织和索引
- 减少前端数据处理负担
- 更好的扩展性

### 6.2 API 层优化

- 实现 GraphQL API 按需获取数据
- 添加数据聚合和过滤端点
- 实现高级搜索功能

## 7. 结论

通过数据分离、分块索引和延迟加载策略，可以显著提高 SPADE 数据库的加载性能和用户体验。演示页面展示了这些优化的效果，可以根据实际需求进一步调整和优化。