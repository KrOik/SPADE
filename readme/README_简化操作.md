# 抗菌肽数据处理工具 - 简化操作指南

## 🚀 快速开始（推荐）

### 最简单的使用方式
```bash
cd Pure_Era/Program
python quick_start.py
```

然后选择：
- `1` - 系统检查
- `2` - 快速处理（推荐）
- `5` - 查看结果

## 📁 文件说明

### 核心文件（必需）
- `unified_processor.py` - 主处理程序
- `quick_start.py` - 快速启动器（推荐使用）
- `weights_config.yaml` - 评分配置文件

### 可选文件
- `run_processor.py` - 完整功能启动器
- `performance_monitor.py` - 性能监控工具
- `README_Processor.md` - 详细文档

## ⚡ 一键操作

### 方法1：快速启动器（最简单）
```bash
python quick_start.py
```

### 方法2：命令行快速处理
```bash
python unified_processor.py batch
```

### 方法3：自定义参数
```bash
python unified_processor.py batch --workers 6 --mode both
```

## 📊 处理结果

处理完成后，结果会保存在 `../WebPage/result/` 目录：
- `all_scores.json` - 所有肽的评分汇总（按分数排序）
- `peptide_index.json` - 肽数据索引
- `scored_*.json` - 单个肽的详细评分

## 🔧 常见问题

### 问题1：缺少依赖
```bash
pip install pyyaml
```

### 问题2：找不到数据文件
确保 `../WebPage/Database/` 目录存在且包含SPADE JSON文件

### 问题3：内存不足
使用较少的线程数：
```bash
python unified_processor.py batch --workers 2
```

## 📈 性能指标

- **处理速度**: 约 250-300 文件/秒
- **内存使用**: 约 2-4GB RAM
- **推荐配置**: 4+ CPU核心，8GB+ RAM

## 🎯 最佳实践

1. **首次使用**: 运行 `python quick_start.py` 选择系统检查
2. **大规模处理**: 使用 2-4 个线程避免系统卡顿
3. **定期检查**: 使用结果检查功能查看处理状态

## 💡 使用技巧

### 快速评分前N个文件
```bash
# 只处理前1000个文件进行测试
ls ../WebPage/Database/SPADE*.json | head -1000 | xargs cp -t test_data/
python unified_processor.py batch --input test_data --output test_result
```

### 只生成索引
```bash
python unified_processor.py batch --mode index --workers 6
```

### 只进行评分
```bash
python unified_processor.py batch --mode score --workers 4
```

## 🔄 工作流程

1. **系统检查** → 确认数据和依赖
2. **快速处理** → 评分 + 索引生成
3. **结果检查** → 查看统计和排名
4. **结果使用** → 在网页中使用处理结果

## 📞 获取帮助

- 详细文档: 查看 `README_Processor.md`
- 性能优化: 运行 `python performance_monitor.py`
- 命令帮助: `python unified_processor.py --help` 