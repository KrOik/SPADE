const { spawn } = require('child_process');
const path = require('path');

/**
 * Netlify Functions - 抗菌肽数据处理器
 * 端点: /.netlify/functions/peptide-processor
 */
exports.handler = async (event, context) => {
    // 处理CORS预检请求
    if (event.httpMethod === 'OPTIONS') {
        return {
            statusCode: 200,
            headers: {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST, GET, OPTIONS'
            },
            body: ''
        };
    }

    // 只允许POST请求
    if (event.httpMethod !== 'POST') {
        return {
            statusCode: 405,
            headers: {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            body: JSON.stringify({
                error: '仅支持POST请求',
                success: false
            })
        };
    }

    try {
        // 解析请求体
        let requestData;
        try {
            requestData = JSON.parse(event.body || '{}');
        } catch (e) {
            return {
                statusCode: 400,
                headers: {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                body: JSON.stringify({
                    error: '无效的JSON格式',
                    success: false
                })
            };
        }

        // 验证请求数据
        if (!requestData.action) {
            return {
                statusCode: 400,
                headers: {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                body: JSON.stringify({
                    error: '缺少action字段',
                    success: false,
                    usage: {
                        actions: ['process', 'index', 'batch'],
                        example: {
                            action: 'process',
                            data: {
                                'SPADE ID': 'SPADE001',
                                'Peptide Name': 'Example Peptide',
                                'Sequence': 'KWKLLKKLLKLLLKLLK'
                            }
                        }
                    }
                })
            };
        }

        if (!requestData.data) {
            return {
                statusCode: 400,
                headers: {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                body: JSON.stringify({
                    error: '缺少data字段',
                    success: false
                })
            };
        }

        // 调用Python处理器
        const pythonScript = path.join(__dirname, '..', 'serverless_processor.py');
        const result = await callPythonProcessor(pythonScript, requestData);

        return {
            statusCode: result.success ? 200 : 400,
            headers: {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            body: JSON.stringify(result, null, 2)
        };

    } catch (error) {
        console.error('处理请求时出错:', error);
        return {
            statusCode: 500,
            headers: {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            body: JSON.stringify({
                error: '服务器内部错误',
                success: false,
                details: process.env.NODE_ENV === 'development' ? error.message : undefined
            })
        };
    }
};

/**
 * 调用Python处理器
 */
function callPythonProcessor(scriptPath, data) {
    return new Promise((resolve, reject) => {
        // 在Netlify环境中，可能需要使用python3或python
        const pythonCmd = process.env.NETLIFY ? 'python3' : 'python3';
        const python = spawn(pythonCmd, [scriptPath]);
        
        let stdout = '';
        let stderr = '';

        // 向Python脚本发送数据
        python.stdin.write(JSON.stringify(data));
        python.stdin.end();

        python.stdout.on('data', (data) => {
            stdout += data.toString();
        });

        python.stderr.on('data', (data) => {
            stderr += data.toString();
        });

        python.on('close', (code) => {
            if (code !== 0) {
                console.error('Python脚本错误:', stderr);
                reject(new Error(`Python脚本执行失败，退出码: ${code}\n错误信息: ${stderr}`));
                return;
            }

            try {
                const result = JSON.parse(stdout);
                resolve(result);
            } catch (e) {
                console.error('解析Python输出时出错:', e);
                console.error('Python输出:', stdout);
                reject(new Error('无法解析Python脚本输出: ' + stdout));
            }
        });

        python.on('error', (error) => {
            console.error('启动Python脚本时出错:', error);
            reject(new Error('无法启动Python脚本: ' + error.message));
        });

        // 设置超时（Netlify Functions有10秒限制）
        setTimeout(() => {
            python.kill();
            reject(new Error('处理超时'));
        }, 8000);
    });
} 