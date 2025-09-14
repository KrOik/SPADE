#!/usr/bin/env python3
"""
简化的抗菌肽数据处理快速启动器
提供最常用的处理选项
"""

import os
import sys
import subprocess
import json
import time

def get_script_dir():
    """获取脚本所在目录"""
    return os.path.dirname(os.path.abspath(__file__))

def check_system():
    """系统检查"""
    script_dir = get_script_dir()
    # 修改为适配新的数据目录结构
    database_dir = os.path.join(script_dir, "../data/detail")
    result_dir = os.path.join(script_dir, "../data/result")
    index_dir = os.path.join(script_dir, "../data/index")
    
    if not os.path.exists(database_dir):
        print(f"❌ 数据库目录不存在: {database_dir}")
        return False
    
    json_files = [f for f in os.listdir(database_dir) if f.lower().endswith('.json')]
    dramp_files = [f for f in json_files if f.lower().startswith('dramp')]
    
    print(f"✅ 数据库目录: {database_dir}")
    print(f"📁 JSON文件总数: {len(json_files)}")
    print(f"🧬 DRAMP文件数: {len(dramp_files)}")
    
    # 检查结果目录
    if os.path.exists(result_dir):
        result_files = [f for f in os.listdir(result_dir) if f.lower().endswith('.json')]
        print(f"📊 结果文件数: {len(result_files)}")
    else:
        print(f"⚠️ 结果目录不存在，将在处理时创建: {result_dir}")
    
    # 检查索引目录
    if os.path.exists(index_dir):
        index_files = [f for f in os.listdir(index_dir) if f.lower().endswith('.json')]
        print(f"📝 索引文件数: {len(index_files)}")
    else:
        print(f"⚠️ 索引目录不存在，将在处理时创建: {index_dir}")
    
    # 检查依赖
    try:
        import yaml
        print("✅ YAML模块已安装")
    except ImportError:
        print("❌ 缺少YAML模块，请运行: pip install pyyaml")
        return False
    
    return True

def quick_process():
    """快速处理所有数据"""
    script_dir = get_script_dir()
    
    print("🚀 开始快速处理...")
    print("=" * 50)
    
    start_time = time.time()
    
    cmd = [
        sys.executable, "unified_processor.py", "batch",
        "--input", "../data/detail",
        "--output", "../data/result",
        "--mode", "both",
        "--workers", "4"
    ]
    
    result = subprocess.run(cmd, cwd=script_dir)
    
    if result.returncode == 0:
        end_time = time.time()
        duration = end_time - start_time
        print(f"\n✅ 处理完成！用时: {duration:.1f}秒")
        
        # 处理完成后生成索引文件
        print("📝 生成索引文件...")
        _generate_index()
        
        return True
    else:
        print("❌ 处理失败")
        return False

def index_only():
    """仅生成索引"""
    script_dir = get_script_dir()
    
    print("📝 开始生成索引...")
    print("=" * 50)
    
    cmd = [
        sys.executable, "unified_processor.py", "batch",
        "--input", "../data/detail",
        "--output", "../data/result",
        "--mode", "index",
        "--workers", "6"
    ]
    
    result = subprocess.run(cmd, cwd=script_dir)
    
    if result.returncode == 0:
        print("\n✅ 索引生成完成！")
        _generate_index()
        return True
    else:
        print("❌ 索引生成失败")
        return False

def score_only():
    """仅进行评分"""
    script_dir = get_script_dir()
    
    print("📊 开始评分处理...")
    print("=" * 50)
    
    cmd = [
        sys.executable, "unified_processor.py", "batch",
        "--input", "../data/detail",
        "--output", "../data/result",
        "--mode", "score",
        "--workers", "4"
    ]
    
    result = subprocess.run(cmd, cwd=script_dir)
    
    if result.returncode == 0:
        print("\n✅ 评分完成！")
        return True
    else:
        print("❌ 评分失败")
        return False

def _generate_index():
    """生成统一索引文件"""
    script_dir = get_script_dir()
    result_dir = os.path.join(script_dir, "../data/result")
    index_dir = os.path.join(script_dir, "../data/index")
    
    # 确保索引目录存在
    os.makedirs(index_dir, exist_ok=True)
    
    try:
        # 从所有评分文件中提取索引信息
        index_data = []
        
        if not os.path.exists(result_dir):
            print("⚠️ 结果目录不存在，跳过索引生成")
            return False
            
        scored_files = [f for f in os.listdir(result_dir) if f.startswith('scored_') and f.endswith('.json')]
        
        for file in scored_files:
            file_path = os.path.join(result_dir, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 提取索引信息
                entry = {
                    'id': data.get('DRAMP ID') or data.get('SPADE ID'),
                    'name': data.get('Peptide Name', 'N/A'),
                    'sequence': data.get('Sequence', ''),
                    'length': len(data.get('Sequence', '')),
                    'total_score': data.get('total', 0)
                }
                
                if entry['id']:  # 只添加有效ID的条目
                    index_data.append(entry)
                    
            except Exception as e:
                print(f"⚠️ 处理文件 {file} 时出错: {e}")
                continue
        
        # 按评分排序
        index_data.sort(key=lambda x: x.get('total_score', 0), reverse=True)
        
        # 保存索引文件
        index_file = os.path.join(index_dir, 'peptide_index.json')
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 已生成索引文件: {index_file} ({len(index_data)} 条记录)")
        return True
        
    except Exception as e:
        print(f"❌ 生成索引时出错: {e}")
        return False

def optimize_index():
    """优化索引文件（分块处理）"""
    script_dir = get_script_dir()
    
    print("🔧 开始优化索引文件...")
    print("=" * 50)
    
    # 检查索引文件是否存在
    index_file = os.path.join(script_dir, "../data/index/peptide_index.json")
    if not os.path.exists(index_file):
        print("❌ 未找到索引文件，请先运行数据处理")
        return False
    
    cmd = [
        sys.executable, "create_chunked_index.py",
        "--input", "../data/index/peptide_index.json",
        "--output", "../js/chunks",
        "--chunk-size", "5000"
    ]
    
    result = subprocess.run(cmd, cwd=script_dir)
    
    if result.returncode == 0:
        print("\n✅ 索引优化完成！")
        
        # 复制索引文件到js目录
        src_index = os.path.join(script_dir, "../data/index/peptide_index.json")
        dst_index = os.path.join(script_dir, "../js/peptide_index.json")
        
        try:
            import shutil
            os.makedirs(os.path.dirname(dst_index), exist_ok=True)
            shutil.copy2(src_index, dst_index)
            print(f"✅ 已复制索引文件到: {dst_index}")
        except Exception as e:
            print(f"⚠️ 复制索引文件时出错: {e}")
        
        return True
    else:
        print("❌ 索引优化失败")
        return False

def create_page_cache():
    """生成分页缓存（解决翻页加载问题）"""
    script_dir = get_script_dir()
    
    print("📄 开始生成分页缓存...")
    print("=" * 50)
    
    # 检查数据库目录
    database_dir = os.path.join(script_dir, "../data/detail")
    if not os.path.exists(database_dir):
        print("❌ 数据库目录不存在")
        return False
    
    json_files = [f for f in os.listdir(database_dir) if f.lower().endswith('.json')]
    if len(json_files) == 0:
        print("❌ 数据库目录中没有JSON文件")
        return False
    
    print(f"📁 找到 {len(json_files)} 个JSON文件")
    
    # 确保js目录存在（根据规则，.js文件应放在SPADE/js）
    cache_dir = os.path.join(script_dir, "../js/PageCache")
    os.makedirs(cache_dir, exist_ok=True)
    
    cmd = [
        sys.executable, "create_page_cache.py",
        "--input", "../data/detail",
        "--output", cache_dir,
        "--items-per-page", "10",
        "--workers", "6"
    ]
    
    result = subprocess.run(cmd, cwd=script_dir)
    
    if result.returncode == 0:
        print("\n✅ 分页缓存生成完成！")
        
        # 检查生成的文件
        if os.path.exists(cache_dir):
            page_files = [f for f in os.listdir(cache_dir) if f.startswith('page_')]
            metadata_file = os.path.join(cache_dir, 'cache_metadata.json')
            quick_index_file = os.path.join(cache_dir, 'quick_index.json')
            
            print(f"   分页文件: {len(page_files)} 个")
            print(f"   元数据文件: {'✓' if os.path.exists(metadata_file) else '✗'}")
            print(f"   快速索引: {'✓' if os.path.exists(quick_index_file) else '✗'}")
            
            # 显示总页数信息
            if os.path.exists(metadata_file):
                try:
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                    print(f"   总页数: {metadata.get('total_pages', 'Unknown')}")
                    print(f"   总条目: {metadata.get('total_items', 'Unknown')}")
                except:
                    pass
        
        return True
    else:
        print("❌ 分页缓存生成失败")
        return False

def test_page_cache():
    """测试分页缓存的完整性"""
    script_dir = get_script_dir()
    
    print("🧪 开始测试分页缓存...")
    print("=" * 50)
    
    # 检查缓存目录
    cache_dir = os.path.join(script_dir, "../js/PageCache")
    if not os.path.exists(cache_dir):
        print("❌ 分页缓存目录不存在")
        print("💡 请先运行 '生成分页缓存' 选项")
        return False
    
    cmd = [
        sys.executable, "test_page_cache.py",
        cache_dir
    ]
    
    result = subprocess.run(cmd, cwd=script_dir)
    
    if result.returncode == 0:
        print("\n🎉 分页缓存测试通过！")
        print("💡 现在可以在search.html中使用分页缓存了")
        return True
    else:
        print("\n❌ 分页缓存测试失败！")
        print("🔧 建议重新生成分页缓存")
        return False

def check_results():
    """检查处理结果"""
    script_dir = get_script_dir()
    result_dir = os.path.join(script_dir, "../data/result")
    index_dir = os.path.join(script_dir, "../data/index")
    
    print("📂 检查处理结果...")
    print("=" * 50)
    
    # 检查结果目录
    if not os.path.exists(result_dir):
        print("❌ 结果目录不存在")
        return
    
    print(f"📂 结果目录: {result_dir}")
    
    files = os.listdir(result_dir)
    scored_files = [f for f in files if f.startswith('scored_')]
    summary_files = [f for f in files if f == 'all_scores.json']
    
    print(f"📊 评分文件: {len(scored_files)}")
    print(f"📈 汇总文件: {len(summary_files)}")
    
    # 检查索引目录
    if os.path.exists(index_dir):
        index_files = os.listdir(index_dir)
        print(f"📝 索引文件: {len(index_files)}")
        for f in index_files:
            print(f"   - {f}")
    else:
        print("📝 索引目录不存在")
    
    # 检查分块索引
    chunks_dir = os.path.join(script_dir, "../js/chunks")
    if os.path.exists(chunks_dir):
        chunk_files = [f for f in os.listdir(chunks_dir) if f.startswith('index_chunk_')]
        print(f"🧩 分块索引: {len(chunk_files)} 个块")
    else:
        print("🧩 分块索引目录不存在")
    
    # 显示评分汇总
    all_scores_path = os.path.join(result_dir, "all_scores.json")
    if os.path.exists(all_scores_path):
        try:
            with open(all_scores_path, 'r', encoding='utf-8') as f:
                scores_data = json.load(f)
            
            print(f"\n📈 评分汇总统计:")
            print(f"   总条目数: {len(scores_data)}")
            
            if scores_data:
                total_scores = [item.get('total', 0) for item in scores_data]
                avg_score = sum(total_scores) / len(total_scores)
                max_score = max(total_scores)
                min_score = min(total_scores)
                
                print(f"   平均总分: {avg_score:.2f}")
                print(f"   最高总分: {max_score:.2f}")
                print(f"   最低总分: {min_score:.2f}")
                
                # 显示前3名
                print(f"\n🏆 前3名肽:")
                for i, item in enumerate(scores_data[:3]):
                    primary_id = item.get('Primary ID', 'N/A')
                    total = item.get('total', 0)
                    sequence = item.get('Sequence', '')[:20] + ('...' if len(item.get('Sequence', '')) > 20 else '')
                    print(f"   {i+1}. {primary_id}: {total:.2f} ({sequence})")
                    
        except Exception as e:
            print(f"❌ 读取评分汇总文件时出错: {e}")
    else:
        print("📈 评分汇总文件不存在")

def main():
    """主菜单"""
    print("\n" + "🧬" * 20)
    print("  抗菌肽数据处理工具 - 快速启动")
    print("🧬" * 20)
    
    while True:
        print("\n选择操作:")
        print("1️⃣  系统检查")
        print("2️⃣  快速处理 (评分+索引)")
        print("3️⃣  仅生成索引")
        print("4️⃣  仅进行评分") 
        print("5️⃣  优化索引 (分块处理)")
        print("6️⃣  生成分页缓存 (解决翻页问题)")
        print("7️⃣  测试分页缓存")
        print("8️⃣  检查结果")
        print("9️⃣  退出")
        print("-" * 30)
        
        choice = input("请输入选择 [1-9]: ").strip()
        
        if choice == "1":
            if check_system():
                print("✅ 系统检查通过")
            else:
                print("❌ 系统检查失败")
                
        elif choice == "2":
            if check_system():
                if quick_process():
                    print("\n🚀 是否要优化索引文件以提升搜索性能？")
                    optimize_choice = input("输入 y 继续优化，其他键跳过: ").strip().lower()
                    if optimize_choice == 'y':
                        optimize_index()
            else:
                print("❌ 系统检查失败，无法处理")
                
        elif choice == "3":
            if check_system():
                if index_only():
                    print("\n🚀 是否要优化索引文件以提升搜索性能？")
                    optimize_choice = input("输入 y 继续优化，其他键跳过: ").strip().lower()
                    if optimize_choice == 'y':
                        optimize_index()
            else:
                print("❌ 系统检查失败，无法处理")
                
        elif choice == "4":
            if check_system():
                score_only()
            else:
                print("❌ 系统检查失败，无法处理")
                
        elif choice == "5":
            optimize_index()
            
        elif choice == "6":
            create_page_cache()
            
        elif choice == "7":
            test_page_cache()
            
        elif choice == "8":
            check_results()
            
        elif choice == "9":
            print("👋 再见！")
            break
            
        else:
            print("❌ 无效选择，请重试")

if __name__ == "__main__":
    main() 