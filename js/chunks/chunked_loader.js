
/**
 * 分块索引加载器
 * 自动生成的文件，请勿手动修改
 */

class ChunkedIndexLoader {
    constructor() {
        this.chunks = new Map();
        this.totalChunks = 1;
        this.loadedChunks = new Set();
        this.baseUrl = './js/chunks/';
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
        const results = [];
        const searchLower = searchTerm.toLowerCase();
        
        for (let i = 0; i < this.totalChunks; i++) {
            const chunk = await this.loadChunk(i);
            if (chunk) {
                const matches = chunk.filter(item => {
                    const value = item[field];
                    return value && value.toLowerCase().includes(searchLower);
                });
                results.push(...matches);
            }
        }
        
        return results;
    }
}

// 全局实例
window.chunkedIndexLoader = new ChunkedIndexLoader();
