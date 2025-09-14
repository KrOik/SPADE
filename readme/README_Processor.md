# 抗菌肽数据处理工具 - 使用说明

## 概述

这是一个优化的抗菌肽数据处理工具集，提供了高效的多线程处理、性能监控和便捷的操作界面。

## 文件结构

```
Pure_Era/Program/
├── unified_processor.py      # 统一处理器（主要功能）
├── performance_monitor.py    # 性能监控工具
├── run_processor.py         # 便捷启动器
├── score.py                 # 原始评分脚本（保留）
├── generate_index.py        # 原始索引生成脚本（保留）
└── README_Processor.md      # 本说明文档
```

## 主要功能

### 1. 统一处理器 (unified_processor.py)
- **评分功能**: 对抗菌肽进行多维度评分
- **索引生成**: 创建肽数据索引文件
- **多线程处理**: 支持并行处理提高效率
- **灵活配置**: 支持自定义权重和参数

### 2. 性能监控 (performance_monitor.py)
- **实时监控**: CPU和内存使用率
- **处理统计**: 文件处理速度和成功率
- **自动优化**: 根据系统资源调整处理参数

### 3. 便捷启动器 (run_processor.py)
- **交互式界面**: 图形化菜单操作
- **预设选项**: 常用处理模式
- **结果检查**: 自动分析处理结果

## 快速开始

### 安装依赖
```bash
pip install psutil pyyaml pathlib
```

### 基本使用

#### 方法1: 使用便捷启动器（推荐）
```bash
cd Pure_Era/Program
python run_processor.py
```

#### 方法2: 命令行直接使用
```bash
# 快速处理（评分+索引）
python run_processor.py --quick

# 仅评分
python run_processor.py --score

# 仅索引生成
python run_processor.py --index

# 检查结果
python run_processor.py --results
```

#### 方法3: 直接使用统一处理器
```bash
# 批量处理
python unified_processor.py batch --input ../WebPage/Database --output ../WebPage/result

# 创建配置文件
python unified_processor.py create-config
```

## 处理模式

### 1. 评分模式 (score)
对肽数据进行多维度评分：
- **效力评分**: MIC值预测、抗菌活性
- **毒性评分**: 溶血活性、细胞毒性  
- **稳定性评分**: 蛋白酶抗性、pH稳定性
- **合成可行性**: 序列长度、稀有氨基酸

### 2. 索引模式 (index)
生成肽数据索引：
- 提取关键字段（ID、名称、序列）
- 创建快速查找索引
- 支持SPADE和DRAMP数据

### 3. 综合模式 (both)
同时进行评分和索引生成

## 配置文件

### 权重配置 (weights_config.yaml)
```yaml
efficacy: 0.4      # 效力权重
toxicity: 0.25     # 毒性权重  
stability: 0.2     # 稳定性权重
synthesis: 0.15    # 合成可行性权重

sub_weights:       # 子权重配置
  efficacy:
    mic: 0.9
    synergy_bonus: 0.1
  # ... 其他子权重

scoring_parameters:  # 评分参数
  max_length: 30
  gravy_optimal_range: [-0.2, 0.1]
  # ... 其他参数
```

## 性能优化特性

### 1. 自动线程数调整
- 基于CPU核心数和内存大小
- 自动检测最优并发数
- 避免系统资源过载

### 2. 内存管理
- 分批处理大量文件
- 自动垃圾回收
- 内存使用监控

### 3. 错误处理
- 单文件错误不影响整体处理
- 详细错误日志
- 自动重试机制

## 输出结果

### 评分结果
- `scored_*.json`: 单个肽的评分结果
- `all_scores.json`: 所有肽的汇总评分（按总分排序）

### 索引结果
- `peptide_index.json`: 肽数据索引文件

### 结果示例
```json
{
  "SPADE ID": "SPADE_001",
  "DRAMP ID": "DRAMP_001", 
  "Primary ID": "SPADE_001",
  "Sequence": "KWKLFKKIEKVGQNIRDGIIKAGPAVAVVGQATQIAK",
  "scores": {
    "mic": 8.5,
    "hemolysis": 7.2,
    "cytotoxicity": 9.1,
    // ... 其他评分
  },
  "weighted_scores": {
    "efficacy": 3.4,
    "toxicity": 2.1,
    "stability": 1.6,
    "synthesis": 1.2
  },
  "total": 8.3
}
```

## 命令行选项

### unified_processor.py
```bash
python unified_processor.py batch [选项]
  --input DIR          输入目录 [../WebPage/Database]
  --output DIR         输出目录 [../WebPage/result]  
  --mode MODE          处理模式 [score|index|both]
  --workers N          线程数 [4]
  --pattern PATTERN    文件名过滤
  --config FILE        配置文件路径
  --no-apd3           禁用APD3数据
```

### run_processor.py
```bash
python run_processor.py [选项]
  --check             检查系统和数据
  --quick             快速处理
  --score             仅评分
  --index             仅索引  
  --custom            自定义参数
  --results           检查结果
  --perf              性能测试
```

## 性能指标

### 处理速度
- 典型处理速度: 50-200 文件/秒
- 取决于文件大小和系统配置

### 系统要求
- **最低**: 2GB RAM, 2 CPU核心
- **推荐**: 8GB RAM, 4+ CPU核心
- **磁盘空间**: 输入数据的2-3倍

## 故障排除

### 常见问题

1. **内存不足**
   - 减少线程数 (`--workers 2`)
   - 增加系统内存
   - 分批处理数据

2. **处理速度慢**
   - 增加线程数
   - 检查磁盘I/O性能
   - 关闭不必要的程序

3. **文件不存在错误**
   - 检查输入目录路径
   - 确认文件权限
   - 运行 `--check` 诊断

### 日志和调试
- 所有错误都会打印到控制台
- 使用 `--perf` 检查系统性能
- 查看 `result` 目录中的统计文件

## 开发说明

### 扩展功能
1. 修改 `unified_processor.py` 中的评分算法
2. 在 `weights_config.yaml` 中调整权重
3. 添加新的评分指标到 `_calculate_basic_scores`

### 自定义评分
```python
def custom_score_function(self, sequence: str) -> float:
    # 实现自定义评分逻辑
    return score
```

## 更新日志

### v2.0 (当前版本)
- 合并评分和索引功能
- 添加多线程优化
- 实时性能监控
- 便捷启动器界面

### v1.0
- 基础评分功能
- 单线程处理
- 基本索引生成

## 联系和支持

如有问题或建议，请联系开发团队或提交issue。 