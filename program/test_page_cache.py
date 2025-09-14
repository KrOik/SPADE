#!/usr/bin/env python3
"""
分页缓存测试脚本
验证分页缓存的正确性和完整性
"""

import os
import json
import sys
from pathlib import Path

def test_page_cache(cache_dir):
    """测试分页缓存的完整性"""
    cache_path = Path(cache_dir)
    
    if not cache_path.exists():
        print(f"❌ 缓存目录不存在: {cache_dir}")
        return False
    
    print("🧪 开始测试分页缓存...")
    print("=" * 50)
    
    # 1. 检查元数据文件
    metadata_file = cache_path / 'cache_metadata.json'
    if not metadata_file.exists():
        print("❌ 元数据文件不存在")
        return False
    
    with open(metadata_file, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    
    print(f"📊 元数据信息:")
    print(f"   总条目数: {metadata['total_items']}")
    print(f"   总页数: {metadata['total_pages']}")
    print(f"   每页条目: {metadata['items_per_page']}")
    print(f"   生成时间: {metadata['generated_at']}")
    
    # 2. 检查页面文件完整性
    print(f"\n📄 检查页面文件完整性...")
    missing_pages = []
    total_items_found = 0
    
    for page_num in range(1, metadata['total_pages'] + 1):
        page_file = cache_path / f"page_{page_num:06d}.json"
        
        if not page_file.exists():
            missing_pages.append(page_num)
            continue
        
        try:
            with open(page_file, 'r', encoding='utf-8') as f:
                page_data = json.load(f)
            
            # 验证页面数据结构
            required_fields = ['page_number', 'total_pages', 'data']
            for field in required_fields:
                if field not in page_data:
                    print(f"⚠️ 页面 {page_num} 缺少字段: {field}")
            
            # 统计条目数
            if 'data' in page_data:
                total_items_found += len(page_data['data'])
            
            # 验证页码正确性
            if page_data.get('page_number') != page_num:
                print(f"⚠️ 页面 {page_num} 的页码不匹配: {page_data.get('page_number')}")
            
        except Exception as e:
            print(f"❌ 页面 {page_num} 数据格式错误: {e}")
    
    if missing_pages:
        print(f"❌ 缺失页面: {missing_pages}")
        return False
    else:
        print(f"✅ 所有 {metadata['total_pages']} 个页面文件完整")
    
    # 3. 验证总条目数
    print(f"\n🔢 验证条目数:")
    print(f"   元数据中的总条目: {metadata['total_items']}")
    print(f"   实际统计的条目: {total_items_found}")
    
    if total_items_found != metadata['total_items']:
        print(f"⚠️ 条目数不匹配！")
    else:
        print(f"✅ 条目数匹配")
    
    # 4. 检查快速索引
    quick_index_file = cache_path / 'quick_index.json'
    if quick_index_file.exists():
        print(f"\n⚡ 检查快速索引...")
        
        try:
            with open(quick_index_file, 'r', encoding='utf-8') as f:
                quick_index = json.load(f)
            
            print(f"   索引条目数: {len(quick_index)}")
            
            # 随机检查几个索引条目
            sample_count = min(5, len(quick_index))
            sample_ids = list(quick_index.keys())[:sample_count]
            
            for sample_id in sample_ids:
                index_info = quick_index[sample_id]
                page_num = index_info['page']
                
                # 验证页面文件中确实包含该ID
                page_file = cache_path / f"page_{page_num:06d}.json"
                with open(page_file, 'r', encoding='utf-8') as f:
                    page_data = json.load(f)
                
                found = False
                for item in page_data['data']:
                    if item.get('id') == sample_id:
                        found = True
                        break
                
                if found:
                    print(f"   ✅ {sample_id} -> 第{page_num}页")
                else:
                    print(f"   ❌ {sample_id} -> 第{page_num}页 (未找到)")
            
        except Exception as e:
            print(f"❌ 快速索引检查失败: {e}")
    else:
        print(f"⚠️ 快速索引文件不存在")
    
    # 5. 测试随机页面加载
    print(f"\n🎲 测试随机页面加载...")
    test_pages = [1, metadata['total_pages'] // 2, metadata['total_pages']]
    
    for page_num in test_pages:
        if page_num <= metadata['total_pages']:
            page_file = cache_path / f"page_{page_num:06d}.json"
            try:
                with open(page_file, 'r', encoding='utf-8') as f:
                    page_data = json.load(f)
                
                item_count = len(page_data.get('data', []))
                print(f"   第{page_num}页: {item_count} 条目")
                
                # 检查数据字段完整性
                if page_data.get('data'):
                    sample_item = page_data['data'][0]
                    required_item_fields = ['id', 'name', 'sequence']
                    missing_fields = [f for f in required_item_fields if f not in sample_item]
                    
                    if missing_fields:
                        print(f"     ⚠️ 条目缺少字段: {missing_fields}")
                    else:
                        print(f"     ✅ 数据字段完整")
                
            except Exception as e:
                print(f"   ❌ 第{page_num}页加载失败: {e}")
    
    print("\n" + "=" * 50)
    
    # 总结
    if not missing_pages and total_items_found == metadata['total_items']:
        print("🎉 分页缓存测试通过！")
        print("💡 建议:")
        print("   1. 在search.html中启用分页缓存")
        print("   2. 测试翻页性能")
        print("   3. 验证搜索功能")
        return True
    else:
        print("❌ 分页缓存测试失败！")
        print("🔧 建议:")
        print("   1. 重新生成分页缓存")
        print("   2. 检查源数据完整性")
        print("   3. 验证脚本配置")
        return False

def main():
    if len(sys.argv) != 2:
        print("用法: python test_page_cache.py <缓存目录路径>")
        print("例如: python test_page_cache.py ../WebPage/PageCache")
        return
    
    cache_dir = sys.argv[1]
    success = test_page_cache(cache_dir)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 