#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全面的抗菌肽数据分析工具
分析SPADE数据库中的抗菌肽序列信息
"""

import os
import json
import glob
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from collections import Counter, defaultdict
import sys
from datetime import datetime

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class ComprehensiveAMPAnalyzer:
    def __init__(self, data_dir="../data/detail", analyze_amino_acids=True, handle_special_symbols=True):
        self.data_dir = data_dir
        self.spade_n_dir = os.path.join(data_dir, "SPADE_N")
        self.spade_un_dir = os.path.join(data_dir, "SPADE_UN")
        # 数据存储
        self.peptide_data = []
        self.sequences = []
        self.sequence_lengths = []
        self.biological_activities = []
        self.amino_acid_counts = Counter()
        self.special_symbol_counts = Counter()
        
        # 特殊氨基酸和符号
        self.special_amino_acids = ['C', 'W', 'H', 'M', 'Y', 'F', 'P']  # 特殊氨基酸
        self.special_symbols = ['B', 'Z', 'J', 'X']  # 特殊符号
        
        # 统计数据
        self.stats = {}
        
        # 分析选项
        self.analyze_amino_acids = analyze_amino_acids
        self.handle_special_symbols = handle_special_symbols
        
        # 氨基酸映射规则（用于处理特殊符号）
        self.symbol_mapping = {
            'B': 'D',  # Asx → Asp
            'Z': 'E',  # Glx → Glu
            'J': 'L',  # Xle → Leu
            'X': 'X'   # 未知氨基酸保留为X
        }
    
    def load_json_file(self, file_path):
        """加载单个JSON文件"""
        if not os.path.exists(file_path):
            print(f"文件不存在: {file_path}")
            return None
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if not isinstance(data, dict):
                    print(f"警告：文件 {file_path} 的数据格式不正确，应为字典类型")
                    return None
                return data
        except json.JSONDecodeError as e:
            print(f"JSON解析错误 {file_path}: {str(e)}")
            return None
        except UnicodeDecodeError as e:
            print(f"编码错误 {file_path}: {str(e)}")
            try:
                # 尝试使用其他编码
                with open(file_path, 'r', encoding='gbk') as f:
                    data = json.load(f)
                    if not isinstance(data, dict):
                        print(f"警告：文件 {file_path} 的数据格式不正确，应为字典类型")
                        return None
                    return data
            except Exception as e2:
                print(f"使用GBK编码尝试失败: {str(e2)}")
                return None
        except Exception as e:
            print(f"读取文件 {file_path} 时出错: {str(e)}")
            return None
    
    def extract_peptide_info(self, data, data_type):
        """从肽数据中提取信息"""
        if not data:
            return
            
        for peptide_id, peptide_info in data.items():
            seq_info = peptide_info.get('Sequence Information', {})
            
            # 提取序列信息
            sequence = seq_info.get('Sequence', '')
            if not sequence or not isinstance(sequence, str):
                continue
                
            # 清理序列
            if self.handle_special_symbols:
                # 保留标准氨基酸和特殊符号
                valid_chars = 'ACDEFGHIKLMNPQRSTVWYBJZX'
            else:
                # 仅保留标准20种氨基酸
                valid_chars = 'ACDEFGHIKLMNPQRSTVWY'
                
            clean_sequence = ''.join([c for c in sequence.upper() if c in valid_chars])
            if not clean_sequence:
                continue
                
            # 处理特殊符号（如果需要）
            processed_sequence = clean_sequence
            if self.handle_special_symbols:
                processed_sequence = []
                for aa in clean_sequence:
                    if aa in self.special_symbols:
                        # 统计特殊符号
                        self.special_symbol_counts[aa] += 1
                        # 按映射规则替换
                        processed_sequence.append(self.symbol_mapping[aa])
                    else:
                        processed_sequence.append(aa)
                processed_sequence = ''.join(processed_sequence)
                
            # 基本信息
            peptide_record = {
                'SPADE_ID': peptide_id,
                'data_type': data_type,
                'sequence': processed_sequence,
                'original_sequence': clean_sequence,  # 保存原始序列
                'length': len(processed_sequence),
                'peptide_name': seq_info.get('Peptide Name', ''),
                'source': seq_info.get('Source', ''),
                'family': seq_info.get('Family', ''),
                'biological_activity': seq_info.get('Biological Activity', []),
                'target_organism': seq_info.get('Target Organism', ''),
                'mass': seq_info.get('Mass', 0),
                'pi': seq_info.get('PI', 0),
                'net_charge': seq_info.get('Net Charge', 0),
                'hydrophobicity': seq_info.get('Hydrophobicity', 0),
                'hemolytic_activity': seq_info.get('Hemolytic Activity', ''),
                'linear_cyclic': seq_info.get('Linear/Cyclic', ''),
            }
            
            self.peptide_data.append(peptide_record)
            self.sequences.append(processed_sequence)
            self.sequence_lengths.append(len(processed_sequence))
            
            # 收集生物活性信息
            bio_activity = seq_info.get('Biological Activity', [])
            if isinstance(bio_activity, list):
                self.biological_activities.extend(bio_activity)
            elif isinstance(bio_activity, str) and bio_activity:
                self.biological_activities.append(bio_activity)
            
            # 统计氨基酸
            if self.analyze_amino_acids:
                for aa in processed_sequence:
                    self.amino_acid_counts[aa] += 1
    
    def load_all_data(self):
        """加载所有数据"""
        print("开始加载抗菌肽数据...")
        print(f"数据目录: {os.path.abspath(self.data_dir)}")
        
        # 检查SPADE_N目录
        if not os.path.exists(self.spade_n_dir):
            print(f"错误：SPADE_N目录不存在: {self.spade_n_dir}")
            return
            
        # 检查SPADE_UN目录
        if not os.path.exists(self.spade_un_dir):
            print(f"错误：SPADE_UN目录不存在: {self.spade_un_dir}")
            return
        
        # 加载SPADE_N数据
        spade_n_files = glob.glob(os.path.join(self.spade_n_dir, "*.json"))
        print(f"找到 {len(spade_n_files)} 个SPADE_N文件")
        
        if len(spade_n_files) > 0:
            print(f"示例文件路径: {spade_n_files[0]}")
        
        for i, file_path in enumerate(spade_n_files):
            if i % 1000 == 0:
                print(f"处理SPADE_N进度: {i}/{len(spade_n_files)}")
            try:
                data = self.load_json_file(file_path)
                if data:
                    self.extract_peptide_info(data, 'SPADE_N')
            except Exception as e:
                print(f"处理文件时出错 {file_path}: {str(e)}")
        
        # 加载SPADE_UN数据
        spade_un_files = glob.glob(os.path.join(self.spade_un_dir, "*.json"))
        print(f"找到 {len(spade_un_files)} 个SPADE_UN文件")
        
        if len(spade_un_files) > 0:
            print(f"示例文件路径: {spade_un_files[0]}")
        
        for i, file_path in enumerate(spade_un_files):
            if i % 1000 == 0:
                print(f"处理SPADE_UN进度: {i}/{len(spade_un_files)}")
            try:
                data = self.load_json_file(file_path)
                if data:
                    self.extract_peptide_info(data, 'SPADE_UN')
            except Exception as e:
                print(f"处理文件时出错 {file_path}: {str(e)}")
        
        print(f"数据加载完成！共加载 {len(self.peptide_data)} 条有效序列")
        
        # 打印特殊符号统计（如果有）
        if self.handle_special_symbols and self.special_symbol_counts:
            print("\n特殊符号统计:")
            for symbol, count in self.special_symbol_counts.items():
                print(f"  {symbol}: {count} 次")
    
    def analyze_basic_statistics(self):
        """基础统计分析"""
        if not self.peptide_data:
            print("没有数据可以分析")
            return
        
        df = pd.DataFrame(self.peptide_data)
        
        self.stats['basic'] = {
            'total_sequences': len(self.peptide_data),
            'spade_n_count': len(df[df['data_type'] == 'SPADE_N']),
            'spade_un_count': len(df[df['data_type'] == 'SPADE_UN']),
            'min_length': min(self.sequence_lengths),
            'max_length': max(self.sequence_lengths),
            'mean_length': np.mean(self.sequence_lengths),
            'median_length': np.median(self.sequence_lengths),
            'std_length': np.std(self.sequence_lengths),
        }
        
        print("\n=== 基础统计信息 ===")
        print(f"总序列数: {self.stats['basic']['total_sequences']}")
        print(f"SPADE_N序列数: {self.stats['basic']['spade_n_count']}")
        print(f"SPADE_UN序列数: {self.stats['basic']['spade_un_count']}")
        print(f"序列长度范围: {self.stats['basic']['min_length']} - {self.stats['basic']['max_length']} 氨基酸")
        print(f"平均长度: {self.stats['basic']['mean_length']:.2f} 氨基酸")
        print(f"中位数长度: {self.stats['basic']['median_length']:.2f} 氨基酸")
    
    def analyze_biological_activities(self):
        """分析生物活性分布"""
        # 清理和标准化生物活性数据
        activity_counts = Counter()
        
        for activity in self.biological_activities:
            if activity and isinstance(activity, str):
                # 清理和标准化
                clean_activity = activity.strip()
                if clean_activity and clean_activity.lower() not in ['unknown', 'not found', '']:
                    activity_counts[clean_activity] += 1
        
        self.stats['biological_activities'] = dict(activity_counts.most_common(20))
        
        print("\n=== 生物活性分布 (前20) ===")
        for activity, count in activity_counts.most_common(20):
            percentage = (count / len(self.peptide_data)) * 100
            print(f"{activity}: {count} ({percentage:.2f}%)")
    
    def analyze_amino_acid_composition(self):
        """分析氨基酸组成"""
        if not self.analyze_amino_acids:
            print("\n跳过氨基酸组成分析（配置选项已禁用）")
            return
            
        total_amino_acids = sum(self.amino_acid_counts.values())
        
        # 计算所有氨基酸占比
        aa_percentages = {}
        for aa, count in self.amino_acid_counts.items():
            aa_percentages[aa] = (count / total_amino_acids) * 100
        
        # 特殊氨基酸统计
        special_aa_counts = {aa: self.amino_acid_counts.get(aa, 0) for aa in self.special_amino_acids}
        special_aa_total = sum(special_aa_counts.values())
        special_aa_percentage = (special_aa_total / total_amino_acids) * 100
        
        self.stats['amino_acids'] = {
            'total_amino_acids': total_amino_acids,
            'aa_percentages': aa_percentages,
            'special_aa_counts': special_aa_counts,
            'special_aa_total': special_aa_total,
            'special_aa_percentage': special_aa_percentage
        }
        
        print(f"\n=== 氨基酸组成分析 ===")
        print(f"总氨基酸数: {total_amino_acids}")
        print(f"特殊氨基酸 {self.special_amino_acids} 总数: {special_aa_total}")
        print(f"特殊氨基酸占总氨基酸比例: {special_aa_percentage:.2f}%")
        
        print("\n各氨基酸占比:")
        for aa in sorted(aa_percentages.keys()):
            print(f"{aa}: {aa_percentages[aa]:.2f}%")
        
        print(f"\n特殊氨基酸详细统计:")
        for aa in self.special_amino_acids:
            count = special_aa_counts[aa]
            percentage = (count / total_amino_acids) * 100
            print(f"{aa}: {count} ({percentage:.2f}%)")
    
    def analyze_length_distribution(self):
        """分析序列长度分布"""
        length_counter = Counter(self.sequence_lengths)
        
        # 长度区间统计
        length_ranges = {
            '≤10': 0, '11-20': 0, '21-30': 0, '31-40': 0, 
            '41-50': 0, '51-60': 0, '61-80': 0, '>80': 0
        }
        
        for length in self.sequence_lengths:
            if length <= 10:
                length_ranges['≤10'] += 1
            elif length <= 20:
                length_ranges['11-20'] += 1
            elif length <= 30:
                length_ranges['21-30'] += 1
            elif length <= 40:
                length_ranges['31-40'] += 1
            elif length <= 50:
                length_ranges['41-50'] += 1
            elif length <= 60:
                length_ranges['51-60'] += 1
            elif length <= 80:
                length_ranges['61-80'] += 1
            else:
                length_ranges['>80'] += 1
        
        self.stats['length_distribution'] = {
            'length_counter': dict(length_counter),
            'length_ranges': length_ranges
        }
        
        print(f"\n=== 序列长度分布 ===")
        for range_name, count in length_ranges.items():
            percentage = (count / len(self.sequence_lengths)) * 100
            print(f"{range_name} 氨基酸: {count} ({percentage:.2f}%)")
    
    def create_comprehensive_visualization(self, save_path="data/result/comprehensive_amp_analysis.png"):
        """创建综合可视化图表"""
        if not self.stats:
            print("没有统计数据可供可视化")
            return None
            
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        fig = plt.figure(figsize=(20, 16))
        
        # 1. 序列长度分布直方图
        ax1 = plt.subplot(3, 4, 1)
        plt.hist(self.sequence_lengths, bins=50, alpha=0.7, color='skyblue', edgecolor='black')
        plt.axvline(self.stats['basic']['mean_length'], color='red', linestyle='--', 
                   label=f'平均值: {self.stats["basic"]["mean_length"]:.1f}')
        plt.axvline(self.stats['basic']['median_length'], color='green', linestyle='--',
                   label=f'中位数: {self.stats["basic"]["median_length"]:.1f}')
        plt.xlabel('序列长度 (氨基酸)')
        plt.ylabel('频次')
        plt.title('序列长度分布')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # 2. 数据类型分布饼图
        ax2 = plt.subplot(3, 4, 2)
        data_type_counts = [self.stats['basic']['spade_n_count'], self.stats['basic']['spade_un_count']]
        labels = ['SPADE_N', 'SPADE_UN']
        plt.pie(data_type_counts, labels=labels, autopct='%1.1f%%', startangle=90)
        plt.title('数据类型分布')
        
        # 3. 长度区间分布
        ax3 = plt.subplot(3, 4, 3)
        ranges = list(self.stats['length_distribution']['length_ranges'].keys())
        counts = list(self.stats['length_distribution']['length_ranges'].values())
        bars = plt.bar(ranges, counts, color='lightcoral', alpha=0.7, edgecolor='black')
        plt.xlabel('长度区间 (氨基酸)')
        plt.ylabel('序列数量')
        plt.title('长度区间分布')
        plt.xticks(rotation=45)
        for bar, count in zip(bars, counts):
            plt.text(bar.get_x() + bar.get_width()/2., bar.get_height(),
                    f'{count}', ha='center', va='bottom')
        
        # 4. 氨基酸组成
        if self.analyze_amino_acids and 'amino_acids' in self.stats:
            ax4 = plt.subplot(3, 4, 4)
            aa_list = sorted(self.stats['amino_acids']['aa_percentages'].keys())
            aa_percentages = [self.stats['amino_acids']['aa_percentages'][aa] for aa in aa_list]
            bars = plt.bar(aa_list, aa_percentages, color='lightgreen', alpha=0.7, edgecolor='black')
            plt.xlabel('氨基酸')
            plt.ylabel('占比 (%)')
            plt.title('氨基酸组成分布')
            plt.xticks(rotation=45)
        else:
            ax4 = plt.subplot(3, 4, 4)
            plt.text(0.5, 0.5, '氨基酸分析已禁用', ha='center', va='center', fontsize=12)
            plt.axis('off')
        
        # 5. 特殊氨基酸分布
        if self.analyze_amino_acids and 'amino_acids' in self.stats:
            ax5 = plt.subplot(3, 4, 5)
            special_aa = self.special_amino_acids
            special_counts = [self.stats['amino_acids']['special_aa_counts'][aa] for aa in special_aa]
            bars = plt.bar(special_aa, special_counts, color='orange', alpha=0.7, edgecolor='black')
            plt.xlabel('特殊氨基酸')
            plt.ylabel('数量')
            plt.title('特殊氨基酸分布')
            for bar, count in zip(bars, special_counts):
                plt.text(bar.get_x() + bar.get_width()/2., bar.get_height(),
                        f'{count}', ha='center', va='bottom')
        else:
            ax5 = plt.subplot(3, 4, 5)
            plt.text(0.5, 0.5, '氨基酸分析已禁用', ha='center', va='center', fontsize=12)
            plt.axis('off')
        
        # 6. 生物活性分布（前10）
        ax6 = plt.subplot(3, 4, 6)
        activities = list(self.stats['biological_activities'].keys())[:10]
        activity_counts = list(self.stats['biological_activities'].values())[:10]
        plt.barh(activities, activity_counts, color='purple', alpha=0.7)
        plt.xlabel('数量')
        plt.title('主要生物活性分布 (前10)')
        plt.gca().invert_yaxis()
        
        # 7. 序列长度箱线图
        ax7 = plt.subplot(3, 4, 7)
        plt.boxplot(self.sequence_lengths, vert=True, patch_artist=True,
                   boxprops=dict(facecolor='lightblue', alpha=0.7))
        plt.ylabel('序列长度 (氨基酸)')
        plt.title('序列长度箱线图')
        
        # 8. 累积分布
        ax8 = plt.subplot(3, 4, 8)
        sorted_lengths = np.sort(self.sequence_lengths)
        cumulative = np.arange(1, len(sorted_lengths) + 1) / len(sorted_lengths)
        plt.plot(sorted_lengths, cumulative, linewidth=2, color='purple')
        plt.xlabel('序列长度 (氨基酸)')
        plt.ylabel('累积概率')
        plt.title('序列长度累积分布')
        plt.grid(True, alpha=0.3)
        
        # 9-12. 额外统计图表可以根据需要添加
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"综合统计图表已保存至: {save_path}")
        
        return fig
    
    def generate_comprehensive_report(self, save_path="data/result/comprehensive_amp_report.txt"):
        """生成综合分析报告"""
        if not self.stats:
            print("没有统计数据可供生成报告")
            return
            
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write("SPADE数据库抗菌肽综合分析报告\n")
            f.write("=" * 50 + "\n")
            f.write(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # 基础统计
            f.write("1. 基础统计信息\n")
            f.write("-" * 30 + "\n")
            f.write(f"总序列数: {self.stats['basic']['total_sequences']}\n")
            f.write(f"SPADE_N序列数: {self.stats['basic']['spade_n_count']}\n")
            f.write(f"SPADE_UN序列数: {self.stats['basic']['spade_un_count']}\n")
            f.write(f"最短序列长度: {self.stats['basic']['min_length']} 氨基酸\n")
            f.write(f"最长序列长度: {self.stats['basic']['max_length']} 氨基酸\n")
            f.write(f"平均序列长度: {self.stats['basic']['mean_length']:.2f} 氨基酸\n")
            f.write(f"中位数序列长度: {self.stats['basic']['median_length']:.2f} 氨基酸\n")
            f.write(f"标准差: {self.stats['basic']['std_length']:.2f}\n\n")
            
            # 长度分布
            f.write("2. 序列长度分布\n")
            f.write("-" * 30 + "\n")
            for range_name, count in self.stats['length_distribution']['length_ranges'].items():
                percentage = (count / len(self.sequence_lengths)) * 100
                f.write(f"{range_name} 氨基酸: {count:6d} 条序列 ({percentage:5.2f}%)\n")
            f.write("\n")
            
            # 氨基酸组成
            if self.analyze_amino_acids and 'amino_acids' in self.stats:
                f.write("3. 氨基酸组成分析\n")
                f.write("-" * 30 + "\n")
                f.write(f"总氨基酸数: {self.stats['amino_acids']['total_amino_acids']}\n")
                f.write(f"特殊氨基酸总数: {self.stats['amino_acids']['special_aa_total']}\n")
                f.write(f"特殊氨基酸占比: {self.stats['amino_acids']['special_aa_percentage']:.2f}%\n\n")
                
                f.write("各氨基酸占比:\n")
                for aa in sorted(self.stats['amino_acids']['aa_percentages'].keys()):
                    percentage = self.stats['amino_acids']['aa_percentages'][aa]
                    count = self.amino_acid_counts[aa]
                    f.write(f"{aa}: {count:8d} ({percentage:5.2f}%)\n")
                f.write("\n")
                
                f.write("特殊氨基酸详细统计:\n")
                for aa in self.special_amino_acids:
                    count = self.stats['amino_acids']['special_aa_counts'][aa]
                    percentage = (count / self.stats['amino_acids']['total_amino_acids']) * 100
                    f.write(f"{aa}: {count:6d} ({percentage:5.2f}%)\n")
                f.write("\n")
            else:
                f.write("3. 氨基酸组成分析（已禁用）\n")
                f.write("-" * 30 + "\n")
                f.write("根据配置选项，未进行氨基酸组成分析\n\n")
            
            # 特殊符号统计
            if self.handle_special_symbols and self.special_symbol_counts:
                f.write("4. 特殊符号统计\n")
                f.write("-" * 30 + "\n")
                for symbol, count in self.special_symbol_counts.items():
                    f.write(f"{symbol}: {count} 次\n")
                f.write("\n")
            
            # 生物活性分布
            f.write("5. 生物活性分布 (前20)\n")
            f.write("-" * 30 + "\n")
            for activity, count in list(self.stats['biological_activities'].items())[:20]:
                percentage = (count / len(self.peptide_data)) * 100
                f.write(f"{activity}: {count:4d} ({percentage:5.2f}%)\n")
        
        print(f"综合分析报告已保存至: {save_path}")
    
    def run_comprehensive_analysis(self):
        """运行完整的综合分析"""
        print("开始SPADE数据库抗菌肽综合分析...")
        
        # 加载数据
        self.load_all_data()
        
        if not self.peptide_data:
            print("没有找到有效的序列数据")
            return
        
        # 执行各项分析
        self.analyze_basic_statistics()
        self.analyze_length_distribution()
        if self.analyze_amino_acids:
            self.analyze_amino_acid_composition()
        self.analyze_biological_activities()
        
        # 生成可视化图表
        self.create_comprehensive_visualization()
        
        # 生成详细报告
        self.generate_comprehensive_report()
        
        print("\n=== 综合分析完成！ ===")
        print("请查看以下文件:")
        print("- data/result/comprehensive_amp_analysis.png (综合统计图表)")
        print("- data/result/comprehensive_amp_report.txt (详细分析报告)")

def main():
    # 获取脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # 设置数据目录为脚本目录的上一级的data/detail
    data_dir = os.path.normpath(os.path.join(script_dir, "..", "data", "detail"))
    
    # 检查目录是否存在
    if not os.path.exists(data_dir):
        print(f"错误：数据目录 '{data_dir}' 不存在")
        print(f"当前工作目录: {os.getcwd()}")
        print(f"脚本目录: {script_dir}")
        return
        
    if not os.path.exists(os.path.join(data_dir, "SPADE_N")):
        print(f"错误：SPADE_N 目录不存在于 '{data_dir}' 中")
        return
        
    if not os.path.exists(os.path.join(data_dir, "SPADE_UN")):
        print(f"错误：SPADE_UN 目录不存在于 '{data_dir}' 中")
        return
    
    print(f"使用数据目录: {data_dir}")
    
    # 创建分析器，可通过参数控制分析行为
    analyzer = ComprehensiveAMPAnalyzer(
        data_dir=data_dir,  # 使用绝对路径
        analyze_amino_acids=True,  # 是否分析氨基酸组成
        handle_special_symbols=True  # 是否处理特殊符号
    )
    
    # 运行综合分析
    analyzer.run_comprehensive_analysis()

if __name__ == "__main__":
    main()
    