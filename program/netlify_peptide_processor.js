const { spawn } = require('child_process');
const path = require('path');

/**
 * Netlify Functions 入口点 - JavaScript版本
 * 调用Python处理器来处理抗菌肽数据
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
        if (!requestData.action || !requestData.data) {
            return {
                statusCode: 400,
                headers: {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                body: JSON.stringify({
                    error: '缺少action或data字段',
                    success: false
                })
            };
        }

        // 调用Python处理器
        const pythonScript = path.join(__dirname, 'serverless_processor.py');
        const result = await callPythonProcessor(pythonScript, requestData);

        return {
            statusCode: result.success ? 200 : 400,
            headers: {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            body: JSON.stringify(result)
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
                details: error.message
            })
        };
    }
};

/**
 * 调用Python处理器
 */
function callPythonProcessor(scriptPath, data) {
    return new Promise((resolve, reject) => {
        const python = spawn('python3', [scriptPath]);
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
                reject(new Error(`Python脚本执行失败，退出码: ${code}`));
                return;
            }

            try {
                const result = JSON.parse(stdout);
                resolve(result);
            } catch (e) {
                console.error('解析Python输出时出错:', e);
                console.error('Python输出:', stdout);
                reject(new Error('无法解析Python脚本输出'));
            }
        });

        python.on('error', (error) => {
            console.error('启动Python脚本时出错:', error);
            reject(error);
        });
    });
}

// 本地测试函数
if (require.main === module) {
    // 本地测试
    const testEvent = {
        httpMethod: 'POST',
        body: JSON.stringify({
            action: 'process',
            data: {
                'SPADE ID': 'SPADE001',
                'Peptide Name': 'Test Peptide',
                'Sequence': 'KWKLLKKLLKLLLKLLK'
            }
        })
    };

    exports.handler(testEvent, {})
        .then(result => {
            console.log('测试结果:');
            console.log(JSON.stringify(JSON.parse(result.body), null, 2));
        })
        .catch(error => {
            console.error('测试失败:', error);
        });
} 