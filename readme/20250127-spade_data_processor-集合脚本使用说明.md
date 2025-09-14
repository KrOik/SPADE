# SPADE数据处理集合脚本使用说明

## 概述

`spade_data_processor.py` 是SPADE项目的数据处理集合脚本，整合了所有核心数据处理功能，支持一键运行全流程处理或单独运行特定步骤。

## 功能模块

### 1. 数据拆分处理 (split)
- **功能**: 将原始数据拆分为小块，便于后续处理
- **输入**: `data/load/` 目录下的原始数据文件
- **输出**: `data/detail/` 目录下的拆分数据文件
- **对应脚本**: `split_peptides.py`

### 2. 搜索索引生成 (index)
- **功能**: 为数据生成搜索索引，提高查询效率
- **输入**: `data/detail/` 目录下的拆分数据
- **输出**: `data/index/` 目录下的索引文件
- **对应脚本**: `generate_index.py`

### 3. 增强评分系统 (score)
- **功能**: 对抗菌肽进行增强评分计算
- **输入**: 拆分后的数据和索引
- **输出**: 带有评分的数据文件
- **对应脚本**: `run_enhanced_scoring.py`

### 4. 综合AMP分析 (analysis)
- **功能**: 对抗菌肽进行综合统计分析
- **输入**: 处理后的数据
- **输出**: `data/result/` 目录下的分析报告和图表
- **对应脚本**: `comprehensive_amp_analysis.py`

### 5. 序列长度分析 (length)
- **功能**: 分析抗菌肽序列长度分布
- **输入**: 处理后的数据
- **输出**: `data/result/` 目录下的长度分析报告
- **对应脚本**: `sequence_length_analysis.py`

## 使用方法

### 基本用法

```bash
# 运行所有步骤（默认）
python program/spade_data_processor.py

# 或者明确指定运行所有步骤
python program/spade_data_processor.py --step all
```

### 单步骤运行

```bash
# 仅运行数据拆分
python program/spade_data_processor.py --step split

# 仅运行索引生成
python program/spade_data_processor.py --step index

# 仅运行评分系统
python program/spade_data_processor.py --step score

# 仅运行综合分析
python program/spade_data_processor.py --step analysis

# 仅运行序列长度分析
python program/spade_data_processor.py --step length
```

### 使用自定义配置

```bash
# 使用自定义配置文件
python program/spade_data_processor.py --config program/config.json
```

## 配置文件

可以创建配置文件来自定义处理参数：

```json
{
  "data_source": "data/load",
  "output_detail": "data/detail",
  "output_index": "data/index",
  "output_result": "data/result",
  "chunk_size": 1000,
  "min_length": 5,
  "max_length": 100,
  "enable_scoring": true,
  "enable_analysis": true
}
```

## 前置条件

### 1. 环境要求
- Python 3.7+
- 必需的Python包（见 `requirements_sequence_analysis.txt`）

### 2. 数据准备
- 确保 `data/load/` 目录包含原始数据文件
- 数据格式应符合SPADE项目规范

### 3. 安装依赖
```bash
pip install -r program/requirements_sequence_analysis.txt
```

## 目录结构

```
SPADE/
├── program/
│   ├── spade_data_processor.py    # 集合脚本
│   ├── split_peptides.py          # 数据拆分
│   ├── generate_index.py          # 索引生成
│   ├── run_enhanced_scoring.py    # 增强评分
│   ├── comprehensive_amp_analysis.py  # 综合分析
│   ├── sequence_length_analysis.py    # 序列长度分析
│   └── requirements_sequence_analysis.txt
└── data/
    ├── load/      # 原始数据
    ├── detail/    # 拆分数据
    ├── index/     # 索引文件
    └── result/    # 分析结果
```

## 执行流程

1. **环境检查**: 验证Python依赖和数据源
2. **数据拆分**: 将原始数据拆分为适当大小的块
3. **索引生成**: 为数据创建搜索索引
4. **评分计算**: 运行增强评分算法
5. **综合分析**: 生成统计分析报告
6. **长度分析**: 分析序列长度分布

## 输出说明

- **日志输出**: 带时间戳的详细执行日志
- **成功指示**: ✓ 表示步骤成功，✗ 表示失败
- **执行时间**: 显示每个步骤和总体执行时间
- **结果文件**: 保存在 `data/result/` 目录

## 故障排除

### 常见问题

1. **缺少依赖包**
   ```
   错误: 缺少必要的Python模块
   解决: pip install -r program/requirements_sequence_analysis.txt
   ```

2. **数据源为空**
   ```
   警告: 数据源目录为空
   解决: 确保 data/load 目录包含有效的数据文件
   ```

3. **脚本不存在**
   ```
   错误: 脚本不存在
   解决: 确保所有必需的脚本文件都在 program/ 目录中
   ```

### 调试模式

如果某个步骤失败，可以单独运行该步骤进行调试：

```bash
# 单独运行失败的步骤
python program/spade_data_processor.py --step [failed_step]

# 直接运行原始脚本进行详细调试
python program/[script_name].py
```

## 性能优化

- **并行处理**: 某些步骤支持并行处理以提高性能
- **内存管理**: 大文件会分块处理以避免内存溢出
- **缓存机制**: 中间结果可以缓存以避免重复计算

## 更新日志

### 2025-01-27
- 创建集合脚本整合所有数据处理功能
- 删除冗余和测试脚本
- 添加配置文件支持
- 实现分步骤执行功能
- 添加环境检查和错误处理

## 相关文档

- [README.md](README.md) - 项目总体说明
- [README_Processor.md](README_Processor.md) - 处理器详细说明
- [文件结构适配修改记录.md](文件结构适配修改记录.md) - 文件结构说明 