import json
import os
from typing import Dict, Any, List

def split_spade_data(source_path: str, target_dir: str) -> None:
    """
    从SPADE.json文件中拆分抗菌肽数据并保存到指定目录
    
    参数:
    source_path (str): 源JSON文件路径
    target_dir (str): 目标保存目录
    """
    # 确保主目标目录存在
    os.makedirs(target_dir, exist_ok=True)
    
    # 创建SPADE_N和SPADE_UN子目录
    spade_n_dir = os.path.join(target_dir, "SPADE_N")
    spade_un_dir = os.path.join(target_dir, "SPADE_UN")
    os.makedirs(spade_n_dir, exist_ok=True)
    os.makedirs(spade_un_dir, exist_ok=True)
    
    try:
        # 读取源JSON文件
        with open(source_path, 'r', encoding='utf-8') as f:
            spade_data = json.load(f)
        
        # 遍历数据中的每个条目
        for key, value in spade_data.items():
            # 检查条目是否包含Sequence Information
            if "Sequence Information" in value:
                # 获取SPADE ID作为文件名
                spade_id = value["Sequence Information"].get("SPADE ID", key)
                
                # 根据ID前缀确定保存目录
                if spade_id.startswith("SPADE_N_"):
                    save_dir = spade_n_dir
                elif spade_id.startswith("SPADE_UN_"):
                    save_dir = spade_un_dir
                else:
                    # 如果ID前缀不是SPADE_N_或SPADE_UN_，使用主目录
                    save_dir = target_dir
                
                # 构建目标文件路径
                target_file = os.path.join(save_dir, f"{spade_id}.json")
                
                # 保存数据到单独的JSON文件
                with open(target_file, 'w', encoding='utf-8') as f:
                    json.dump({key: value}, f, ensure_ascii=False, indent=4)
                
                print(f"已保存: {target_file}")
    
    except FileNotFoundError:
        print(f"错误: 找不到源文件 {source_path}")
    except json.JSONDecodeError:
        print(f"错误: 文件 {source_path} 不是有效的JSON格式")
    except Exception as e:
        print(f"发生未知错误: {e}")

if __name__ == "__main__":
    # 源文件路径和目标目录
    source_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'load', 'SPADE.json'))
    target_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'detail'))
    
    # 执行数据拆分
    split_spade_data(source_file, target_directory)    