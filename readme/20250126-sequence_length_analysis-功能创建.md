# 抗菌肽序列长度统计分析功能

## 概述
为SPADE系统新增了抗菌肽序列长度统计分析功能，能够自动分析抗菌肽数据中的序列长度分布，生成详细的统计图表和报告。

## 新增文件
- `program/sequence_length_analysis.py` - 主要分析程序
- `program/requirements_sequence_analysis.txt` - Python依赖包列表
- `sequence_length_visualization.html` - 结果展示页面
- `readme/20250126-sequence_length_analysis-功能创建.md` - 本说明文档

## 功能特性

### 数据处理能力
- 自动搜索并读取data目录下的JSON格式数据文件
- 支持多种数据结构格式（列表、字典、嵌套结构）
- 从数据中提取"Sequence"和"Sequence Length"字段
- 如果未找到实际数据，自动生成示例数据进行演示

### 统计分析
- **基础统计**: 总序列数、最短/最长序列长度、平均值、中位数、标准差
- **长度分布**: 按生物学意义划分的长度区间统计
- **详细分布**: 每个具体长度的序列数量和占比

### 可视化图表
生成4种类型的统计图表：
1. **序列长度分布直方图** - 显示整体分布情况，包含平均值和中位数标线
2. **箱线图** - 展示统计特征（四分位数、异常值等）
3. **累积分布图** - 显示序列长度的累积概率分布
4. **长度区间分布柱状图** - 按区间分组统计，便于生物学解释

### 输出结果
- `data/result/sequence_length_analysis.png` - 高清统计图表（300 DPI）
- `data/result/sequence_length_report.txt` - 详细文本报告

## 使用方法

### 1. 安装依赖
```bash
pip install -r program/requirements_sequence_analysis.txt
```

### 2. 运行分析
```bash
cd SPADE
python program/sequence_length_analysis.py
```

### 3. 查看结果
- 打开 `sequence_length_visualization.html` 查看结果展示页面
- 查看 `data/result/` 目录下的生成文件

## 数据要求

### 支持的数据格式
JSON文件，包含以下字段之一：
- `"Sequence"`: 氨基酸序列字符串（如："KWKLFKKIEKVGQNIRDGIIKAGPAVAVVGQATQIAK"）
- `"Sequence Length"`: 序列长度数值（如：38）

### 数据搜索路径
程序会自动搜索以下位置：
- `data/**/*.json` - data目录及其子目录下的所有JSON文件
- `data/detail/**/*.json` - detail目录下的数据文件
- `data/load/**/*.json` - load目录下的数据文件

### 示例数据结构
```json
{
  "Peptide Name": "Buforin I",
  "Sequence": "AGRGKQGGKVRAKAKTRSSRAGLQFPVGRVHRLLRKGNY",
  "Sequence Length": 38,
  "Source": "Bufo bufo gargarizans",
  "Target Organism": "Gram-positive and Gram-negative bacteria"
}
```

## 长度区间分类

根据抗菌肽的生物学特征，将序列长度分为以下区间：
- **≤10 氨基酸**: 短肽，通常具有特殊的环状结构
- **11-20 氨基酸**: 常见的抗菌肽长度范围
- **21-30 氨基酸**: 中等长度抗菌肽
- **31-40 氨基酸**: 较长的抗菌肽
- **41-50 氨基酸**: 长抗菌肽
- **51-60 氨基酸**: 很长的抗菌肽
- **>60 氨基酸**: 超长抗菌肽或蛋白质片段

## 技术实现

### 核心类：SequenceLengthAnalyzer
- `find_data_files()`: 搜索数据文件
- `load_data_from_json()`: 读取JSON数据
- `extract_sequence_info()`: 提取序列信息
- `analyze_lengths()`: 统计分析
- `create_visualization()`: 生成图表
- `generate_report()`: 生成报告

### 依赖包
- matplotlib: 图表绘制
- seaborn: 美化图表样式
- pandas: 数据处理
- numpy: 数值计算

## 扩展功能

### 未来可扩展的功能
1. **氨基酸组成分析**: 分析不同长度区间的氨基酸组成特征
2. **理化性质关联**: 结合序列长度分析理化性质分布
3. **数据库比对**: 与已知数据库进行长度分布比较
4. **交互式图表**: 使用Plotly等库生成交互式图表
5. **批量处理**: 支持多个数据集的批量分析和比较

### 自定义选项
程序支持以下自定义：
- 修改长度区间划分标准
- 调整图表样式和颜色
- 自定义输出路径
- 添加其他统计指标

## 错误处理
- 文件读取错误的容错处理
- 数据格式不匹配的自动处理
- 空数据集的处理（自动生成示例数据）
- 编码问题的处理（支持UTF-8）

## 生成时间
2025年1月26日

## 版本
v1.0.0 