#!/usr/bin/env python3
"""
增强评分系统 - SPADE项目
基于实际实验数据的抗菌肽评分系统
作者: SPADE团队
版本: 2.0
"""

import json
import re
import os
import math
import statistics
import warnings
from pathlib import Path
from typing import Dict, Any, List, Union, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse
import sys

warnings.filterwarnings("ignore", message="Unverified HTTPS request")

class EnhancedScoring:
    """增强评分系统主类"""
    
    def __init__(self):
        # 增强权重配置 - 基于抗菌肽特性重要性调整
        self.weights = {
            'efficacy': 0.35,      # 效力 - 稍微降低，因为实验数据更可靠
            'selectivity': 0.25,   # 选择性 - 新增，非常重要
            'stability': 0.20,     # 稳定性 - 保持重要
            'synthesis': 0.12,     # 合成难度 - 降低优先级
            'novelty': 0.08        # 新颖性 - 新增，基于序列相似性
        }
        
        # 氨基酸特性字典
        self.aa_properties = {
            'hydrophobic': set('AVILMFYW'),
            'hydrophilic': set('NQST'),
            'positive': set('KRH'),
            'negative': set('DE'),
            'aromatic': set('FYW'),
            'cysteine': set('C'),
            'proline': set('P'),
            'glycine': set('G')
        }
        
        # MIC值评分标准 (μg/ml)
        self.mic_ranges = {
            'excellent': (0, 2),    # ≤2 μg/ml
            'good': (2, 8),         # 2-8 μg/ml
            'moderate': (8, 32),    # 8-32 μg/ml
            'poor': (32, 128),      # 32-128 μg/ml
            'very_poor': (128, float('inf'))  # >128 μg/ml
        }
        
        # 溶血活性评分标准 (%)
        self.hemolysis_ranges = {
            'excellent': (0, 5),     # ≤5%
            'good': (5, 10),         # 5-10%
            'moderate': (10, 25),    # 10-25%
            'poor': (25, 50),        # 25-50%
            'very_poor': (50, 100)   # >50%
        }

    def find_value_in_dict(self, data: Any, target_key: str) -> Optional[Any]:
        """递归搜索嵌套字典或列表中的键"""
        if isinstance(data, dict):
            if target_key in data:
                return data[target_key]
            for key, value in data.items():
                found = self.find_value_in_dict(value, target_key)
                if found is not None:
                    return found
        elif isinstance(data, list):
            for item in data:
                found = self.find_value_in_dict(item, target_key)
                if found is not None:
                    return found
        return None

    def extract_mic_values(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """提取MIC值数据"""
        mic_values = []
        
        # 从目标生物数据中提取MIC值
        target_organisms = self.find_value_in_dict(data, "Target Organism") or []
        if isinstance(target_organisms, list):
            for organism in target_organisms:
                if isinstance(organism, dict):
                    organism_name = organism.get('name', '')
                    mic_value = organism.get('mic_value')
                    unit = organism.get('unit', 'μg/ml')
                    
                    if mic_value and isinstance(mic_value, (int, float)):
                        mic_values.append({
                            'organism': organism_name,
                            'value': float(mic_value),
                            'unit': unit
                        })
        
        # 从其他可能的字段中提取MIC值
        activity_data = self.find_value_in_dict(data, "Biological Activity") or []
        if isinstance(activity_data, list):
            for activity in activity_data:
                if isinstance(activity, str) and 'mic' in activity.lower():
                    # 解析MIC值字符串
                    mic_match = re.search(r'mic[:\s]*([0-9.]+)\s*([μu]g/ml|mg/ml)', activity.lower())
                    if mic_match:
                        value = float(mic_match.group(1))
                        unit = mic_match.group(2)
                        # 统一单位为μg/ml
                        if 'mg/ml' in unit:
                            value *= 1000
                        mic_values.append({
                            'organism': activity,
                            'value': value,
                            'unit': 'μg/ml'
                        })
        
        return mic_values

    def extract_hemolysis_data(self, data: Dict[str, Any]) -> Optional[float]:
        """提取溶血活性数据"""
        # 搜索溶血相关数据
        hemolysis_keys = ["Hemolysis", "Hemolytic", "HC50", "HD50"]
        
        for key in hemolysis_keys:
            value = self.find_value_in_dict(data, key)
            if value is not None:
                if isinstance(value, (int, float)):
                    return float(value)
                elif isinstance(value, str):
                    # 解析溶血百分比
                    percent_match = re.search(r'([0-9.]+)\s*%', value)
                    if percent_match:
                        return float(percent_match.group(1))
                    # 解析HC50/HD50值
                    conc_match = re.search(r'([0-9.]+)\s*([μu]g/ml|mg/ml)', value.lower())
                    if conc_match:
                        conc_value = float(conc_match.group(1))
                        unit = conc_match.group(2)
                        if 'mg/ml' in unit:
                            conc_value *= 1000
                        # 将浓度转换为溶血百分比估算值
                        return min(100, conc_value / 10)  # 简化估算
        
        return None

    def calculate_sequence_features(self, sequence: str) -> Dict[str, float]:
        """计算序列特征"""
        if not sequence:
            return {}
            
        length = len(sequence)
        features = {}
        
        # 基本氨基酸组成
        for prop, aa_set in self.aa_properties.items():
            count = sum(1 for aa in sequence if aa.upper() in aa_set)
            features[f'{prop}_count'] = count
            features[f'{prop}_ratio'] = count / length if length > 0 else 0
        
        # 净电荷计算
        positive_charge = features['positive_count']
        negative_charge = features['negative_count']
        features['net_charge'] = positive_charge - negative_charge
        
        # 疏水性比例
        features['hydrophobicity'] = features['hydrophobic_ratio']
        
        # 两亲性指数 (amphipathicity)
        features['amphipathicity'] = features['hydrophobic_ratio'] * features['hydrophilic_ratio']
        
        # 芳香性
        features['aromaticity'] = features['aromatic_ratio']
        
        # 结构特征
        features['cys_bonds_potential'] = features['cysteine_count'] // 2
        features['flexibility'] = features['glycine_count'] + features.get('proline_count', 0)
        
        return features

    def score_efficacy(self, data: Dict[str, Any], features: Dict[str, float]) -> Tuple[float, Dict[str, Any]]:
        """评分效力 - 基于实际MIC数据和序列特征"""
        details = {}
        
        # 提取MIC值
        mic_values = self.extract_mic_values(data)
        details['mic_data'] = mic_values
        
        if mic_values:
            # 基于实际MIC值评分
            mic_scores = []
            for mic_data in mic_values:
                mic_value = mic_data['value']
                if mic_value <= 2:
                    mic_scores.append(10.0)
                elif mic_value <= 8:
                    mic_scores.append(8.5)
                elif mic_value <= 32:
                    mic_scores.append(6.0)
                elif mic_value <= 128:
                    mic_scores.append(3.5)
                else:
                    mic_scores.append(1.0)
            
            base_score = statistics.mean(mic_scores)
            details['mic_based_score'] = base_score
        else:
            # 基于序列特征预测效力
            net_charge = features.get('net_charge', 0)
            hydrophobicity = features.get('hydrophobicity', 0)
            
            # 最适净电荷范围 (2-6)
            if 2 <= net_charge <= 6:
                charge_score = 10.0
            elif 1 <= net_charge <= 7:
                charge_score = 8.0
            elif 0 <= net_charge <= 8:
                charge_score = 6.0
            else:
                charge_score = 3.0
            
            # 最适疏水性范围 (30-60%)
            if 0.3 <= hydrophobicity <= 0.6:
                hydro_score = 10.0
            elif 0.2 <= hydrophobicity <= 0.7:
                hydro_score = 8.0
            elif 0.1 <= hydrophobicity <= 0.8:
                hydro_score = 6.0
            else:
                hydro_score = 3.0
            
            base_score = (charge_score + hydro_score) / 2
            details['predicted_score'] = base_score
            details['charge_score'] = charge_score
            details['hydrophobicity_score'] = hydro_score
        
        # 序列长度调整
        length = len(self.find_value_in_dict(data, "Sequence") or "")
        if 10 <= length <= 50:  # 最适长度范围
            length_factor = 1.0
        elif 8 <= length <= 80:
            length_factor = 0.9
        else:
            length_factor = 0.7
        
        final_score = base_score * length_factor
        details['length_factor'] = length_factor
        details['final_score'] = final_score
        
        return min(10.0, final_score), details

    def score_selectivity(self, data: Dict[str, Any], features: Dict[str, float]) -> Tuple[float, Dict[str, Any]]:
        """评分选择性 - 抗菌活性vs细胞毒性"""
        details = {}
        
        # 提取溶血活性数据
        hemolysis = self.extract_hemolysis_data(data)
        details['hemolysis_data'] = hemolysis
        
        if hemolysis is not None:
            # 基于实际溶血活性评分
            if hemolysis <= 5:
                hemolysis_score = 10.0
            elif hemolysis <= 10:
                hemolysis_score = 8.5
            elif hemolysis <= 25:
                hemolysis_score = 6.0
            elif hemolysis <= 50:
                hemolysis_score = 3.5
            else:
                hemolysis_score = 1.0
            
            details['hemolysis_score'] = hemolysis_score
            base_score = hemolysis_score
        else:
            # 基于序列特征预测选择性
            hydrophobicity = features.get('hydrophobicity', 0)
            net_charge = features.get('net_charge', 0)
            
            # 过高疏水性增加细胞毒性风险
            if hydrophobicity > 0.7:
                hydro_penalty = (hydrophobicity - 0.7) * 10
            else:
                hydro_penalty = 0
            
            # 适中的正电荷有利于选择性
            if 2 <= net_charge <= 5:
                charge_bonus = 2.0
            elif net_charge > 8:
                charge_bonus = -1.0  # 过高正电荷可能增加毒性
            else:
                charge_bonus = 0
            
            base_score = 7.0 - hydro_penalty + charge_bonus
            details['predicted_selectivity'] = base_score
            details['hydrophobicity_penalty'] = hydro_penalty
            details['charge_bonus'] = charge_bonus
        
        # 检查目标生物多样性
        target_organisms = self.find_value_in_dict(data, "Target Organism") or []
        organism_types = set()
        if isinstance(target_organisms, list):
            for org in target_organisms:
                if isinstance(org, dict):
                    org_name = org.get('name', '').lower()
                    if any(term in org_name for term in ['gram+', 'gram-', 'staphyl', 'strept']):
                        organism_types.add('bacteria')
                    elif any(term in org_name for term in ['candida', 'fungal', 'yeast']):
                        organism_types.add('fungi')
                    elif any(term in org_name for term in ['cancer', 'tumor', 'cell line']):
                        organism_types.add('cancer')
        
        # 多样性奖励
        diversity_bonus = len(organism_types) * 0.5
        final_score = min(10.0, base_score + diversity_bonus)
        details['diversity_bonus'] = diversity_bonus
        details['final_score'] = final_score
        
        return final_score, details

    def score_stability(self, data: Dict[str, Any], features: Dict[str, float]) -> Tuple[float, Dict[str, Any]]:
        """评分稳定性"""
        details = {}
        base_score = 5.0
        
        # 二硫键稳定性
        cys_count = features.get('cysteine_count', 0)
        potential_bonds = cys_count // 2
        if potential_bonds >= 2:
            disulfide_bonus = min(3.0, potential_bonds * 1.0)
        elif potential_bonds == 1:
            disulfide_bonus = 1.5
        else:
            disulfide_bonus = 0
        
        details['disulfide_bonds'] = potential_bonds
        details['disulfide_bonus'] = disulfide_bonus
        
        # 序列稳定性特征
        proline_ratio = features.get('proline_ratio', 0)
        glycine_ratio = features.get('glycine_ratio', 0)
        
        # 适量脯氨酸增加稳定性
        if 0.05 <= proline_ratio <= 0.15:
            proline_bonus = 1.0
        elif proline_ratio > 0.2:
            proline_bonus = -0.5  # 过多可能影响活性
        else:
            proline_bonus = 0
        
        # 过多甘氨酸降低结构稳定性
        glycine_penalty = max(0, (glycine_ratio - 0.1) * 5)
        
        details['proline_bonus'] = proline_bonus
        details['glycine_penalty'] = glycine_penalty
        
        # 检查已知稳定性信息
        stability_info = self.find_value_in_dict(data, "Stability") or self.find_value_in_dict(data, "Half-life")
        if stability_info:
            details['experimental_stability'] = stability_info
            base_score += 1.0  # 有实验数据的加分
        
        final_score = min(10.0, base_score + disulfide_bonus + proline_bonus - glycine_penalty)
        details['final_score'] = final_score
        
        return final_score, details

    def score_synthesis(self, data: Dict[str, Any], features: Dict[str, float]) -> Tuple[float, Dict[str, Any]]:
        """评分合成难度"""
        details = {}
        
        sequence = self.find_value_in_dict(data, "Sequence") or ""
        length = len(sequence)
        
        # 长度评分 - 越短越容易合成
        if length <= 20:
            length_score = 10.0
        elif length <= 30:
            length_score = 8.0
        elif length <= 40:
            length_score = 6.0
        elif length <= 50:
            length_score = 4.0
        else:
            length_score = 2.0
        
        details['length'] = length
        details['length_score'] = length_score
        
        # 稀有氨基酸惩罚
        rare_aa = set('WYC')  # 色氨酸、酪氨酸、半胱氨酸
        rare_count = sum(1 for aa in sequence if aa.upper() in rare_aa)
        rare_penalty = rare_count * 0.5
        
        details['rare_amino_acids'] = rare_count
        details['rare_penalty'] = rare_penalty
        
        # 重复序列奖励（更容易合成）
        unique_aa = len(set(sequence.upper()))
        repetition_bonus = max(0, (20 - unique_aa) * 0.1)
        
        details['unique_amino_acids'] = unique_aa
        details['repetition_bonus'] = repetition_bonus
        
        # 二硫键复杂性
        cys_count = features.get('cysteine_count', 0)
        if cys_count > 4:
            disulfide_penalty = (cys_count - 4) * 0.5
        else:
            disulfide_penalty = 0
        
        details['disulfide_penalty'] = disulfide_penalty
        
        final_score = max(1.0, length_score - rare_penalty + repetition_bonus - disulfide_penalty)
        details['final_score'] = final_score
        
        return final_score, details

    def score_novelty(self, data: Dict[str, Any], features: Dict[str, float]) -> Tuple[float, Dict[str, Any]]:
        """评分新颖性 - 基于序列相似性和功能多样性"""
        details = {}
        base_score = 5.0
        
        # 检查是否有相似序列信息
        similar_sequences = self.find_value_in_dict(data, "Similar Sequences") or []
        if isinstance(similar_sequences, list) and similar_sequences:
            similarity_scores = []
            for sim_seq in similar_sequences[:5]:  # 只看前5个最相似的
                if isinstance(sim_seq, dict):
                    similarity = sim_seq.get('similarity', 0)
                    if isinstance(similarity, (int, float)):
                        similarity_scores.append(similarity)
            
            if similarity_scores:
                max_similarity = max(similarity_scores)
                avg_similarity = statistics.mean(similarity_scores)
                
                # 相似性惩罚
                novelty_score = 10.0 - (max_similarity / 10)  # 假设相似性0-100
                details['max_similarity'] = max_similarity
                details['avg_similarity'] = avg_similarity
                details['novelty_from_similarity'] = novelty_score
                base_score = novelty_score
        
        # 功能多样性检查
        bioactivities = self.find_value_in_dict(data, "Biological Activity") or []
        unique_activities = set()
        if isinstance(bioactivities, list):
            for activity in bioactivities:
                if isinstance(activity, str):
                    activity_lower = activity.lower()
                    if 'antibacterial' in activity_lower:
                        unique_activities.add('antibacterial')
                    elif 'antifungal' in activity_lower:
                        unique_activities.add('antifungal')
                    elif 'antiviral' in activity_lower:
                        unique_activities.add('antiviral')
                    elif 'anticancer' in activity_lower:
                        unique_activities.add('anticancer')
                    elif 'anti-inflammatory' in activity_lower:
                        unique_activities.add('anti-inflammatory')
        
        # 多功能性奖励
        multifunctional_bonus = len(unique_activities) * 0.5
        details['unique_activities'] = list(unique_activities)
        details['multifunctional_bonus'] = multifunctional_bonus
        
        # 序列组成独特性
        aa_composition = {}
        sequence = self.find_value_in_dict(data, "Sequence") or ""
        for aa in sequence:
            aa_composition[aa.upper()] = aa_composition.get(aa.upper(), 0) + 1
        
        # 计算氨基酸分布的熵（多样性）
        if sequence:
            length = len(sequence)
            entropy = 0
            for count in aa_composition.values():
                p = count / length
                if p > 0:
                    entropy -= p * math.log2(p)
            
            # 标准化熵值（0-4.32，20种氨基酸的最大熵）
            normalized_entropy = entropy / 4.32
            composition_bonus = normalized_entropy * 2
            details['composition_entropy'] = entropy
            details['composition_bonus'] = composition_bonus
        else:
            composition_bonus = 0
        
        final_score = min(10.0, base_score + multifunctional_bonus + composition_bonus)
        details['final_score'] = final_score
        
        return final_score, details

    def calculate_total_score(self, scores: Dict[str, float]) -> float:
        """计算总分"""
        total = 0.0
        for category, weight in self.weights.items():
            if category in scores:
                total += scores[category] * weight
        return min(10.0, total)

    def get_score_category(self, score: float) -> str:
        """根据分数返回评价等级"""
        if score >= 8.5:
            return "Excellent"
        elif score >= 7.5:
            return "Good"
        elif score >= 6.5: 
            return "Above Average"
        elif score >= 5.5:
            return "Average"
        elif score >= 4.5:
            return "Below Average"
        elif score >= 3.5:
            return "Fair"
        elif score >= 2.5:
            return "Poor"
        else:
            return "Very Poor"

    def score_peptide(self, data: Dict[str, Any], file_id: str = None) -> Dict[str, Any]:
        """对单个肽进行评分"""
        sequence = self.find_value_in_dict(data, "Sequence") or ""
        if not sequence:
            return {
                "error": "No sequence found",
                "total": 0.0,
                "scores": {},
                "weighted_scores": {},
                "details": {}
            }
        
        # 计算序列特征
        features = self.calculate_sequence_features(sequence)
        
        # 各项评分
        scores = {}
        details = {}
        
        scores['efficacy'], details['efficacy'] = self.score_efficacy(data, features)
        scores['selectivity'], details['selectivity'] = self.score_selectivity(data, features)
        scores['stability'], details['stability'] = self.score_stability(data, features)
        scores['synthesis'], details['synthesis'] = self.score_synthesis(data, features)
        scores['novelty'], details['novelty'] = self.score_novelty(data, features)
        
        # 加权评分
        weighted_scores = {}
        for category, score in scores.items():
            weighted_scores[category] = score * self.weights[category]
        
        # 总分
        total_score = self.calculate_total_score(scores)
        
        # 目标生物信息整理
        target_organisms = self.organize_target_organisms(data)
        
        # 确定肽ID - 优先使用DRAMP ID，然后是文件ID
        peptide_id = self.find_value_in_dict(data, "DRAMP ID")
        if not peptide_id and file_id:
            peptide_id = file_id
        if not peptide_id:
            # 尝试其他可能的ID字段
            peptide_id = (self.find_value_in_dict(data, "Peptide Name") or 
                         self.find_value_in_dict(data, "ID") or 
                         self.find_value_in_dict(data, "Name") or 
                         "Unknown")
        
        return {
            "DRAMP ID": peptide_id,
            "total": round(total_score, 2),
            "category": self.get_score_category(total_score),
            "scores": {k: round(v, 2) for k, v in scores.items()},
            "weighted_scores": {k: round(v, 2) for k, v in weighted_scores.items()},
            "weights": self.weights,
            "features": features,
            "details": details,
            "target_organisms": target_organisms,
            "scoring_version": "2.0",
            "timestamp": self.get_timestamp()
        }

    def organize_target_organisms(self, data: Dict[str, Any]) -> Dict[str, List[Dict[str, str]]]:
        """整理目标生物信息"""
        target_organisms = {"Gram-positive": [], "Gram-negative": [], "Fungi": [], "Cancer": [], "Other": []}
        
        target_data = self.find_value_in_dict(data, "Target Organism") or []
        if isinstance(target_data, list):
            for target in target_data:
                if isinstance(target, dict):
                    name = target.get('name', '')
                    activity = target.get('activity', 'N/A')
                    
                    organism_info = {"name": name, "activity": activity}
                    
                    name_lower = name.lower()
                    if any(term in name_lower for term in ['staphyl', 'strept', 'bacill', 'enteroc', 'gram+']):
                        target_organisms['Gram-positive'].append(organism_info)
                    elif any(term in name_lower for term in ['e.coli', 'pseudom', 'gram-', 'salmonella']):
                        target_organisms['Gram-negative'].append(organism_info)
                    elif any(term in name_lower for term in ['candida', 'fungal', 'yeast']):
                        target_organisms['Fungi'].append(organism_info)
                    elif any(term in name_lower for term in ['cancer', 'tumor', 'cell line', 'hela']):
                        target_organisms['Cancer'].append(organism_info)
                    else:
                        target_organisms['Other'].append(organism_info)
        
        # 移除空分类
        return {k: v for k, v in target_organisms.items() if v}

    def get_timestamp(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().isoformat()

    def process_directory(self, input_dir: Path, output_dir: Path, 
                          max_workers: int = 4) -> Dict[str, Any]:
        """处理整个目录的数据"""
        input_dir = Path(input_dir)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 查找所有JSON文件
        json_files = []
        for subdir in ['SPADE_N', 'SPADE_UN']:
            subdir_path = input_dir / subdir
            if subdir_path.exists():
                json_files.extend(subdir_path.glob('*.json'))
        
        if not json_files:
            # 如果没有子目录，直接查找JSON文件
            json_files = list(input_dir.glob('*.json'))
        
        print(f"找到 {len(json_files)} 个JSON文件")
        
        results = {
            'processed': 0,
            'errors': 0,
            'success_files': [],
            'error_files': []
        }
        
        def process_file(json_file: Path) -> Tuple[bool, str, Optional[str]]:
            """处理单个文件"""
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 从文件名提取ID
                file_id = json_file.stem
                
                # 评分 - 传递文件ID
                score_result = self.score_peptide(data, file_id)
                
                # 获取肽ID作为输出文件名
                peptide_id = score_result.get("DRAMP ID", file_id)
                
                # 保存结果
                output_file = output_dir / f"scored_{peptide_id}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(score_result, f, indent=2, ensure_ascii=False)
                
                return True, str(json_file), None
                
            except Exception as e:
                return False, str(json_file), str(e)
        
        # 并行处理
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_file = {executor.submit(process_file, f): f for f in json_files}
            
            for future in as_completed(future_to_file):
                success, filename, error_msg = future.result()
                if success:
                    results['processed'] += 1
                    results['success_files'].append(filename)
                    if results['processed'] % 10 == 0:
                        print(f"已处理: {results['processed']}/{len(json_files)}")
                else:
                    results['errors'] += 1
                    results['error_files'].append(f"{filename}: {error_msg}")
                    print(f"错误处理文件 {filename}: {error_msg}")
        
        return results

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='SPADE增强评分系统')
    parser.add_argument('--input', '-i', type=str, default='data/detail',
                       help='输入目录路径 (默认: data/detail)')
    parser.add_argument('--output', '-o', type=str, default='data/result',
                       help='输出目录路径 (默认: data/result)')
    parser.add_argument('--workers', '-w', type=int, default=4,
                       help='并行工作线程数 (默认: 4)')
    parser.add_argument('--file', '-f', type=str,
                       help='处理单个文件')
    
    args = parser.parse_args()
    
    scorer = EnhancedScoring()
    
    if args.file:
        # 处理单个文件
        input_file = Path(args.file)
        if not input_file.exists():
            print(f"错误：文件不存在 - {input_file}")
            sys.exit(1)
        
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 从文件名提取ID
            file_id = input_file.stem
            result = scorer.score_peptide(data, file_id)
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
        except Exception as e:
            print(f"错误处理文件 {input_file}: {e}")
            sys.exit(1)
    
    else:
        # 处理整个目录
        input_dir = Path(args.input)
        output_dir = Path(args.output)
        
        if not input_dir.exists():
            print(f"错误：输入目录不存在 - {input_dir}")
            sys.exit(1)
        
        print("=== SPADE 增强评分系统 v2.0 ===")
        print(f"输入目录: {input_dir}")
        print(f"输出目录: {output_dir}")
        print(f"工作线程: {args.workers}")
        print()
        
        results = scorer.process_directory(input_dir, output_dir, args.workers)
        
        print("\n=== 处理完成 ===")
        print(f"成功处理: {results['processed']} 个文件")
        print(f"处理错误: {results['errors']} 个文件")
        
        if results['error_files']:
            print("\n错误文件:")
            for error_file in results['error_files'][:10]:  # 只显示前10个错误
                print(f"  {error_file}")
            if len(results['error_files']) > 10:
                print(f"  ... 还有 {len(results['error_files']) - 10} 个错误")

if __name__ == "__main__":
    main()