import json
import re
import os
import yaml
import time
import warnings
from pathlib import Path
from typing import Dict, Any, List, Union, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse
import sys
from functools import partial

# 禁用SSL证书验证警告
warnings.filterwarnings("ignore", message="Unverified HTTPS request")

def find_value_in_dict(data: Any, target_key: str) -> Optional[Any]:
    """Recursively search for a key in a nested dictionary or list."""
    if isinstance(data, dict):
        if target_key in data:
            return data[target_key]
        for key, value in data.items():
            found = find_value_in_dict(value, target_key)
            if found is not None:
                return found
    elif isinstance(data, list):
        for item in data:
            found = find_value_in_dict(item, target_key)
            if found is not None:
                return found
    return None

def safe_get(data: Dict, key: str, default: Any = None) -> Any:
    """安全获取字典中的值，如果键不存在则返回默认值"""
    try:
        return data[key]
    except (KeyError, TypeError):
        return default

class UnifiedProcessor:
    """统一的肽数据处理器，支持评分和索引生成"""
    
    def __init__(self, config_file: str = None):
        # 默认权重配置
        self.default_weights = {
            "efficacy": 0.4,
            "toxicity": 0.25,
            "stability": 0.2,
            "synthesis": 0.15,
            "sub_weights": {},
            "scoring_parameters": {
                "max_length": 30,
                "min_hydrophobicity": 0.4,
                "optimal_disulfide": 4,
                "gravy_optimal_range": [-0.2, 0.1]
            }
        }
        
        # 加载配置
        self.weights = self.default_weights.copy()
        if config_file and os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                    if config and isinstance(config, dict):
                        self.weights.update(config)
                print(f"已从 {config_file} 加载权重配置")
            except Exception as e:
                print(f"加载配置文件时出错: {str(e)}，将使用默认配置")

    def process_single_file(self, file_path: str, mode: str = "both") -> Tuple[Optional[Dict], Optional[Dict]]:
        """
        处理单个JSON文件
        
        Args:
            file_path: 文件路径
            mode: 处理模式 ("score", "index", "both")
            
        Returns:
            (评分结果, 索引条目) 的元组
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            score_result = None
            index_entry = None
            
            # 生成评分结果
            if mode in ["score", "both"]:
                score_result = self._score_peptide(data)
            
            # 生成索引条目
            if mode in ["index", "both"]:
                index_entry = self._create_index_entry(data, os.path.basename(file_path))
            
            return score_result, index_entry
            
        except Exception as e:
            print(f"处理文件 {file_path} 时出错: {str(e)}")
            return None, None

    def _create_index_entry(self, data: Dict, filename: str) -> Optional[Dict]:
        """创建索引条目"""
        try:
            # 提取关键字段
            spade_id = find_value_in_dict(data, 'SPADE ID')
            dramp_id = find_value_in_dict(data, 'DRAMP ID')
            
            # 确定主要ID
            primary_id = spade_id if spade_id else dramp_id
            
            if primary_id is None:
                print(f"警告：文件 '{filename}' 缺少 'SPADE ID' 和 'DRAMP ID'，已跳过。")
                return None
            
            name = find_value_in_dict(data, 'Peptide Name') or 'N/A'
            sequence = find_value_in_dict(data, 'Sequence')

            # 确保数据类型正确
            if not isinstance(name, str):
                name = str(name)

            if not isinstance(sequence, str):
                try:
                    sequence = str(sequence) if sequence is not None else ''
                except:
                    sequence = ''

            length = len(sequence)

            return {
                'id': primary_id,
                'spade_id': spade_id,
                'dramp_id': dramp_id,
                'name': name,
                'sequence': sequence,
                'length': length,
                'filename': filename
            }
            
        except Exception as e:
            print(f"创建索引条目时出错 ({filename}): {str(e)}")
            return None

    def _score_peptide(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """评分单个肽数据 - 简化版本"""
        if not raw_data:
            return {"error": "数据为空"}

        # 提取基本信息
        sequence = find_value_in_dict(raw_data, "Sequence") or ""
        spade_id = find_value_in_dict(raw_data, "SPADE ID") or ""
        dramp_id = find_value_in_dict(raw_data, "DRAMP ID") or ""
        primary_id = spade_id if spade_id else dramp_id

        # 基本分数计算
        scores = self._calculate_basic_scores(raw_data, sequence)
        
        # 应用权重
        weighted_scores = self._apply_weights(scores)
        total = sum(weighted_scores.values())

        return {
            "SPADE ID": spade_id,
            "DRAMP ID": dramp_id,
            "Primary ID": primary_id,
            "Sequence": sequence,
            "scores": scores,
            "weighted_scores": weighted_scores,
            "total": total
        }

    def _calculate_basic_scores(self, data: Dict, sequence: str) -> Dict[str, float]:
        """计算基本评分 - 简化版本"""
        scores = {}
        
        # 基本分子特性
        length = len(sequence)
        net_charge = self._calculate_net_charge(sequence)
        hydrophobic_ratio = self._calculate_hydrophobic_ratio(sequence)
        
        # 效力评分 (基于序列特征)
        scores["mic"] = self._score_mic_prediction(sequence, hydrophobic_ratio, net_charge)
        
        # 毒性评分
        scores["hemolysis"] = self._score_hemolysis(sequence, hydrophobic_ratio, net_charge)
        scores["cytotoxicity"] = self._score_cytotoxicity(net_charge)
        
        # 稳定性评分
        scores["protease"] = self._score_protease_resistance(sequence)
        scores["ph_thermal"] = 7.0  # 默认值
        scores["half_life"] = 5.0   # 默认值
        
        # 合成可行性
        scores["length"] = 10.0 if length <= 30 else 5.0
        scores["rare_aa"] = 10.0   # 默认无稀有氨基酸
        scores["disulfide"] = self._score_disulfide(sequence)
        
        return scores

    def _calculate_net_charge(self, sequence: str) -> int:
        """计算净电荷"""
        positive = sequence.count('K') + sequence.count('R') + sequence.count('H')
        negative = sequence.count('D') + sequence.count('E')
        return positive - negative

    def _calculate_hydrophobic_ratio(self, sequence: str) -> float:
        """计算疏水残基比例"""
        hydrophobic_aa = set("AVILMFYW")
        hydrophobic_count = sum(1 for aa in sequence if aa.upper() in hydrophobic_aa)
        return (hydrophobic_count / len(sequence)) * 100 if sequence else 0

    def _score_mic_prediction(self, sequence: str, hydrophobic_ratio: float, net_charge: int) -> float:
        """预测MIC评分"""
        base_score = 5.0
        
        # 基于净电荷调整
        if 2 <= net_charge <= 6:
            base_score += 2.0
        elif net_charge > 6:
            base_score += 1.0
        
        # 基于疏水比例调整
        if 30 <= hydrophobic_ratio <= 60:
            base_score += 2.0
        elif hydrophobic_ratio > 80:
            base_score -= 2.0
            
        return max(0, min(10, base_score))

    def _score_hemolysis(self, sequence: str, hydrophobic_ratio: float, net_charge: int) -> float:
        """溶血活性评分"""
        if hydrophobic_ratio < 30:
            base_score = 10.0
        elif hydrophobic_ratio < 50:
            base_score = 7.0
        elif hydrophobic_ratio < 70:
            base_score = 4.0
        else:
            base_score = 1.0

        # 扣分项
        if re.search(r"[WFY]{3,}", sequence):
            base_score -= 2.0
        if net_charge == 0:
            base_score -= 1.0
            
        return max(0, min(10, base_score))

    def _score_cytotoxicity(self, net_charge: int) -> float:
        """细胞毒性评分"""
        if 2 <= net_charge <= 6:
            return 10.0 - abs(4 - net_charge)
        else:
            return max(0, 6.0 - abs(net_charge - 4))

    def _score_protease_resistance(self, sequence: str) -> float:
        """蛋白酶抗性评分"""
        return 10.0 if 'K' not in sequence and 'R' not in sequence else 5.0

    def _score_disulfide(self, sequence: str) -> float:
        """二硫键评分"""
        cys_count = sequence.count('C')
        disulfide_bonds = cys_count // 2
        
        if disulfide_bonds == 0:
            return 10.0
        elif disulfide_bonds <= 2:
            return 8.0
        else:
            return 6.0

    def _apply_weights(self, scores: Dict[str, float]) -> Dict[str, float]:
        """应用权重到各项评分"""
        weighted = {}
        
        category_items = {
            "efficacy": ["mic"],
            "toxicity": ["hemolysis", "cytotoxicity"],
            "stability": ["protease", "ph_thermal", "half_life"],
            "synthesis": ["length", "rare_aa", "disulfide"]
        }
        
        for category, items in category_items.items():
            main_weight = self.weights.get(category, 0.25)
            category_items_present = [item for item in items if item in scores]
            
            if category_items_present:
                category_score = sum(scores.get(item, 0) for item in category_items_present) / len(category_items_present)
            else:
                category_score = 0
                
            weighted[category] = category_score * main_weight
        
        return weighted

    def batch_process(self, input_dir: str, output_dir: str = None, mode: str = "both", 
                     max_workers: int = 4, file_pattern: str = None) -> Dict[str, Any]:
        """
        批量处理文件
        
        Args:
            input_dir: 输入目录
            output_dir: 输出目录（可选）
            mode: 处理模式 ("score", "index", "both")
            max_workers: 最大工作线程数
            file_pattern: 文件名模式过滤
            
        Returns:
            处理结果统计
        """
        # 路径处理
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        if not os.path.isabs(input_dir):
            if input_dir.startswith("Pure_Era/WebPage/"):
                relative_path = input_dir.replace("Pure_Era/", "../")
                input_dir = os.path.join(script_dir, relative_path)
            else:
                input_dir = os.path.join(script_dir, input_dir)
        
        input_dir = os.path.normpath(input_dir)
        
        if not os.path.exists(input_dir):
            raise FileNotFoundError(f"输入目录不存在: {input_dir}")
        
        # 创建输出目录
        if output_dir:
            if not os.path.isabs(output_dir):
                if output_dir.startswith("Pure_Era/WebPage/"):
                    relative_path = output_dir.replace("Pure_Era/", "../")
                    output_dir = os.path.join(script_dir, relative_path)
                else:
                    output_dir = os.path.join(script_dir, output_dir)
            
            output_dir = os.path.normpath(output_dir)
            os.makedirs(output_dir, exist_ok=True)
        
        # 获取文件列表
        json_files = []
        for f in os.listdir(input_dir):
            if f.lower().endswith('.json'):
                if file_pattern:
                    if file_pattern.lower() in f.lower():
                        json_files.append(f)
                else:
                    # 默认匹配dramp和spade文件
                    if f.lower().startswith(('dramp', 'spade')):
                        json_files.append(f)
        
        print(f"找到 {len(json_files)} 个匹配的JSON文件")
        print(f"处理模式: {mode}")
        print(f"使用 {max_workers} 个线程进行并行处理")
        
        # 初始化结果容器
        all_scores = []
        all_index_entries = []
        processed_count = 0
        error_count = 0
        
        # 多线程处理
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交任务
            future_to_file = {}
            for json_file in json_files:
                file_path = os.path.join(input_dir, json_file)
                future = executor.submit(self.process_single_file, file_path, mode)
                future_to_file[future] = json_file
            
            # 收集结果
            for future in as_completed(future_to_file):
                json_file = future_to_file[future]
                try:
                    score_result, index_entry = future.result()
                    
                    if score_result or index_entry:
                        processed_count += 1
                        
                        # 保存评分结果
                        if score_result and output_dir and mode in ["score", "both"]:
                            score_file = os.path.join(output_dir, f"scored_{json_file}")
                            with open(score_file, 'w', encoding='utf-8') as f:
                                json.dump(score_result, f, indent=2, ensure_ascii=False)
                            all_scores.append(score_result)
                        
                        # 收集索引条目
                        if index_entry and mode in ["index", "both"]:
                            all_index_entries.append(index_entry)
                        
                        if processed_count % 100 == 0:
                            print(f"已处理 {processed_count} 个文件...")
                    else:
                        error_count += 1
                        
                except Exception as e:
                    print(f"处理文件 {json_file} 时出错: {str(e)}")
                    error_count += 1
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # 保存汇总结果
        results = {
            "processed_files": processed_count,
            "error_files": error_count,
            "total_files": len(json_files),
            "processing_time": processing_time,
            "files_per_second": processed_count / processing_time if processing_time > 0 else 0
        }
        
        if output_dir:
            # 保存合并的评分结果
            if all_scores and mode in ["score", "both"]:
                all_scores.sort(key=lambda x: x.get('total', 0), reverse=True)
                scores_file = os.path.join(output_dir, "all_scores.json")
                with open(scores_file, 'w', encoding='utf-8') as f:
                    json.dump(all_scores, f, indent=2, ensure_ascii=False)
                print(f"已保存合并的评分结果: {scores_file}")
            
            # 保存索引文件
            if all_index_entries and mode in ["index", "both"]:
                index_file = os.path.join(output_dir, "peptide_index.json")
                with open(index_file, 'w', encoding='utf-8') as f:
                    json.dump(all_index_entries, f, indent=2, ensure_ascii=False)
                print(f"已保存索引文件: {index_file}")
                results["index_entries"] = len(all_index_entries)
        
        print(f"批量处理完成: {processed_count}/{len(json_files)} 个文件处理成功，{error_count} 个文件出错")
        print(f"处理时间: {processing_time:.2f}秒，处理速度: {results['files_per_second']:.2f} 文件/秒")
        
        return results

def create_config_template(output_path: str = "weights_config.yaml"):
    """创建配置文件模板"""
    config_template = {
        "efficacy": 0.4,
        "toxicity": 0.25,
        "stability": 0.2,
        "synthesis": 0.15,
        "sub_weights": {
            "efficacy": {"mic": 0.9, "synergy_bonus": 0.1},
            "toxicity": {"hemolysis": 0.4, "cytotoxicity": 0.3, "boman_score": 0.3},
            "stability": {"protease": 0.3, "ph_thermal": 0.4, "half_life": 0.3},
            "synthesis": {"length": 0.3, "rare_aa": 0.3, "disulfide": 0.4}
        },
        "scoring_parameters": {
            "max_length": 30,
            "min_hydrophobicity": 0.4,
            "optimal_disulfide": 4,
            "gravy_optimal_range": [-0.2, 0.1]
        }
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        yaml.dump(config_template, f, allow_unicode=True, default_flow_style=False)
    
    print(f"已创建配置文件模板: {output_path}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="统一的抗菌肽数据处理工具")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # 批量处理命令
    batch_parser = subparsers.add_parser("batch", help="批量处理JSON文件")
    batch_parser.add_argument("--input", help="输入目录", default="../data/detail")
    batch_parser.add_argument("--output", help="输出目录", default="../data/result")
    batch_parser.add_argument("--mode", choices=["score", "index", "both"], default="both", help="处理模式")
    batch_parser.add_argument("--config", help="配置文件路径", default="weights_config.yaml")
    batch_parser.add_argument("--workers", help="并行工作线程数", type=int, default=4)
    batch_parser.add_argument("--pattern", help="文件名过滤模式")
    
    # 创建配置文件命令
    config_parser = subparsers.add_parser("create-config", help="创建权重配置文件模板")
    config_parser.add_argument("--output", help="输出配置文件路径", default="weights_config.yaml")
    
    # 索引生成命令
    index_parser = subparsers.add_parser("index", help="生成肽索引文件")
    index_parser.add_argument("--input", help="输入目录", default="../data/detail")
    index_parser.add_argument("--output", help="输出文件", default="../data/index/peptide_index.json")
    index_parser.add_argument("--workers", help="并行工作线程数", type=int, default=4)
    
    args = parser.parse_args()
    
    if args.command == "batch":
        processor = UnifiedProcessor(
            config_file=args.config if os.path.exists(args.config) else None
        )
        
        results = processor.batch_process(
            input_dir=args.input,
            output_dir=args.output,
            mode=args.mode,
            max_workers=args.workers,
            file_pattern=args.pattern
        )
        
        print("\n处理结果统计:")
        for key, value in results.items():
            print(f"  {key}: {value}")
    
    elif args.command == "create-config":
        create_config_template(args.output)
    
    elif args.command == "index":
        processor = UnifiedProcessor()
        results = processor.batch_process(
            input_dir=args.input,
            output_dir=os.path.dirname(args.output) if os.path.dirname(args.output) else ".",
            mode="index",
            max_workers=args.workers
        )
        
        print(f"索引生成完成，处理了 {results['processed_files']} 个文件")
    
    else:
        # 默认执行批量处理
        print("使用默认参数执行批量处理...")
        processor = UnifiedProcessor()
        processor.batch_process(
            "../data/detail", 
            "../data/result",
            mode="both",
            max_workers=4
        )

if __name__ == "__main__":
    main() 