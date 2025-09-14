# 抗菌肽数据拆分处理说明

## 处理时间
2025年6月17日 00:25

## 数据结构分析

### 原始数据格式
原始数据文件位于 `data/load/` 目录，包含两个大型JSON文件：

1. **SPADE_UN.json** (82MB) - 包含30,873个抗菌肽条目
2. **SPADE_N.json** (41MB) - 包含16,004个抗菌肽条目

### 数据结构组成
每个抗菌肽条目包含以下三个主要部分：

1. **Clinical Information** (临床信息)
   - 类型：数组
   - 包含相关临床研究和试验信息

2. **Patent Information** (专利信息)
   - 类型：数组
   - 包含专利号、链接、类型、发布日期、标题、摘要等详细信息

3. **Sequence Information** (序列信息)
   - 包含抗菌肽的详细生物信息学数据：
     - SPADE ID：唯一标识符
     - Peptide Name：肽名称
     - Source：来源生物
     - Family：家族分类
     - Gene：基因信息
     - Sequence：氨基酸序列
     - 理化性质：质量、PI值、电荷、疏水性等
     - 生物活性：抗菌活性、目标微生物等
     - 相似序列：包含相似肽的信息

## 拆分处理过程

### 处理脚本
- **脚本位置**：`program/split_peptides.py`
- **功能**：将大型JSON文件中的每个抗菌肽条目拆分为单独的JSON文件

### 输出结构
```
data/detail/
├── SPADE_UN/           # SPADE_UN.json拆分结果
│   ├── SPADE_UN_00001.json
│   ├── SPADE_UN_00002.json
│   └── ... (30,873个文件)
└── SPADE_N/            # SPADE_N.json拆分结果
    ├── SPADE_N_00001.json
    ├── SPADE_N_00002.json
    └── ... (16,004个文件)
```

### 拆分结果统计
- **SPADE_UN目录**：30,873个JSON文件
- **SPADE_N目录**：16,004个JSON文件  
- **总计**：46,877个抗菌肽文件

### 单个文件格式示例
每个拆分后的文件保持原有的完整数据结构：

```json
{
    "SPADE_UN_00001": {
        "Clinical Information": [],
        "Patent Information": [...],
        "Sequence Information": {
            "SPADE ID": "SPADE_UN_00001",
            "Peptide Name": "Lantibiotic (Bacteriocin)",
            "Source": "Streptococcus pyogenes...",
            "Sequence": "MNNTIKDFDLDLKTNKKDTATPYVGSRYLCTPGSCWKLVCFTTTVK",
            ...
        }
    }
}
```

## 处理优势

1. **数据访问优化**：每个抗菌肽单独存储，便于快速访问特定条目
2. **内存效率**：避免加载大型JSON文件，减少内存占用
3. **并行处理**：支持对单个抗菌肽的并行处理操作
4. **模块化管理**：便于数据的增删改查操作
5. **存储优化**：保持原有完整信息的同时提高查询效率

## 后续应用建议

1. **索引构建**：可为拆分后的文件构建高效索引系统
2. **搜索优化**：基于单文件结构实现快速搜索功能
3. **批量处理**：可以并行处理多个抗菌肽的分析任务
4. **数据更新**：单个文件的修改不会影响其他数据

## 技术细节

- **编码格式**：UTF-8
- **JSON格式**：保持4空格缩进的可读格式
- **错误处理**：包含完整的异常处理机制
- **进度显示**：每100个文件显示一次处理进度
- **文件命名**：使用SPADE ID作为文件名保证唯一性 