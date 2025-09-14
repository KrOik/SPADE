#!/usr/bin/env python3
"""
运行增强评分系统的便捷脚本
基于实际实验数据为data/detail中的抗菌肽进行评分
"""

import os
import sys
import time
from pathlib import Path

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from enhanced_scoring import EnhancedScoring

def main():
    """主函数"""
    print("=== SPADE 增强评分系统 ===")
    print("基于实际实验数据的抗菌肽评分")
    print()
    
    # 设置路径
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    input_dir = project_root / "data" / "detail"
    output_dir = project_root / "data" / "result"
    
    print(f"输入目录: {input_dir}")
    print(f"输出目录: {output_dir}")
    print()
    
    # 检查输入目录
    if not input_dir.exists():
        print(f"错误：输入目录不存在 - {input_dir}")
        sys.exit(1)
    
    # 创建输出目录
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 初始化评分系统
    print("初始化增强评分系统...")
    scorer = EnhancedScoring()
    
    # 显示权重配置
    print("\n评分权重配置:")
    for category, weight in scorer.weights.items():
        print(f"  {category}: {weight:.2%}")
    
    print(f"\n开始处理目录: {input_dir}")
    start_time = time.time()
    
    try:
        # 处理所有文件
        results = scorer.process_directory(input_dir, output_dir, max_workers=4)
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        print(f"\n=== 处理完成 ===")
        print(f"处理时间: {elapsed_time:.2f} 秒")
        print(f"成功处理: {results['processed']} 个文件")
        print(f"处理错误: {results['errors']} 个文件")
        
        if results['processed'] > 0:
            print(f"平均处理速度: {results['processed']/elapsed_time:.2f} 文件/秒")
        
        # 显示错误摘要
        if results['errors'] > 0:
            print(f"\n错误摘要 (显示前5个):")
            for i, error in enumerate(results['error_files'][:5]):
                print(f"  {i+1}. {error}")
            if len(results['error_files']) > 5:
                print(f"  ... 还有 {len(results['error_files']) - 5} 个错误")
        
        # 生成索引文件
        generate_peptide_index(output_dir)
        
        print(f"\n结果已保存到: {output_dir}")
        print("增强评分处理完成！")
        
    except KeyboardInterrupt:
        print("\n用户中断处理")
        sys.exit(1)
    except Exception as e:
        print(f"\n处理过程中出错: {e}")
        sys.exit(1)

def generate_peptide_index(output_dir: Path):
    """生成肽索引文件"""
    print("\n生成索引文件...")
    
    index_entries = []
    scored_files = list(output_dir.glob("scored_*.json"))
    
    for scored_file in scored_files:
        try:
            import json
            with open(scored_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 提取基本信息
            dramp_id = data.get("DRAMP ID", "")
            total_score = data.get("total", 0)
            category = data.get("category", "")
            
            # 创建索引条目
            index_entry = {
                "id": dramp_id,
                "spade_id": None,  # SPADE ID在新系统中不适用
                "dramp_id": dramp_id,
                "name": f"AMP {dramp_id}",  # 简化名称
                "sequence": data.get("features", {}).get("sequence", ""),
                "length": len(data.get("features", {}).get("sequence", "")),
                "total_score": total_score,
                "category": category,
                "filename": f"{dramp_id}.json"
            }
            
            index_entries.append(index_entry)
            
        except Exception as e:
            print(f"  警告：处理文件 {scored_file} 时出错: {e}")
    
    # 按总分排序
    index_entries.sort(key=lambda x: x["total_score"], reverse=True)
    
    # 保存索引文件
    index_file = output_dir / "peptide_index.json"
    with open(index_file, 'w', encoding='utf-8') as f:
        import json
        json.dump(index_entries, f, indent=2, ensure_ascii=False)
    
    print(f"索引文件已保存: {index_file}")
    print(f"索引包含 {len(index_entries)} 个条目")

def show_sample_result(output_dir: Path):
    """显示示例结果"""
    scored_files = list(output_dir.glob("scored_*.json"))
    if scored_files:
        sample_file = scored_files[0]
        print(f"\n示例结果 ({sample_file.name}):")
        
        try:
            import json
            with open(sample_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print(f"  DRAMP ID: {data.get('DRAMP ID', 'N/A')}")
            print(f"  总分: {data.get('total', 0):.2f}")
            print(f"  评级: {data.get('category', 'N/A')}")
            print("  详细评分:")
            for category, score in data.get('scores', {}).items():
                print(f"    {category}: {score:.2f}")
                
        except Exception as e:
            print(f"  无法读取示例文件: {e}")

if __name__ == "__main__":
    main() 