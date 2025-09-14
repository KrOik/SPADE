
/**
 * 分块索引加载器
 * 自动生成的文件，请勿手动修改
 */

class ChunkedIndexLoader {
    constructor() {
        this.chunks = new Map();
        this.totalChunks = 47;
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
