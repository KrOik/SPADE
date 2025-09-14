#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全面索引生成脚本
从data/detail中提取所有类目信息，生成更完整的索引
"""

import json
import os
import re
from collections import defaultdict, Counter
from typing import Dict, List, Set, Any

def extract_categories_from_detail_data():
    """从detail数据中提取所有类目信息"""
    
    categories = {
        'activity_types': set(),
        'target_organisms': set(),
        'families': set(),
        'sources': set(),
        'binding_targets': set(),
        'linear_cyclic': set(),
        'stereochemistry': set(),
        'charge_ranges': set(),
        'hydrophobicity_ranges': set(),
        'mass_ranges': set(),
        'length_ranges': set()
    }
    
    # 处理SPADE_N和SPADE_UN两个目录
    detail_dirs = ['data/detail/SPADE_N', 'data/detail/SPADE_UN']
    
    for detail_dir in detail_dirs:
        if not os.path.exists(detail_dir):
            print(f"目录不存在: {detail_dir}")
            continue
            
        print(f"处理目录: {detail_dir}")
        
        # 获取所有JSON文件
        json_files = [f for f in os.listdir(detail_dir) if f.endswith('.json')]
        print(f"找到 {len(json_files)} 个JSON文件")
        
        for filename in json_files:
            filepath = os.path.join(detail_dir, filename)
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 获取第一个键（通常是SPADE ID）
                spade_id = list(data.keys())[0]
                peptide_data = data[spade_id]
                
                if 'Sequence Information' not in peptide_data:
                    continue
                    
                seq_info = peptide_data['Sequence Information']
                
                # 提取活性类型
                if 'Biological Activity' in seq_info:
                    activities = seq_info['Biological Activity']
                    if isinstance(activities, list):
                        for activity in activities:
                            categories['activity_types'].add(activity.strip())
                    else:
                        categories['activity_types'].add(str(activities).strip())
                
                # 提取目标生物
                if 'Target Organism' in seq_info:
                    target_org = seq_info['Target Organism']
                    if target_org and target_org != 'No MICs found in DRAMP database':
                        # 分割多个目标生物
                        orgs = re.split(r'[,;]', target_org)
                        for org in orgs:
                            org = org.strip()
                            if org and org != 'No MICs found in DRAMP database':
                                categories['target_organisms'].add(org)
                
                # 提取家族信息
                if 'Family' in seq_info:
                    family = seq_info['Family']
                    if family and family != 'Not found':
                        categories['families'].add(family.strip())
                
                # 提取来源信息
                if 'Source' in seq_info:
                    source = seq_info['Source']
                    if source and source != 'Not found':
                        categories['sources'].add(source.strip())
                
                # 提取结合目标
                if 'Binding Target' in seq_info:
                    binding = seq_info['Binding Target']
                    if binding and binding != 'Not found':
                        categories['binding_targets'].add(binding.strip())
                
                # 提取线性/环状信息
                if 'Linear/Cyclic' in seq_info:
                    lc = seq_info['Linear/Cyclic']
                    if lc and lc != 'Not included yet':
                        categories['linear_cyclic'].add(lc.strip())
                
                # 提取立体化学信息
                if 'Stereochemistry' in seq_info:
                    stereo = seq_info['Stereochemistry']
                    if stereo and stereo != 'Not included yet':
                        categories['stereochemistry'].add(stereo.strip())
                
                # 提取电荷信息
                if 'Net Charge' in seq_info:
                    charge = seq_info['Net Charge']
                    if isinstance(charge, (int, float)):
                        if charge < 0:
                            categories['charge_ranges'].add('Negative')
                        elif charge > 0:
                            categories['charge_ranges'].add('Positive')
                        else:
                            categories['charge_ranges'].add('Neutral')
                
                # 提取疏水性信息
                if 'Hydrophobicity' in seq_info:
                    hydro = seq_info['Hydrophobicity']
                    if isinstance(hydro, (int, float)):
                        if hydro < -0.5:
                            categories['hydrophobicity_ranges'].add('Very Hydrophilic')
                        elif hydro < 0:
                            categories['hydrophobicity_ranges'].add('Hydrophilic')
                        elif hydro < 0.5:
                            categories['hydrophobicity_ranges'].add('Neutral')
                        else:
                            categories['hydrophobicity_ranges'].add('Hydrophobic')
                
                # 提取分子量范围
                if 'Mass' in seq_info:
                    mass = seq_info['Mass']
                    if isinstance(mass, (int, float)):
                        if mass < 1000:
                            categories['mass_ranges'].add('Small (<1kDa)')
                        elif mass < 3000:
                            categories['mass_ranges'].add('Medium (1-3kDa)')
                        elif mass < 5000:
                            categories['mass_ranges'].add('Large (3-5kDa)')
                        else:
                            categories['mass_ranges'].add('Very Large (>5kDa)')
                
                # 提取长度范围
                if 'Sequence Length' in seq_info:
                    length = seq_info['Sequence Length']
                    if isinstance(length, (int, float)):
                        if length < 10:
                            categories['length_ranges'].add('Very Short (<10)')
                        elif length < 20:
                            categories['length_ranges'].add('Short (10-20)')
                        elif length < 50:
                            categories['length_ranges'].add('Medium (20-50)')
                        else:
                            categories['length_ranges'].add('Long (>50)')
                
            except Exception as e:
                print(f"处理文件 {filename} 时出错: {e}")
                continue
    
    # 转换为列表并排序
    for key in categories:
        categories[key] = sorted(list(categories[key]))
    
    return categories

def generate_comprehensive_index():
    """生成全面的索引文件"""
    
    print("开始提取类目信息...")
    categories = extract_categories_from_detail_data()
    
    print("\n提取的类目信息:")
    for category_name, category_list in categories.items():
        print(f"{category_name}: {len(category_list)} 个选项")
        if len(category_list) <= 10:  # 只显示前10个
            print(f"  示例: {category_list[:5]}")
    
    # 保存类目信息
    categories_file = 'data/index/categories.json'
    os.makedirs(os.path.dirname(categories_file), exist_ok=True)
    
    with open(categories_file, 'w', encoding='utf-8') as f:
        json.dump(categories, f, ensure_ascii=False, indent=2)
    
    print(f"\n类目信息已保存到: {categories_file}")
    
    # 生成改进的索引
    print("\n开始生成改进的索引...")
    
    comprehensive_index = []
    detail_dirs = ['data/detail/SPADE_N', 'data/detail/SPADE_UN']
    
    for detail_dir in detail_dirs:
        if not os.path.exists(detail_dir):
            continue
            
        json_files = [f for f in os.listdir(detail_dir) if f.endswith('.json')]
        
        for filename in json_files:
            filepath = os.path.join(detail_dir, filename)
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                spade_id = list(data.keys())[0]
                peptide_data = data[spade_id]
                
                if 'Sequence Information' not in peptide_data:
                    continue
                    
                seq_info = peptide_data['Sequence Information']
                
                # 构建索引条目
                index_entry = {
                    'id': seq_info.get('SPADE ID', ''),
                    'name': seq_info.get('Peptide Name', ''),
                    'sequence': seq_info.get('Sequence', ''),
                    'length': seq_info.get('Sequence Length', 0),
                    'mass': seq_info.get('Mass', 0),
                    'charge': seq_info.get('Net Charge', 0),
                    'hydrophobicity': seq_info.get('Hydrophobicity', 0),
                    'pi': seq_info.get('PI', 0),
                    'formula': seq_info.get('Formula', ''),
                    'source': seq_info.get('Source', ''),
                    'family': seq_info.get('Family', ''),
                    'gene': seq_info.get('Gene', ''),
                    'activity_type': seq_info.get('Biological Activity', []),
                    'target_organisms': seq_info.get('Target Organism', ''),
                    'binding_target': seq_info.get('Binding Target', ''),
                    'linear_cyclic': seq_info.get('Linear/Cyclic', ''),
                    'stereochemistry': seq_info.get('Stereochemistry', ''),
                    'hemolytic_activity': seq_info.get('Hemolytic Activity', ''),
                    'cytotoxicity': seq_info.get('Cytotoxicity', ''),
                    'function': seq_info.get('Function', ''),
                    'half_life': seq_info.get('Half Life', ''),
                    'frequent_amino_acids': seq_info.get('Frequent Amino Acids', ''),
                    'absent_amino_acids': seq_info.get('Absent Amino Acids', ''),
                    'basic_residues': seq_info.get('Basic Residues', 0),
                    'acidic_residues': seq_info.get('Acidic Residues', 0),
                    'hydrophobic_residues': seq_info.get('Hydrophobic Residues', 0),
                    'polar_residues': seq_info.get('Polar Residues', 0),
                    'positive_residues': seq_info.get('Positive Residues', 0),
                    'negative_residues': seq_info.get('Negative Residues', 0),
                    'uniprot_entries': seq_info.get('UniProt Entry', []),
                    'literature': seq_info.get('Literature', []),
                    'similar_sequences': seq_info.get('Similar Sequences', [])
                }
                
                # 处理目标生物信息
                target_org = seq_info.get('Target Organism', '')
                if target_org and target_org != 'No MICs found in DRAMP database':
                    # 提取生物名称
                    orgs = re.split(r'[,;]', target_org)
                    target_organisms = []
                    for org in orgs:
                        org = org.strip()
                        if org and org != 'No MICs found in DRAMP database':
                            # 提取生物名称（去除MIC信息）
                            org_name = re.split(r'[\(\)]', org)[0].strip()
                            if org_name:
                                target_organisms.append(org_name)
                    index_entry['target_organisms'] = target_organisms
                
                comprehensive_index.append(index_entry)
                
            except Exception as e:
                print(f"处理文件 {filename} 时出错: {e}")
                continue
    
    # 保存全面索引
    comprehensive_index_file = 'data/index/peptide_comprehensive_index.json'
    with open(comprehensive_index_file, 'w', encoding='utf-8') as f:
        json.dump(comprehensive_index, f, ensure_ascii=False, indent=2)
    
    print(f"\n全面索引已保存到: {comprehensive_index_file}")
    print(f"总共处理了 {len(comprehensive_index)} 条记录")
    
    return categories, comprehensive_index

def generate_search_options():
    """生成搜索选项配置"""
    
    categories, _ = generate_comprehensive_index()
    
    # 生成搜索选项配置
    search_options = {
        'activity_types': {
            'label': '活性类型',
            'options': [{'value': cat, 'label': cat} for cat in categories['activity_types']]
        },
        'target_organisms': {
            'label': '目标生物',
            'options': [{'value': org, 'label': org} for org in categories['target_organisms'][:50]]  # 限制数量
        },
        'families': {
            'label': '家族',
            'options': [{'value': fam, 'label': fam} for fam in categories['families']]
        },
        'sources': {
            'label': '来源',
            'options': [{'value': src, 'label': src} for src in categories['sources'][:30]]  # 限制数量
        },
        'binding_targets': {
            'label': '结合目标',
            'options': [{'value': bt, 'label': bt} for bt in categories['binding_targets']]
        },
        'linear_cyclic': {
            'label': '结构类型',
            'options': [{'value': lc, 'label': lc} for lc in categories['linear_cyclic']]
        },
        'charge_ranges': {
            'label': '电荷',
            'options': [{'value': cr, 'label': cr} for cr in categories['charge_ranges']]
        },
        'hydrophobicity_ranges': {
            'label': '疏水性',
            'options': [{'value': hr, 'label': hr} for hr in categories['hydrophobicity_ranges']]
        },
        'mass_ranges': {
            'label': '分子量',
            'options': [{'value': mr, 'label': mr} for mr in categories['mass_ranges']]
        },
        'length_ranges': {
            'label': '长度',
            'options': [{'value': lr, 'label': lr} for lr in categories['length_ranges']]
        }
    }
    
    # 保存搜索选项配置
    search_options_file = 'data/index/search_options.json'
    with open(search_options_file, 'w', encoding='utf-8') as f:
        json.dump(search_options, f, ensure_ascii=False, indent=2)
    
    print(f"\n搜索选项配置已保存到: {search_options_file}")
    
    return search_options

if __name__ == "__main__":
    print("开始生成全面索引和搜索选项...")
    
    # 生成全面索引
    categories, comprehensive_index = generate_comprehensive_index()
    
    # 生成搜索选项
    search_options = generate_search_options()
    
    print("\n=== 生成完成 ===")
    print(f"类目信息: {len(categories)} 个类别")
    print(f"索引记录: {len(comprehensive_index)} 条")
    print(f"搜索选项: {len(search_options)} 个类别")
    
    # 显示统计信息
    print("\n=== 类目统计 ===")
    for category_name, category_list in categories.items():
        print(f"{category_name}: {len(category_list)} 个选项") 