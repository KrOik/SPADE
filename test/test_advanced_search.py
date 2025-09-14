#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试高级搜索功能
验证全面索引和搜索选项的生成和使用
"""

import json
import os
import re
from typing import Dict, List, Any

def test_comprehensive_index():
    """测试全面索引的生成和使用"""
    
    print("=== 测试全面索引 ===")
    
    # 检查索引文件是否存在
    index_file = 'data/index/peptide_comprehensive_index.json'
    if not os.path.exists(index_file):
        print(f"❌ 索引文件不存在: {index_file}")
        return False
    
    # 加载索引数据
    try:
        with open(index_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✅ 成功加载索引数据: {len(data)} 条记录")
    except Exception as e:
        print(f"❌ 加载索引数据失败: {e}")
        return False
    
    # 检查数据完整性
    required_fields = ['id', 'name', 'sequence', 'activity_type', 'target_organisms']
    sample_item = data[0] if data else {}
    
    missing_fields = [field for field in required_fields if field not in sample_item]
    if missing_fields:
        print(f"❌ 缺少必需字段: {missing_fields}")
        return False
    
    print("✅ 数据完整性检查通过")
    
    # 测试搜索功能
    test_search_functionality(data)
    
    return True

def test_search_options():
    """测试搜索选项的生成"""
    
    print("\n=== 测试搜索选项 ===")
    
    # 检查搜索选项文件
    options_file = 'data/index/search_options.json'
    if not os.path.exists(options_file):
        print(f"❌ 搜索选项文件不存在: {options_file}")
        return False
    
    # 加载搜索选项
    try:
        with open(options_file, 'r', encoding='utf-8') as f:
            options = json.load(f)
        print(f"✅ 成功加载搜索选项: {len(options)} 个类别")
    except Exception as e:
        print(f"❌ 加载搜索选项失败: {e}")
        return False
    
    # 检查选项结构
    for category, config in options.items():
        if 'label' not in config or 'options' not in config:
            print(f"❌ 搜索选项结构错误: {category}")
            return False
        
        if not config['options']:
            print(f"⚠️  警告: {category} 没有选项")
        else:
            print(f"✅ {config['label']}: {len(config['options'])} 个选项")
    
    return True

def test_search_functionality(data: List[Dict[str, Any]]):
    """测试搜索功能"""
    
    print("\n=== 测试搜索功能 ===")
    
    # 测试活性类型搜索
    print("测试活性类型搜索...")
    antibacterial_results = [item for item in data if 
                           item.get('activity_type') and 
                           any('antibacterial' in str(act).lower() 
                               for act in (item['activity_type'] if isinstance(item['activity_type'], list) 
                                         else [item['activity_type']]))]
    print(f"  抗菌活性: {len(antibacterial_results)} 条记录")
    
    # 测试目标生物搜索
    print("测试目标生物搜索...")
    staph_results = [item for item in data if 
                    item.get('target_organisms') and 
                    any('staphylococcus' in str(org).lower() 
                        for org in (item['target_organisms'] if isinstance(item['target_organisms'], list) 
                                  else [item['target_organisms']]))]
    print(f"  金黄色葡萄球菌: {len(staph_results)} 条记录")
    
    # 测试家族搜索
    print("测试家族搜索...")
    lantibiotic_results = [item for item in data if 
                          item.get('family') and 
                          'lantibiotic' in item['family'].lower()]
    print(f"  羊毛硫抗生素: {len(lantibiotic_results)} 条记录")
    
    # 测试电荷搜索
    print("测试电荷搜索...")
    positive_charge_results = [item for item in data if 
                             item.get('charge') and 
                             isinstance(item['charge'], (int, float)) and 
                             item['charge'] > 0]
    print(f"  正电荷: {len(positive_charge_results)} 条记录")
    
    # 测试分子量搜索
    print("测试分子量搜索...")
    small_mass_results = [item for item in data if 
                         item.get('mass') and 
                         isinstance(item['mass'], (int, float)) and 
                         item['mass'] < 1000]
    print(f"  小分子量(<1kDa): {len(small_mass_results)} 条记录")
    
    print("✅ 搜索功能测试完成")

def test_categories():
    """测试类目信息"""
    
    print("\n=== 测试类目信息 ===")
    
    categories_file = 'data/index/categories.json'
    if not os.path.exists(categories_file):
        print(f"❌ 类目文件不存在: {categories_file}")
        return False
    
    try:
        with open(categories_file, 'r', encoding='utf-8') as f:
            categories = json.load(f)
        
        print("类目统计:")
        for category_name, category_list in categories.items():
            print(f"  {category_name}: {len(category_list)} 个选项")
            if len(category_list) <= 5:
                print(f"    示例: {category_list[:3]}")
        
        return True
    except Exception as e:
        print(f"❌ 加载类目信息失败: {e}")
        return False

def test_data_quality():
    """测试数据质量"""
    
    print("\n=== 测试数据质量 ===")
    
    index_file = 'data/index/peptide_comprehensive_index.json'
    if not os.path.exists(index_file):
        print("❌ 索引文件不存在")
        return False
    
    with open(index_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 统计各种数据
    total_records = len(data)
    records_with_sequence = len([item for item in data if item.get('sequence')])
    records_with_activity = len([item for item in data if item.get('activity_type')])
    records_with_target = len([item for item in data if item.get('target_organisms')])
    records_with_family = len([item for item in data if item.get('family')])
    records_with_charge = len([item for item in data if item.get('charge')])
    records_with_mass = len([item for item in data if item.get('mass')])
    
    print(f"总记录数: {total_records}")
    print(f"有序列信息: {records_with_sequence} ({records_with_sequence/total_records*100:.1f}%)")
    print(f"有活性信息: {records_with_activity} ({records_with_activity/total_records*100:.1f}%)")
    print(f"有目标生物: {records_with_target} ({records_with_target/total_records*100:.1f}%)")
    print(f"有家族信息: {records_with_family} ({records_with_family/total_records*100:.1f}%)")
    print(f"有电荷信息: {records_with_charge} ({records_with_charge/total_records*100:.1f}%)")
    print(f"有分子量信息: {records_with_mass} ({records_with_mass/total_records*100:.1f}%)")
    
    return True

def main():
    """主测试函数"""
    
    print("开始测试高级搜索功能...\n")
    
    tests = [
        test_comprehensive_index,
        test_search_options,
        test_categories,
        test_data_quality
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
                print("✅ 测试通过\n")
            else:
                print("❌ 测试失败\n")
        except Exception as e:
            print(f"❌ 测试异常: {e}\n")
    
    print(f"=== 测试总结 ===")
    print(f"通过: {passed}/{total}")
    print(f"成功率: {passed/total*100:.1f}%")
    
    if passed == total:
        print("🎉 所有测试通过！高级搜索功能已准备就绪。")
    else:
        print("⚠️  部分测试失败，请检查相关功能。")

if __name__ == "__main__":
    main() 