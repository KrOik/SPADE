# SPADE Serverless Functions 部署说明

## 概述

本文档说明如何将SPADE项目的Python处理脚本部署为serverless functions，主要针对Netlify Functions平台。

## 文件结构

```
SPADE/
├── program/
│   ├── functions/
│   │   └── peptide-processor.js    # Netlify Functions入口
│   ├── serverless_processor.py     # Python处理核心
│   ├── netlify.toml                # Netlify配置
│   ├── package.json                # Node.js依赖
│   └── requirements.txt            # Python依赖
├── test/
│   └── test-serverless.js          # 测试文件
└── readme/
    └── [此文件]
```

## 功能说明

### 1. 核心功能

- **单个肽数据处理** (`action: "process"`)
  - 评分计算
  - 等级评定
  - 分子特性分析

- **索引条目创建** (`action: "index"`)
  - 提取关键信息
  - 创建检索条目

- **批量处理** (`action: "batch"`)
  - 同时处理多个肽数据
  - 错误统计和报告

### 2. API接口

#### 端点
```
POST /.netlify/functions/peptide-processor
```

#### 请求格式
```json
{
  "action": "process|index|batch",
  "data": {...} | [{...}]
}
```

#### 响应格式
```json
{
  "success": true|false,
  "data": {...},
  "error": "错误信息（如果有）"
}
```

## 部署步骤

### 1. 准备环境

确保已安装：
- Node.js 14+
- Python 3.8+
- Netlify CLI

```bash
# 安装Netlify CLI
npm install -g netlify-cli

# 进入项目目录
cd SPADE/program

# 安装Node.js依赖
npm install
```

### 2. 本地测试

```bash
# 测试Python处理器
python3 serverless_processor.py test

# 测试Netlify Functions
node ../test/test-serverless.js

# 启动本地开发服务器
netlify dev
```

### 3. 部署到Netlify

#### 方法1: 通过CLI部署

```bash
# 首次部署
netlify deploy

# 生产环境部署
netlify deploy --prod
```

#### 方法2: 通过Git自动部署

1. 将代码推送到Git仓库
2. 在Netlify控制台连接仓库
3. 设置构建配置：
   - Build command: `echo 'Building SPADE functions'`
   - Publish directory: `.`
   - Functions directory: `program/functions`

### 4. 环境变量配置

在Netlify控制台设置：
- `PYTHON_VERSION`: `3.8`
- `NODE_ENV`: `production`

## 使用示例

### JavaScript/前端调用

```javascript
// 单个肽处理
const response = await fetch('/.netlify/functions/peptide-processor', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    action: 'process',
    data: {
      'SPADE ID': 'SPADE001',
      'Peptide Name': 'Test Peptide',
      'Sequence': 'KWKLLKKLLKLLLKLLK'
    }
  })
});

const result = await response.json();
console.log(result);
```

### cURL调用

```bash
curl -X POST https://your-site.netlify.app/.netlify/functions/peptide-processor \
  -H "Content-Type: application/json" \
  -d '{
    "action": "process",
    "data": {
      "SPADE ID": "SPADE001",
      "Peptide Name": "Test Peptide",
      "Sequence": "KWKLLKKLLKLLLKLLK"
    }
  }'
```

## 性能考虑

### 1. 执行时间限制
- Netlify Functions: 10秒超时
- 本实现设置8秒超时避免边缘情况

### 2. 内存限制
- Netlify Functions: 1008MB内存
- 当前实现内存占用较低

### 3. 并发处理
- 批量处理建议每次不超过50个肽数据
- 超大批量可分批调用

## 错误处理

### 常见错误类型

1. **数据格式错误**
   ```json
   {
     "success": false,
     "error": "缺少序列信息"
   }
   ```

2. **处理超时**
   ```json
   {
     "success": false,
     "error": "处理超时"
   }
   ```

3. **Python环境错误**
   ```json
   {
     "success": false,
     "error": "无法启动Python脚本"
   }
   ```

### 错误排查

1. 检查请求格式是否正确
2. 验证序列数据完整性
3. 查看Netlify Functions日志
4. 确认Python环境可用

## 监控和日志

### 1. Netlify Analytics
- 访问Netlify控制台查看调用统计
- 监控错误率和响应时间

### 2. 函数日志
- 在Netlify控制台的Functions页面查看实时日志
- 错误信息会记录在stderr中

### 3. 自定义监控
- 可集成第三方监控服务
- 建议设置响应时间和错误率告警

## 扩展功能

### 1. 缓存优化
- 可添加Redis缓存层
- 缓存常见序列的计算结果

### 2. 数据库集成
- 连接云数据库存储结果
- 实现持久化和历史查询

### 3. 批处理优化
- 实现队列系统处理大批量数据
- 异步处理和结果通知

## 安全考虑

### 1. 输入验证
- 序列长度限制（当前最大100个氨基酸）
- 字符集验证（仅允许标准氨基酸字母）

### 2. 访问控制
- 可配置API密钥验证
- 实现请求频率限制

### 3. 数据保护
- 不记录敏感的肽序列数据
- 使用HTTPS传输

## 故障排除

### 问题1: Python脚本无法执行
**解决方案:**
- 检查Python版本兼容性
- 确认脚本文件权限
- 验证依赖包安装

### 问题2: 超时错误
**解决方案:**
- 减少批量处理数量
- 优化算法复杂度
- 检查网络连接

### 问题3: 内存不足
**解决方案:**
- 减少同时处理的数据量
- 优化数据结构
- 使用流式处理

## 版本更新

### 当前版本: 1.0.0
- 基础功能完整实现
- 支持三种主要操作模式
- 完整的错误处理机制

### 后续计划
- 增加更多评分算法
- 优化性能和内存使用
- 添加批量处理队列

## 技术支持

如有问题，请联系：
- 开发团队: [team@spade-igem.org]
- 技术文档: [项目GitHub仓库]
- 在线支持: [项目官网]

---
**最后更新**: 2025-6-6
**文档版本**: 1.0.0 