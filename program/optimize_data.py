#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据优化处理器
将肽数据分离为基础数据和扩展数据，并生成分块索引文件
"""

import json
import os
import re
import time
import shutil
from pathlib import Path
from typing import Dict, Any, List, Union, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse
import sys
from functools import partial

def find_value_in_dict(data: Any, target_key: str) -> Optional[Any]:
    """递归搜索嵌套字典或列表中的键"""
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

class DataOptimizer:
    """肽数据优化处理器"""
    
    def __init__(self):
        self.basic_fields = [
            "SPADE ID", "DRAMP ID", "Peptide Name", "Sequence", "Source", 
            "Biological Activity", "Target Organism", "Linear/Cyclic", "Sequence Length"
        ]
        
    def process_single_file(self, file_path: str) -> Tuple[Optional[Dict], Optional[Dict]]:
        """
        处理单个JSON文件，分离基础数据和扩展数据
        
        Args:
            file_path: 文件路径
            
        Returns:
            (基础数据, 扩展数据) 的元组
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 获取主键（通常是SPADE_N_XXXXX或SPADE_UN_XXXXX）
            if not data or not isinstance(data, dict) or len(data.keys()) == 0:
                print(f"警告：文件 {file_path} 格式不正确")
                return None, None
                
            primary_key = list(data.keys())[0]
            
            # 创建基础数据
            basic_data = {primary_key: {}}
            extended_data = {primary_key: {}}
            
            # 处理序列信息
            seq_info = data[primary_key].get("Sequence Information", {})
            if seq_info:
                basic_data[primary_key]["basic"] = {}
                
                # 提取基础字段
                for field in self.basic_fields:
                    if field in seq_info:
                        basic_data[primary_key]["basic"][field] = seq_info[field]
                
                # 添加扩展数据URL
                basic_data[primary_key]["extended_data_url"] = f"{primary_key}_extended.json"
                
                # 复制所有数据到扩展数据
                extended_data[primary_key] = data[primary_key]
            
            return basic_data, extended_data
            
        except Exception as e:
            print(f"处理文件 {file_path} 时出错: {str(e)}")
            return None, None
    
    def batch_process(self, input_dir: str, output_dir: str, 
                     max_workers: int = 4, chunk_size: int = 1000) -> Dict[str, Any]:
        """
        批量处理文件
        
        Args:
            input_dir: 输入目录
            output_dir: 输出目录
            max_workers: 最大工作线程数
            chunk_size: 索引分块大小
            
        Returns:
            处理结果统计
        """
        # 路径处理
        input_dir = os.path.abspath(input_dir)
        output_dir = os.path.abspath(output_dir)
        
        if not os.path.exists(input_dir):
            raise FileNotFoundError(f"输入目录不存在: {input_dir}")
        
        # 创建输出目录结构
        basic_dir = os.path.join(output_dir, "basic")
        extended_dir = os.path.join(output_dir, "extended")
        chunks_dir = os.path.join(output_dir, "chunks")
        
        os.makedirs(basic_dir, exist_ok=True)
        os.makedirs(extended_dir, exist_ok=True)
        os.makedirs(chunks_dir, exist_ok=True)
        
        # 获取文件列表
        json_files = []
        for root, _, files in os.walk(input_dir):
            for f in files:
                if f.lower().endswith('.json'):
                    if f.lower().startswith(('spade_n_', 'spade_un_', 'dramp')):
                        json_files.append(os.path.join(root, f))
        
        print(f"找到 {len(json_files)} 个匹配的JSON文件")
        print(f"使用 {max_workers} 个线程进行并行处理")
        
        # 初始化结果容器
        all_index_entries = []
        processed_count = 0
        error_count = 0
        
        # 多线程处理
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交任务
            future_to_file = {}
            for json_file in json_files:
                future = executor.submit(self.process_single_file, json_file)
                future_to_file[future] = json_file
            
            # 收集结果
            for future in as_completed(future_to_file):
                json_file = future_to_file[future]
                filename = os.path.basename(json_file)
                
                try:
                    basic_data, extended_data = future.result()
                    
                    if basic_data and extended_data:
                        processed_count += 1
                        
                        # 提取ID用于索引
                        primary_key = list(basic_data.keys())[0]
                        basic_info = basic_data[primary_key].get("basic", {})
                        
                        # 创建索引条目
                        index_entry = {
                            "id": basic_info.get("SPADE ID") or basic_info.get("DRAMP ID") or primary_key,
                            "name": basic_info.get("Peptide Name", "N/A"),
                            "sequence": basic_info.get("Sequence", ""),
                            "length": basic_info.get("Sequence Length", len(basic_info.get("Sequence", ""))),
                            "activity": basic_info.get("Biological Activity", [])
                        }
                        
                        all_index_entries.append(index_entry)
                        
                        # 保存基础数据
                        basic_file = os.path.join(basic_dir, filename)
                        with open(basic_file, 'w', encoding='utf-8') as f:
                            json.dump(basic_data, f, ensure_ascii=False)
                        
                        # 保存扩展数据
                        extended_file = os.path.join(extended_dir, f"{primary_key}_extended.json")
                        with open(extended_file, 'w', encoding='utf-8') as f:
                            json.dump(extended_data, f, ensure_ascii=False)
                        
                        if processed_count % 100 == 0:
                            print(f"已处理 {processed_count} 个文件...")
                    else:
                        error_count += 1
                        
                except Exception as e:
                    print(f"处理文件 {json_file} 时出错: {str(e)}")
                    error_count += 1
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # 生成分块索引文件
        print("生成分块索引文件...")
        self._generate_chunked_index(all_index_entries, chunks_dir, chunk_size)
        
        # 保存汇总结果
        results = {
            "processed_files": processed_count,
            "error_files": error_count,
            "total_files": len(json_files),
            "processing_time": processing_time,
            "files_per_second": processed_count / processing_time if processing_time > 0 else 0,
            "index_entries": len(all_index_entries)
        }
        
        print(f"批量处理完成: {processed_count}/{len(json_files)} 个文件处理成功，{error_count} 个文件出错")
        print(f"处理时间: {processing_time:.2f}秒，处理速度: {results['files_per_second']:.2f} 文件/秒")
        
        return results
    
    def _generate_chunked_index(self, index_entries: List[Dict], output_dir: str, chunk_size: int = 1000):
        """
        生成分块索引文件
        
        Args:
            index_entries: 索引条目列表
            output_dir: 输出目录
            chunk_size: 每个块的大小
        """
        # 按ID排序
        index_entries.sort(key=lambda x: x.get("id", ""))
        
        # 计算块数
        total_entries = len(index_entries)
        total_chunks = (total_entries + chunk_size - 1) // chunk_size
        
        chunk_files = []
        
        # 生成分块文件
        for i in range(total_chunks):
            start_idx = i * chunk_size
            end_idx = min((i + 1) * chunk_size, total_entries)
            
            chunk_data = index_entries[start_idx:end_idx]
            chunk_file = f"index_chunk_{i}.json"
            chunk_path = os.path.join(output_dir, chunk_file)
            
            with open(chunk_path, 'w', encoding='utf-8') as f:
                json.dump(chunk_data, f, ensure_ascii=False)
            
            chunk_files.append(chunk_file)
            print(f"已生成索引块 {i+1}/{total_chunks}")
        
        # 生成元数据文件
        metadata = {
            "total_entries": total_entries,
            "chunk_size": chunk_size,
            "total_chunks": total_chunks,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "chunks": chunk_files
        }
        
        metadata_path = os.path.join(output_dir, "index_metadata.json")
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        print(f"索引元数据已保存到 {metadata_path}")
        
        # 复制加载器脚本
        loader_script = """
/**
 * 分块索引加载器
 * 自动生成的文件，请勿手动修改
 */

class ChunkedIndexLoader {
    constructor() {
        this.chunks = new Map();
        this.totalChunks = %d;
        this.loadedChunks = new Set();
        this.baseUrl = './chunks/';
        this.metadata = null;
    }
    
    async init() {
        try {
            const response = await fetch(`${this.baseUrl}index_metadata.json`);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            this.metadata = await response.json();
            this.totalChunks = this.metadata.total_chunks;
            return this.metadata;
        } catch (error) {
            console.error('加载索引元数据失败:', error);
            return null;
        }
    }
    
    async loadChunk(chunkIndex) {
        if (this.loadedChunks.has(chunkIndex)) {
            return this.chunks.get(chunkIndex);
        }
        
        try {
            const response = await fetch(`${this.baseUrl}index_chunk_${chunkIndex}.json`);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            const chunkData = await response.json();
            this.chunks.set(chunkIndex, chunkData);
            this.loadedChunks.add(chunkIndex);
            
            return chunkData;
        } catch (error) {
            console.error(`加载索引块 ${chunkIndex} 失败:`, error);
            return null;
        }
    }
    
    async loadAllChunks() {
        if (!this.metadata) {
            await this.init();
        }
        
        const promises = [];
        for (let i = 0; i < this.totalChunks; i++) {
            promises.push(this.loadChunk(i));
        }
        
        const results = await Promise.allSettled(promises);
        const allData = [];
        
        results.forEach((result, index) => {
            if (result.status === 'fulfilled' && result.value) {
                allData.push(...result.value);
            } else {
                console.warn(`块 ${index} 加载失败`);
            }
        });
        
        return allData;
    }
    
    async searchInChunks(searchTerm, field = 'name') {
        if (!this.metadata) {
            await this.init();
        }
        
        const results = [];
        const searchLower = searchTerm.toLowerCase();
        
        for (let i = 0; i < this.totalChunks; i++) {
            const chunk = await this.loadChunk(i);
            if (chunk) {
                const matches = chunk.filter(item => {
                    const value = item[field];
                    return value && (typeof value === 'string' ? 
                        value.toLowerCase().includes(searchLower) : 
                        JSON.stringify(value).toLowerCase().includes(searchLower));
                });
                results.push(...matches);
            }
        }
        
        return results;
    }
    
    async getEntryById(id) {
        if (!this.metadata) {
            await this.init();
        }
        
        // 简单的二分查找算法确定可能的块
        // 这里假设ID是按字母顺序排序的
        const idLower = id.toLowerCase();
        
        // 先尝试加载所有块的第一个和最后一个条目来确定范围
        const boundaries = [];
        for (let i = 0; i < this.totalChunks; i++) {
            const chunk = await this.loadChunk(i);
            if (chunk && chunk.length > 0) {
                boundaries.push({
                    chunkIndex: i,
                    firstId: chunk[0].id.toLowerCase(),
                    lastId: chunk[chunk.length - 1].id.toLowerCase()
                });
            }
        }
        
        // 在确定的块中搜索
        for (const boundary of boundaries) {
            if (idLower >= boundary.firstId && idLower <= boundary.lastId) {
                const chunk = await this.loadChunk(boundary.chunkIndex);
                if (chunk) {
                    const entry = chunk.find(item => item.id.toLowerCase() === idLower);
                    if (entry) {
                        return entry;
                    }
                }
            }
        }
        
        // 如果没找到，尝试在所有块中搜索
        for (let i = 0; i < this.totalChunks; i++) {
            const chunk = await this.loadChunk(i);
            if (chunk) {
                const entry = chunk.find(item => item.id.toLowerCase() === idLower);
                if (entry) {
                    return entry;
                }
            }
        }
        
        return null;
    }
}

// 全局实例
window.chunkedIndexLoader = new ChunkedIndexLoader();
""" % total_chunks
        
        loader_path = os.path.join(output_dir, "chunked_loader.js")
        with open(loader_path, 'w', encoding='utf-8') as f:
            f.write(loader_script)
        
        print(f"加载器脚本已保存到 {loader_path}")
        
        # 生成集成指南
        guide = """
# 分块索引集成指南

## 1. 文件结构
```
chunks/
├── index_chunk_0.json
├── index_chunk_1.json
├── ...
├── index_metadata.json
└── chunked_loader.js
```

## 2. 在HTML中引入
```html
<script src="./chunks/chunked_loader.js"></script>
```

## 3. 使用方法

### 初始化
```javascript
// 初始化加载器并获取元数据
await window.chunkedIndexLoader.init();
```

### 加载单个块
```javascript
const chunk = await window.chunkedIndexLoader.loadChunk(0);
```

### 加载所有数据（适用于小数据集）
```javascript
const allData = await window.chunkedIndexLoader.loadAllChunks();
```

### 搜索功能
```javascript
// 按名称搜索
const results = await window.chunkedIndexLoader.searchInChunks('keyword', 'name');

// 按序列搜索
const results = await window.chunkedIndexLoader.searchInChunks('ACDE', 'sequence');

// 按ID精确查找
const entry = await window.chunkedIndexLoader.getEntryById('SPADE_N_00001');
```

## 4. 性能优化建议

1. **按需加载**: 只加载当前页面需要的块
2. **缓存策略**: 使用浏览器缓存或IndexedDB缓存已加载的块
3. **搜索优化**: 对于大数据集，考虑使用Web Workers进行搜索
4. **预加载**: 预加载下一页可能需要的块

## 5. 错误处理

加载器已内置错误处理，会自动跳过失败的块。建议在应用层面也加入相应的错误处理逻辑。

## 6. 数据结构说明

### 基础数据文件 (basic/SPADE_N_00001.json)
```json
{
  "SPADE_N_00001": {
    "basic": {
      "SPADE ID": "SPADE_N_00001",
      "Peptide Name": "Variacin (Bacteriocin)",
      "Sequence": "GSGVIPTISHECHMNSFQFVFTCCS",
      "Source": "Micrococcus varians (Gram-positive bacteria)",
      "Biological Activity": ["Antimicrobial", "Antibacterial", "Anti-Gram+"],
      "Target Organism": "Gram-positive bacteria...",
      "Linear/Cyclic": "Linear",
      "Sequence Length": 25
    },
    "extended_data_url": "SPADE_N_00001_extended.json"
  }
}
```

### 扩展数据文件 (extended/SPADE_N_00001_extended.json)
包含完整的肽数据信息，与原始数据结构相同。

### 索引块文件 (chunks/index_chunk_0.json)
```json
[
  {
    "id": "SPADE_N_00001",
    "name": "Variacin (Bacteriocin)",
    "sequence": "GSGVIPTISHECHMNSFQFVFTCCS",
    "length": 25,
    "activity": ["Antimicrobial", "Antibacterial", "Anti-Gram+"]
  },
  ...
]
```

### 元数据文件 (chunks/index_metadata.json)
```json
{
  "total_entries": 1000,
  "chunk_size": 100,
  "total_chunks": 10,
  "created_at": "2023-06-01 12:00:00",
  "chunks": ["index_chunk_0.json", ...]
}
```
"""
        
        guide_path = os.path.join(output_dir, "integration_guide.md")
        with open(guide_path, 'w', encoding='utf-8') as f:
            f.write(guide)
        
        print(f"集成指南已保存到 {guide_path}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="肽数据优化工具")
    parser.add_argument("--input", help="输入目录", default="../data/detail")
    parser.add_argument("--output", help="输出目录", default="../data/optimized")
    parser.add_argument("--workers", help="并行工作线程数", type=int, default=4)
    parser.add_argument("--chunk-size", help="索引分块大小", type=int, default=1000)
    
    args = parser.parse_args()
    
    optimizer = DataOptimizer()
    results = optimizer.batch_process(
        input_dir=args.input,
        output_dir=args.output,
        max_workers=args.workers,
        chunk_size=args.chunk_size
    )
    
    print("\n处理结果统计:")
    for key, value in results.items():
        print(f"  {key}: {value}")

if __name__ == "__main__":
    main()