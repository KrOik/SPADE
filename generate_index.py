#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
抗菌肽索引生成脚本
从 data/detail 目录的 SPADE_UN 和 SPADE_N 子目录（大写）读取JSON文件，生成索引文件
支持分页索引和完整索引生成
"""

import json
import os
import glob
import math

def extract_peptide_info(file_path, spade_id):
    """
    从单个抗菌肽JSON文件中提取索引信息
    
    Args:
        file_path (str): JSON文件路径
        spade_id (str): SPADE ID（从文件名提取）
    
    Returns:
        dict: 包含索引信息的字典，如果提取失败返回None
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 获取第一个（也是唯一的）条目
        if not data:
            print(f"警告: 文件 {file_path} 为空")
            return None
            
        peptide_data = list(data.values())[0]
        
        # 提取序列信息
        seq_info = peptide_data.get('Sequence Information', {})
        
        # 提取关键字段
        peptide_id = seq_info.get('SPADE ID') or seq_info.get('DRAMP ID') or spade_id
        peptide_name = seq_info.get('Peptide Name', 'N/A')
        sequence = seq_info.get('Sequence', '')
        sequence_length = seq_info.get('Sequence Length', len(sequence) if sequence else 0)
        
        # 构建索引条目
        index_entry = {
            'id': peptide_id,
            'name': peptide_name if peptide_name else 'N/A',
            'sequence': sequence if sequence else '',
            'length': int(sequence_length) if isinstance(sequence_length, (int, float)) else len(sequence) if sequence else 0
        }
        
        return index_entry
        
    except Exception as e:
        print(f"处理文件 {file_path} 时出错: {e}")
        return None

def process_detail_directory(detail_dir):
    """
    处理detail目录下的SPADE_UN和SPADE_N子目录（大写），提取索引信息
    
    Args:
        detail_dir (str): detail目录路径
    
    Returns:
        list: 索引条目列表
    """
    print(f"开始处理目录: {detail_dir}")
    
    index_entries = []
    total_files = 0
    success_count = 0
    
    # 处理SPADE_UN和SPADE_N两个子目录（恢复为大写）
    subdirs = ['SPADE_UN', 'SPADE_N']  # 核心修改：改回大写目录名
    
    for subdir in subdirs:
        subdir_path = os.path.join(detail_dir, subdir)
        
        if not os.path.exists(subdir_path):
            print(f"警告: 子目录 {subdir_path} 不存在，跳过")
            continue
        
        print(f"处理子目录: {subdir_path}")
        
        # 获取所有JSON文件
        json_files = glob.glob(os.path.join(subdir_path, '*.json'))
        total_files += len(json_files)
        
        print(f"在 {subdir} 中找到 {len(json_files)} 个JSON文件")
        
        for file_path in json_files:
            # 从文件名提取SPADE ID
            file_name = os.path.basename(file_path)
            spade_id = file_name.replace('.json', '')
            
            # 提取索引信息
            entry = extract_peptide_info(file_path, spade_id)
            
            if entry:
                index_entries.append(entry)
                success_count += 1
                
                # 显示进度
                if success_count % 1000 == 0:
                    print(f"已处理: {success_count}/{total_files}")
    
    print(f"索引提取完成: {success_count}/{total_files} 个文件成功处理")
    return index_entries

def generate_complete_index(index_entries, output_path):
    """
    生成完整的索引文件
    
    Args:
        index_entries (list): 索引条目列表
        output_path (str): 输出文件路径
    """
    print(f"生成完整索引文件: {output_path}")
    
    # 按ID排序
    sorted_entries = sorted(index_entries, key=lambda x: x['id'])
    
    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 保存完整索引
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(sorted_entries, f, ensure_ascii=False, indent=2)
    
    print(f"完整索引已保存，包含 {len(sorted_entries)} 个条目")

def generate_paginated_indexes(index_entries, output_dir, items_per_page=15):
    """
    生成分页索引文件
    
    Args:
        index_entries (list): 索引条目列表
        output_dir (str): 输出目录路径
        items_per_page (int): 每页条目数，默认15
    """
    print(f"生成分页索引文件，每页 {items_per_page} 条数据")
    
    # 按ID排序
    sorted_entries = sorted(index_entries, key=lambda x: x['id'])
    
    # 计算总页数
    total_pages = math.ceil(len(sorted_entries) / items_per_page)
    
    print(f"总计 {len(sorted_entries)} 个条目，将生成 {total_pages} 页索引")
    
    # 确保输出目录存在
    pages_dir = os.path.join(output_dir, 'pages')
    os.makedirs(pages_dir, exist_ok=True)
    
    # 生成每页的索引文件
    for page in range(1, total_pages + 1):
        start_index = (page - 1) * items_per_page
        end_index = min(page * items_per_page, len(sorted_entries))
        
        page_entries = sorted_entries[start_index:end_index]
        
        # 构建页面文件名
        page_filename = f"peptide_index_page_{page}.json"
        page_path = os.path.join(pages_dir, page_filename)
        
        # 保存页面索引
        with open(page_path, 'w', encoding='utf-8') as f:
            json.dump(page_entries, f, ensure_ascii=False, indent=2)
        
        print(f"已生成第 {page} 页索引: {len(page_entries)} 个条目")
    
    # 生成页面元数据文件
    metadata = {
        'total_items': len(sorted_entries),
        'items_per_page': items_per_page,
        'total_pages': total_pages,
        'page_template': 'peptide_index_page_{}.json',
        'generated_at': __import__('datetime').datetime.now().isoformat()
    }
    
    metadata_path = os.path.join(pages_dir, 'metadata.json')
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    print(f"分页索引生成完成，元数据已保存到: {metadata_path}")

def generate_statistics(index_entries):
    """
    生成索引统计信息
    
    Args:
        index_entries (list): 索引条目列表
    
    Returns:
        dict: 统计信息
    """
    if not index_entries:
        return {}
    
    # 基本统计
    total_count = len(index_entries)
    sequences_with_data = sum(1 for entry in index_entries if entry['sequence'])
    named_peptides = sum(1 for entry in index_entries if entry['name'] and entry['name'] != 'N/A')
    
    # 长度统计
    lengths = [entry['length'] for entry in index_entries if entry['length'] > 0]
    length_stats = {
        'min_length': min(lengths) if lengths else 0,
        'max_length': max(lengths) if lengths else 0,
        'avg_length': sum(lengths) / len(lengths) if lengths else 0
    }
    
    # 按前缀分组统计（恢复为大写）
    spade_un_count = sum(1 for entry in index_entries if entry['id'].startswith('SPADE_UN'))
    spade_n_count = sum(1 for entry in index_entries if entry['id'].startswith('SPADE_N'))
    dramp_count = sum(1 for entry in index_entries if entry['id'].startswith('DRAMP'))
    
    stats = {
        'total_peptides': total_count,
        'peptides_with_sequence': sequences_with_data,
        'named_peptides': named_peptides,
        'length_statistics': length_stats,
        'category_counts': {
            'SPADE_UN': spade_un_count,  # 恢复为大写分类名
            'SPADE_N': spade_n_count,    # 恢复为大写分类名
            'DRAMP': dramp_count,
            'other': total_count - spade_un_count - spade_n_count - dramp_count
        }
    }
    
    return stats

def main():
    """主函数"""
    print("=" * 60)
    print("抗菌肽索引生成器")
    print("=" * 60)
    
    # 配置路径
    detail_dir = "data/detail"
    index_dir = "data/index"
    
    # 检查输入目录
    if not os.path.exists(detail_dir):
        print(f"错误: 输入目录 {detail_dir} 不存在")
        return
    
    print(f"输入目录: {detail_dir}")
    print(f"输出目录: {index_dir}")
    print("-" * 60)
    
    # 处理detail目录，提取索引信息
    index_entries = process_detail_directory(detail_dir)
    
    if not index_entries:
        print("错误: 没有成功提取到任何索引条目")
        return
    
    print("-" * 60)
    
    # 生成统计信息
    stats = generate_statistics(index_entries)
    print("数据统计:")
    print(f"  总抗菌肽数量: {stats['total_peptides']}")
    print(f"  有序列数据: {stats['peptides_with_sequence']}")
    print(f"  有名称数据: {stats['named_peptides']}")
    print(f"  序列长度范围: {stats['length_statistics']['min_length']} - {stats['length_statistics']['max_length']}")
    print(f"  平均序列长度: {stats['length_statistics']['avg_length']:.1f}")
    print("  分类统计:")
    for category, count in stats['category_counts'].items():
        if count > 0:
            print(f"    {category}: {count}")
    
    print("-" * 60)
    
    # 生成完整索引文件
    complete_index_path = os.path.join(index_dir, "peptide_index.json")
    generate_complete_index(index_entries, complete_index_path)
    
    print("-" * 60)
    
    # 生成分页索引文件
    generate_paginated_indexes(index_entries, index_dir, items_per_page=15)
    
    print("-" * 60)
    
    # 保存统计信息
    stats_path = os.path.join(index_dir, "statistics.json")
    with open(stats_path, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    
    print(f"统计信息已保存到: {stats_path}")
    
    print("=" * 60)
    print("索引生成完成！")
    print(f"完整索引: {complete_index_path}")
    print(f"分页索引: {index_dir}/pages/")
    print("=" * 60)

if __name__ == "__main__":
    main()

    # 12121