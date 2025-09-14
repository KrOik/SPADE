#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成扩展索引文件
从详细数据中提取多维度检索所需的信息，生成扩展索引文件
"""

import json
import os
import re
from pathlib import Path

def extract_activity_type(biological_activity):
    """从生物活性中提取活性类型"""
    activity_types = []
    
    if not biological_activity:
        return []
    
    activity_str = ' '.join(biological_activity).lower()
    
    # 映射规则
    if any(term in activity_str for term in ['anti-gram+', 'gram-positive', 'gram positive']):
        activity_types.append('gram-positive')
    if any(term in activity_str for term in ['anti-gram-', 'gram-negative', 'gram negative']):
        activity_types.append('gram-negative')
    if any(term in activity_str for term in ['antifungal', 'anti-fungal', 'fungal']):
        activity_types.append('antifungal')
    if any(term in activity_str for term in ['antiviral', 'anti-viral', 'viral']):
        activity_types.append('antiviral')
    if any(term in activity_str for term in ['antibacterial', 'anti-bacterial']):
        if 'gram-positive' not in activity_types and 'gram-negative' not in activity_types:
            activity_types.append('broad-spectrum')
    
    return activity_types

def extract_target_organisms(target_organism_str):
    """从目标生物字符串中提取标准化的目标生物"""
    if not target_organism_str:
        return []
    
    target_str = target_organism_str.lower()
    organisms = []
    
    # 常见目标生物映射
    organism_mapping = {
        'staphylococcus aureus': 'Staphylococcus aureus',
        'escherichia coli': 'Escherichia coli', 
        'e. coli': 'Escherichia coli',
        'pseudomonas aeruginosa': 'Pseudomonas aeruginosa',
        'klebsiella pneumoniae': 'Klebsiella pneumoniae',
        'acinetobacter baumannii': 'Acinetobacter baumannii',
        'enterococcus faecalis': 'Enterococcus faecalis',
        'candida albicans': 'Candida albicans',
        'aspergillus fumigatus': 'Aspergillus fumigatus',
        'listeria monocytogenes': 'Listeria monocytogenes',
        'lactobacillus': 'Lactobacillus spp.',
        'streptococcus': 'Streptococcus spp.'
    }
    
    for key, value in organism_mapping.items():
        if key in target_str:
            organisms.append(value)
    
    # 如果没有找到具体的生物，添加通用分类
    if not organisms:
        if 'gram-positive' in target_str or 'gram positive' in target_str:
            organisms.append('Gram-positive bacteria')
        if 'gram-negative' in target_str or 'gram negative' in target_str:
            organisms.append('Gram-negative bacteria')
    
    return list(set(organisms))  # 去重

def determine_charge(net_charge):
    """根据净电荷确定电荷类型"""
    if net_charge is None:
        return 'unknown'
    
    try:
        charge_val = float(net_charge)
        if charge_val > 0:
            return 'positive'
        elif charge_val < 0:
            return 'negative'
        else:
            return 'neutral'
    except (ValueError, TypeError):
        return 'unknown'

def determine_hydrophobicity(hydrophobicity_value):
    """根据疏水性数值确定疏水性类型"""
    if hydrophobicity_value is None:
        return 'unknown'
    
    try:
        hydro_val = float(hydrophobicity_value)
        if hydro_val > 0.5:
            return 'hydrophobic'
        elif hydro_val < -0.5:
            return 'hydrophilic'
        else:
            return 'amphipathic'
    except (ValueError, TypeError):
        return 'unknown'

def determine_secondary_structure(structure_desc, linear_cyclic):
    """根据结构描述确定二级结构"""
    if linear_cyclic and linear_cyclic.lower() == 'cyclic':
        return 'cyclic'
    elif linear_cyclic and linear_cyclic.lower() == 'linear':
        return 'linear'
    
    if structure_desc:
        desc_lower = structure_desc.lower()
        if 'alpha' in desc_lower or 'helix' in desc_lower:
            return 'alpha-helix'
        elif 'beta' in desc_lower or 'sheet' in desc_lower:
            return 'beta-sheet'
        elif 'coil' in desc_lower or 'random' in desc_lower:
            return 'random-coil'
    
    return 'unknown'

def process_detail_file(file_path):
    """处理单个详细数据文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 获取第一个键（SPADE ID）
        spade_id = list(data.keys())[0]
        seq_info = data[spade_id].get('Sequence Information', {})
        
        # 提取基础信息
        extracted_data = {
            'id': seq_info.get('SPADE ID', ''),
            'name': seq_info.get('Peptide Name', ''),
            'sequence': seq_info.get('Sequence', ''),
            'length': seq_info.get('Sequence Length', 0),
            'source': seq_info.get('Source', ''),
            'pi': seq_info.get('PI', None),
            'net_charge': seq_info.get('Net Charge', None),
            'hydrophobicity_value': seq_info.get('Hydrophobicity', None)
        }
        
        # 提取活性类型
        biological_activity = seq_info.get('Biological Activity', [])
        extracted_data['activity_type'] = extract_activity_type(biological_activity)
        
        # 提取目标生物
        target_organism = seq_info.get('Target Organism', '')
        extracted_data['target_organisms'] = extract_target_organisms(target_organism)
        
        # 确定电荷类型
        extracted_data['charge'] = determine_charge(seq_info.get('Net Charge'))
        
        # 确定疏水性类型
        extracted_data['hydrophobicity'] = determine_hydrophobicity(seq_info.get('Hydrophobicity'))
        
        # 确定二级结构
        structure_desc = seq_info.get('Structure Description', '')
        linear_cyclic = seq_info.get('Linear/Cyclic', '')
        extracted_data['secondary_structure'] = determine_secondary_structure(structure_desc, linear_cyclic)
        
        return extracted_data
        
    except Exception as e:
        print(f"处理文件 {file_path} 时出错: {e}")
        return None

def generate_extended_index():
    """生成扩展索引文件"""
    detail_dirs = ['data/detail/SPADE_N', 'data/detail/SPADE_UN']
    extended_index = []
    
    for detail_dir in detail_dirs:
        detail_path = Path(detail_dir)
        if not detail_path.exists():
            print(f"目录不存在: {detail_dir}")
            continue
            
        print(f"处理目录: {detail_dir}")
        
        # 处理目录中的所有JSON文件
        json_files = list(detail_path.glob('*.json'))
        total_files = len(json_files)
        
        for i, json_file in enumerate(json_files):
            if i % 100 == 0:
                print(f"处理进度: {i}/{total_files}")
                
            extracted_data = process_detail_file(json_file)
            if extracted_data:
                extended_index.append(extracted_data)
    
    # 保存扩展索引
    output_path = 'data/index/peptide_extended_index.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(extended_index, f, ensure_ascii=False, indent=2)
    
    print(f"扩展索引已生成: {output_path}")
    print(f"总共处理了 {len(extended_index)} 个条目")

if __name__ == '__main__':
    generate_extended_index()