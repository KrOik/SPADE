#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
抗菌肽序列长度统计分析工具
生成序列长度分布图表
"""

import os
import json
import glob
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from collections import Counter
import sys

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class SequenceLengthAnalyzer:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.sequences = []
        self.sequence_lengths = []
        self.peptide_data = []
        
    def find_data_files(self):
        """查找数据文件"""
        data_files = []
        
        # 查找可能的数据文件位置
        search_patterns = [
            os.path.join(self.data_dir, "**/*.json"),
            os.path.join(self.data_dir, "detail/**/*.json"),
            os.path.join(self.data_dir, "load/**/*.json"),
            os.path.join(self.data_dir, "**/*.txt"),
        ]
        
        for pattern in search_patterns:
            files = glob.glob(pattern, recursive=True)
            data_files.extend(files)
            
        return data_files
    
    def load_data_from_json(self, file_path):
        """从JSON文件加载数据"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # 如果是列表格式
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        self.extract_sequence_info(item)
            # 如果是字典格式
            elif isinstance(data, dict):
                # 可能是单个肽数据
                if 'Sequence' in data or 'Sequence Length' in data:
                    self.extract_sequence_info(data)
                # 可能是多个肽数据的字典
                else:
                    for key, value in data.items():
                        if isinstance(value, dict):
                            self.extract_sequence_info(value)
                            
        except Exception as e:
            print(f"读取文件 {file_path} 时出错: {e}")
    
    def extract_sequence_info(self, peptide_dict):
        """从肽数据字典中提取序列信息"""
        sequence = peptide_dict.get('Sequence', '')
        sequence_length = peptide_dict.get('Sequence Length', None)
        
        # 如果有序列，计算长度
        if sequence and isinstance(sequence, str) and sequence.strip():
            seq_clean = sequence.strip()
            length = len(seq_clean)
            self.sequences.append(seq_clean)
            self.sequence_lengths.append(length)
            self.peptide_data.append(peptide_dict)
        
        # 如果直接有序列长度信息
        elif sequence_length and isinstance(sequence_length, (int, float)):
            self.sequence_lengths.append(int(sequence_length))
            self.peptide_data.append(peptide_dict)
    
    def generate_sample_data(self, n_samples=1000):
        """生成示例数据用于演示"""
        print("未找到数据文件，生成示例数据进行演示...")
        
        # 基于真实抗菌肽长度分布生成样本数据
        # 大多数抗菌肽长度在5-50之间，峰值在10-25之间
        np.random.seed(42)
        
        # 多峰分布，更符合实际情况
        lengths1 = np.random.normal(15, 3, n_samples//3)  # 短肽
        lengths2 = np.random.normal(25, 5, n_samples//3)  # 中等长度肽
        lengths3 = np.random.normal(35, 7, n_samples//3)  # 长肽
        
        all_lengths = np.concatenate([lengths1, lengths2, lengths3])
        # 限制在合理范围内
        all_lengths = np.clip(all_lengths, 5, 100).astype(int)
        
        self.sequence_lengths = all_lengths.tolist()
        
        # 生成对应的序列
        amino_acids = 'ACDEFGHIKLMNPQRSTVWY'
        for length in self.sequence_lengths:
            seq = ''.join(np.random.choice(list(amino_acids), size=length))
            self.sequences.append(seq)
    
    def load_all_data(self):
        """加载所有数据"""
        data_files = self.find_data_files()
        
        if not data_files:
            print("未找到数据文件，将生成示例数据")
            self.generate_sample_data()
            return
        
        print(f"找到 {len(data_files)} 个潜在数据文件")
        
        for file_path in data_files:
            print(f"正在处理: {file_path}")
            if file_path.endswith('.json'):
                self.load_data_from_json(file_path)
        
        if not self.sequence_lengths:
            print("从数据文件中未找到序列信息，生成示例数据")
            self.generate_sample_data()
        else:
            print(f"成功加载 {len(self.sequence_lengths)} 条序列数据")
    
    def analyze_lengths(self):
        """分析序列长度统计"""
        if not self.sequence_lengths:
            print("没有序列数据可以分析")
            return None
        
        lengths_array = np.array(self.sequence_lengths)
        
        stats = {
            'total_count': len(lengths_array),
            'min_length': lengths_array.min(),
            'max_length': lengths_array.max(),
            'mean_length': lengths_array.mean(),
            'median_length': np.median(lengths_array),
            'std_length': lengths_array.std(),
            'length_distribution': Counter(lengths_array)
        }
        
        return stats
    
    def create_visualization(self, save_path="data/result/sequence_length_analysis.png"):
        """创建序列长度统计可视化图表"""
        if not self.sequence_lengths:
            print("没有数据可以可视化")
            return
        
        # 创建结果目录
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        # 设置图表样式
        plt.style.use('seaborn-v0_8')
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('抗菌肽序列长度统计分析', fontsize=16, fontweight='bold')
        
        lengths_array = np.array(self.sequence_lengths)
        
        # 1. 直方图
        ax1.hist(lengths_array, bins=30, alpha=0.7, color='skyblue', edgecolor='black')
        ax1.set_xlabel('序列长度 (氨基酸残基数)')
        ax1.set_ylabel('频次')
        ax1.set_title('序列长度分布直方图')
        ax1.grid(True, alpha=0.3)
        
        # 添加统计信息
        mean_val = lengths_array.mean()
        median_val = np.median(lengths_array)
        ax1.axvline(mean_val, color='red', linestyle='--', label=f'平均值: {mean_val:.1f}')
        ax1.axvline(median_val, color='green', linestyle='--', label=f'中位数: {median_val:.1f}')
        ax1.legend()
        
        # 2. 箱线图
        ax2.boxplot(lengths_array, vert=True, patch_artist=True,
                   boxprops=dict(facecolor='lightblue', alpha=0.7))
        ax2.set_ylabel('序列长度 (氨基酸残基数)')
        ax2.set_title('序列长度箱线图')
        ax2.grid(True, alpha=0.3)
        
        # 3. 累积分布图
        sorted_lengths = np.sort(lengths_array)
        cumulative = np.arange(1, len(sorted_lengths) + 1) / len(sorted_lengths)
        ax3.plot(sorted_lengths, cumulative, linewidth=2, color='purple')
        ax3.set_xlabel('序列长度 (氨基酸残基数)')
        ax3.set_ylabel('累积概率')
        ax3.set_title('序列长度累积分布图')
        ax3.grid(True, alpha=0.3)
        
        # 4. 长度区间统计柱状图
        # 定义长度区间
        bins = [0, 10, 20, 30, 40, 50, 60, float('inf')]
        labels = ['≤10', '11-20', '21-30', '31-40', '41-50', '51-60', '>60']
        
        length_groups = pd.cut(lengths_array, bins=bins, labels=labels, right=True)
        group_counts = length_groups.value_counts().sort_index()
        
        bars = ax4.bar(range(len(group_counts)), group_counts.values, 
                      color='lightcoral', alpha=0.7, edgecolor='black')
        ax4.set_xlabel('序列长度区间 (氨基酸残基数)')
        ax4.set_ylabel('数量')
        ax4.set_title('序列长度区间分布')
        ax4.set_xticks(range(len(labels)))
        ax4.set_xticklabels(labels, rotation=45)
        ax4.grid(True, alpha=0.3)
        
        # 在柱状图上添加数值标签
        for bar, count in zip(bars, group_counts.values):
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height,
                    f'{count}', ha='center', va='bottom')
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"统计图表已保存至: {save_path}")
        
        return fig
    
    def generate_report(self, save_path="data/result/sequence_length_report.txt"):
        """生成详细的统计报告"""
        stats = self.analyze_lengths()
        if not stats:
            return
        
        # 创建结果目录
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write("抗菌肽序列长度统计分析报告\n")
            f.write("=" * 40 + "\n\n")
            
            f.write(f"总序列数: {stats['total_count']}\n")
            f.write(f"最短序列长度: {stats['min_length']} 个氨基酸残基\n")
            f.write(f"最长序列长度: {stats['max_length']} 个氨基酸残基\n")
            f.write(f"平均序列长度: {stats['mean_length']:.2f} 个氨基酸残基\n")
            f.write(f"中位数序列长度: {stats['median_length']:.2f} 个氨基酸残基\n")
            f.write(f"标准差: {stats['std_length']:.2f}\n\n")
            
            f.write("长度分布详情:\n")
            f.write("-" * 20 + "\n")
            
            # 按长度排序显示分布
            sorted_distribution = sorted(stats['length_distribution'].items())
            for length, count in sorted_distribution:
                percentage = (count / stats['total_count']) * 100
                f.write(f"{length:2d} 个氨基酸: {count:4d} 条序列 ({percentage:5.2f}%)\n")
        
        print(f"详细报告已保存至: {save_path}")
    
    def run_analysis(self):
        """运行完整的分析流程"""
        print("开始抗菌肽序列长度统计分析...")
        
        # 加载数据
        self.load_all_data()
        
        if not self.sequence_lengths:
            print("没有找到有效的序列数据")
            return
        
        # 分析统计
        stats = self.analyze_lengths()
        print(f"\n统计结果:")
        print(f"总序列数: {stats['total_count']}")
        print(f"长度范围: {stats['min_length']} - {stats['max_length']} 个氨基酸残基")
        print(f"平均长度: {stats['mean_length']:.2f} 个氨基酸残基")
        print(f"中位数长度: {stats['median_length']:.2f} 个氨基酸残基")
        
        # 生成图表
        self.create_visualization()
        
        # 生成报告
        self.generate_report()
        
        print("\n分析完成！")

def main():
    # 创建分析器
    analyzer = SequenceLengthAnalyzer()
    
    # 运行分析
    analyzer.run_analysis()

if __name__ == "__main__":
    main() 