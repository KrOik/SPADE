#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SPADE数据处理集合脚本
一键运行所有核心数据处理功能

功能包括：
1. 数据拆分处理
2. 索引生成
3. 增强评分系统
4. 综合AMP分析
5. 序列长度分析

使用方法:
python spade_data_processor.py [--step STEP] [--config CONFIG]

Steps:
- all: 运行所有步骤（默认）
- split: 仅数据拆分
- index: 仅索引生成  
- score: 仅增强评分
- analysis: 仅综合分析
- length: 仅序列长度分析
"""

import os
import sys
import json
import time
import argparse
import subprocess
from pathlib import Path
from datetime import datetime

class SPADEDataProcessor:
    def __init__(self, config_path=None):
        self.base_dir = Path(__file__).parent.parent
        self.data_dir = self.base_dir / "data"
        self.load_dir = self.data_dir / "load"
        self.detail_dir = self.data_dir / "detail"
        self.index_dir = self.data_dir / "index"
        self.result_dir = self.data_dir / "result"
        
        # 确保目录存在
        self.ensure_directories()
        
        # 加载配置
        self.config = self.load_config(config_path)
        
    def ensure_directories(self):
        """确保所有必要目录存在"""
        for dir_path in [self.data_dir, self.load_dir, self.detail_dir, 
                        self.index_dir, self.result_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
            
    def load_config(self, config_path):
        """加载配置文件"""
        default_config = {
            "data_source": "data/load",
            "output_detail": "data/detail", 
            "output_index": "data/index",
            "output_result": "data/result",
            "chunk_size": 1000,
            "min_length": 5,
            "max_length": 100,
            "enable_scoring": True,
            "enable_analysis": True
        }
        
        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception as e:
                print(f"警告：无法加载配置文件 {config_path}: {e}")
                print("使用默认配置")
                
        return default_config
        
    def log(self, message, level="INFO"):
        """日志输出"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
        
    def run_script(self, script_name, description):
        """运行Python脚本"""
        script_path = Path(__file__).parent / script_name
        if not script_path.exists():
            self.log(f"脚本不存在: {script_path}", "ERROR")
            return False
            
        self.log(f"开始 {description}...")
        try:
            result = subprocess.run(
                [sys.executable, str(script_path)],
                cwd=self.base_dir,
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            
            if result.returncode == 0:
                self.log(f"✓ {description} 完成")
                if result.stdout.strip():
                    print(result.stdout)
                return True
            else:
                self.log(f"✗ {description} 失败: {result.stderr}", "ERROR")
                if result.stdout.strip():
                    print("STDOUT:", result.stdout)
                return False
                
        except Exception as e:
            self.log(f"✗ {description} 执行异常: {e}", "ERROR")
            return False
            
    def step_split_data(self):
        """步骤1：数据拆分处理"""
        return self.run_script("split_peptides.py", "数据拆分处理")
        
    def step_generate_index(self):
        """步骤2：生成搜索索引"""
        return self.run_script("generate_index.py", "搜索索引生成")
        
    def step_enhanced_scoring(self):
        """步骤3：增强评分系统"""
        return self.run_script("run_enhanced_scoring.py", "增强评分系统")
        
    def step_comprehensive_analysis(self):
        """步骤4：综合AMP分析"""
        return self.run_script("comprehensive_amp_analysis.py", "综合AMP分析")
        
    def step_sequence_analysis(self):
        """步骤5：序列长度分析"""
        return self.run_script("sequence_length_analysis.py", "序列长度分析")
        
    def check_prerequisites(self):
        """检查运行前提条件"""
        self.log("检查运行环境...")
        
        # 检查数据源
        if not self.load_dir.exists() or not any(self.load_dir.iterdir()):
            self.log("警告：数据源目录为空，请确保 data/load 目录包含原始数据", "WARNING")
            
        # 检查Python依赖
        required_modules = ['pandas', 'numpy', 'json']
        missing_modules = []
        
        for module in required_modules:
            try:
                __import__(module)
            except ImportError:
                missing_modules.append(module)
                
        if missing_modules:
            self.log(f"缺少必要的Python模块: {', '.join(missing_modules)}", "ERROR")
            self.log("请运行: pip install -r requirements_sequence_analysis.txt", "ERROR")
            return False
            
        self.log("✓ 环境检查通过")
        return True
        
    def run_all_steps(self):
        """运行所有数据处理步骤"""
        start_time = time.time()
        self.log("=" * 60)
        self.log("开始SPADE数据处理流程")
        self.log("=" * 60)
        
        if not self.check_prerequisites():
            return False
            
        steps = [
            ("split", self.step_split_data, "数据拆分处理"),
            ("index", self.step_generate_index, "搜索索引生成"),
            ("score", self.step_enhanced_scoring, "增强评分系统"),
            ("analysis", self.step_comprehensive_analysis, "综合AMP分析"),
            ("length", self.step_sequence_analysis, "序列长度分析")
        ]
        
        success_count = 0
        for step_name, step_func, step_desc in steps:
            if step_func():
                success_count += 1
            else:
                self.log(f"步骤失败: {step_desc}", "ERROR")
                
        duration = time.time() - start_time
        self.log("=" * 60)
        self.log(f"数据处理完成！成功: {success_count}/{len(steps)}")
        self.log(f"总耗时: {duration:.1f}秒")
        self.log("=" * 60)
        
        return success_count == len(steps)
        
    def run_single_step(self, step):
        """运行单个步骤"""
        steps_map = {
            "split": self.step_split_data,
            "index": self.step_generate_index,
            "score": self.step_enhanced_scoring,
            "analysis": self.step_comprehensive_analysis,
            "length": self.step_sequence_analysis
        }
        
        if step not in steps_map:
            self.log(f"未知的步骤: {step}", "ERROR")
            self.log(f"可用步骤: {', '.join(steps_map.keys())}")
            return False
            
        return steps_map[step]()

def main():
    parser = argparse.ArgumentParser(description="SPADE数据处理集合脚本")
    parser.add_argument("--step", default="all", 
                       help="指定运行步骤 (all/split/index/score/analysis/length)")
    parser.add_argument("--config", 
                       help="配置文件路径")
    
    args = parser.parse_args()
    
    processor = SPADEDataProcessor(args.config)
    
    if args.step == "all":
        success = processor.run_all_steps()
    else:
        success = processor.run_single_step(args.step)
        
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 