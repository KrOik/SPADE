# 抗菌肽索引生成处理说明

## 处理时间
2025年6月17日 00:34

## 项目需求分析

### search.html 页面索引加载规则
通过分析 `search.html` 页面代码，确定了以下索引数据要求：

1. **索引文件路径**：`data/index/peptide_index.json`
2. **数据格式**：JSON数组，每个条目包含：
   - `id`: 抗菌肽唯一标识符
   - `name`: 抗菌肽名称
   - `sequence`: 氨基酸序列
   - `length`: 序列长度
3. **分页要求**：每页显示15条数据
4. **搜索支持**：
   - ID搜索：精确匹配或包含匹配
   - 名称搜索：不区分大小写的包含匹配
   - 序列搜索：不区分大小写的包含匹配
   - 长度范围搜索：指定最小-最大长度范围

## 索引生成脚本

### 脚本功能
创建了 `program/generate_index.py` 脚本，主要功能包括：

1. **数据提取**：从 `data/detail` 目录读取拆分后的JSON文件
2. **信息解析**：提取每个抗菌肽的关键索引信息
3. **完整索引生成**：生成包含所有条目的完整索引文件
4. **分页索引生成**：按每页15条数据分页，生成分页索引文件
5. **统计信息生成**：生成数据统计报告

### 数据处理逻辑

#### 输入数据结构
- 输入目录：`data/detail/SPADE_UN/` 和 `data/detail/SPADE_N/`
- 文件格式：单个抗菌肽的JSON文件
- 数据结构：包含 `Sequence Information` 对象的嵌套JSON

#### 索引信息提取
从每个JSON文件的 `Sequence Information` 对象中提取：
```json
{
  "id": "SPADE_N_00001",
  "name": "Variacin (Bacteriocin)",
  "sequence": "GSGVIPTISHECHMNSFQFVFTCCS",
  "length": 25
}
```

## 处理结果

### 数据统计
- **总抗菌肽数量**: 46,877个
- **有序列数据**: 46,877个（100%）
- **有名称数据**: 39,129个（83.5%）
- **序列长度范围**: 1 - 190 氨基酸
- **平均序列长度**: 23.0 氨基酸

### 分类统计
- **SPADE_N**: 16,004个条目
- **SPADE_UN**: 30,873个条目
- **其他**: 0个条目

### 生成的文件结构

#### 1. 完整索引文件
- **路径**: `data/index/peptide_index.json`
- **大小**: 6.5MB
- **格式**: 包含所有46,877个条目的JSON数组
- **用途**: search.html页面直接加载使用

#### 2. 分页索引文件
- **目录**: `data/index/pages/`
- **总页数**: 3,126页
- **每页条目**: 15个（最后一页2个）
- **文件模板**: `peptide_index_page_{页码}.json`
- **元数据文件**: `metadata.json`

#### 3. 统计信息文件
- **路径**: `data/index/statistics.json`
- **内容**: 详细的数据统计信息

### 分页索引示例

#### 元数据结构
```json
{
  "total_items": 46877,
  "items_per_page": 15,
  "total_pages": 3126,
  "page_template": "peptide_index_page_{}.json",
  "generated_at": "2025-06-17T00:34:23.584706"
}
```

#### 单页索引格式
第1页包含15个条目，格式如下：
```json
[
  {
    "id": "SPADE_N_00001",
    "name": "Variacin (Bacteriocin)",
    "sequence": "GSGVIPTISHECHMNSFQFVFTCCS",
    "length": 25
  },
  // ... 14个更多条目
]
```

## 性能优化策略

### 1. 分页索引优势
- **内存效率**: 避免一次性加载全部46,877条数据
- **网络优化**: 按需加载，减少初始加载时间
- **用户体验**: 快速响应，渐进式数据显示

### 2. 索引文件优化
- **数据压缩**: 仅包含搜索必需的字段
- **按ID排序**: 支持二分查找等优化算法
- **UTF-8编码**: 支持多语言字符

### 3. 搜索性能
- **内存索引**: search.html在内存中维护完整索引
- **客户端过滤**: 支持实时搜索和过滤
- **缓存机制**: 浏览器缓存和IndexedDB持久化

## 与search.html的集成

### 索引加载路径
search.html会按以下优先级尝试加载索引：
1. `./data/index/peptide_index.json`
2. `data/index/peptide_index.json`
3. `/data/index/peptide_index.json`

### 数据验证
页面会验证索引数据格式：
- 检查是否为JSON数组
- 验证必需字段（id, name, sequence, length）
- 生成文件名列表用于后续数据加载

### 搜索功能支持
生成的索引完全支持search.html的所有搜索功能：
- ✅ ID精确搜索和模糊搜索
- ✅ 名称不区分大小写搜索
- ✅ 序列包含搜索
- ✅ 长度范围过滤（格式：10-50）

## 后续维护

### 数据更新流程
1. 更新 `data/detail` 目录中的原始数据
2. 运行 `python program/generate_index.py`
3. 重新生成完整和分页索引文件
4. 更新统计信息

### 脚本可扩展性
- 支持新增字段（如评分、分类等）
- 支持自定义分页大小
- 支持多种排序策略
- 支持数据验证和清理

## 文件清单

### 新增文件
1. `program/generate_index.py` - 索引生成脚本
2. `data/index/peptide_index.json` - 完整索引文件
3. `data/index/statistics.json` - 统计信息
4. `data/index/pages/metadata.json` - 分页元数据
5. `data/index/pages/peptide_index_page_*.json` - 3,126个分页索引文件

### 脚本使用方法
```bash
# 在项目根目录执行
python program/generate_index.py
```

## 总结

成功为SPADE系统生成了符合search.html页面要求的索引文件系统，包括：

1. **完整功能覆盖**: 支持所有搜索和分页需求
2. **高性能设计**: 分页索引和内存优化
3. **数据完整性**: 100%数据覆盖，无丢失
4. **易于维护**: 自动化脚本，可重复执行
5. **统计详实**: 提供完整的数据统计信息

索引系统已准备就绪，可以支持search.html页面的正常运行和高效搜索功能。 