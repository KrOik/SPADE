const { handler } = require('../program/functions/peptide-processor');

/**
 * 测试Serverless Functions
 */
async function testServerlessFunctions() {
    console.log('🧪 开始测试Serverless Functions...\n');

    // 测试用例1: 单个肽数据处理
    console.log('📊 测试1: 单个肽数据处理');
    const testEvent1 = {
        httpMethod: 'POST',
        body: JSON.stringify({
            action: 'process',
            data: {
                'SPADE ID': 'SPADE001',
                'Peptide Name': 'Test Antimicrobial Peptide',
                'Sequence': 'KWKLLKKLLKLLLKLLK'
            }
        })
    };

    try {
        const result1 = await handler(testEvent1, {});
        console.log('状态码:', result1.statusCode);
        const body1 = JSON.parse(result1.body);
        console.log('结果:', body1.success ? '✅ 成功' : '❌ 失败');
        if (body1.success) {
            console.log('总分:', body1.data.total_score);
            console.log('等级:', body1.data.grade);
        } else {
            console.log('错误:', body1.error);
        }
    } catch (error) {
        console.log('❌ 测试1失败:', error.message);
    }

    console.log('\n' + '='.repeat(50) + '\n');

    // 测试用例2: 索引条目创建
    console.log('📝 测试2: 索引条目创建');
    const testEvent2 = {
        httpMethod: 'POST',
        body: JSON.stringify({
            action: 'index',
            data: {
                'SPADE ID': 'SPADE002',
                'Peptide Name': 'Another Test Peptide',
                'Sequence': 'GLLKRIKTLL'
            }
        })
    };

    try {
        const result2 = await handler(testEvent2, {});
        console.log('状态码:', result2.statusCode);
        const body2 = JSON.parse(result2.body);
        console.log('结果:', body2.success ? '✅ 成功' : '❌ 失败');
        if (body2.success) {
            console.log('ID:', body2.data.id);
            console.log('序列长度:', body2.data.length);
        } else {
            console.log('错误:', body2.error);
        }
    } catch (error) {
        console.log('❌ 测试2失败:', error.message);
    }

    console.log('\n' + '='.repeat(50) + '\n');

    // 测试用例3: 批量处理
    console.log('🔄 测试3: 批量处理');
    const testEvent3 = {
        httpMethod: 'POST',
        body: JSON.stringify({
            action: 'batch',
            data: [
                {
                    'SPADE ID': 'SPADE003',
                    'Peptide Name': 'Batch Peptide 1',
                    'Sequence': 'FLPLIGRVLSGIL'
                },
                {
                    'DRAMP ID': 'DRAMP001',
                    'Peptide Name': 'Batch Peptide 2',
                    'Sequence': 'GLLKRIKTLLKRLADLLK'
                }
            ]
        })
    };

    try {
        const result3 = await handler(testEvent3, {});
        console.log('状态码:', result3.statusCode);
        const body3 = JSON.parse(result3.body);
        console.log('结果:', body3.success ? '✅ 成功' : '❌ 失败');
        if (body3.success) {
            console.log('处理数量:', body3.processed_count);
            console.log('错误数量:', body3.error_count);
        } else {
            console.log('错误:', body3.error);
        }
    } catch (error) {
        console.log('❌ 测试3失败:', error.message);
    }

    console.log('\n' + '='.repeat(50) + '\n');

    // 测试用例4: 错误处理
    console.log('⚠️ 测试4: 错误处理');
    const testEvent4 = {
        httpMethod: 'POST',
        body: JSON.stringify({
            action: 'process',
            data: {
                'SPADE ID': 'SPADE004',
                'Peptide Name': 'Invalid Peptide'
                // 缺少序列
            }
        })
    };

    try {
        const result4 = await handler(testEvent4, {});
        console.log('状态码:', result4.statusCode);
        const body4 = JSON.parse(result4.body);
        console.log('结果:', !body4.success ? '✅ 正确处理错误' : '❌ 应该返回错误');
        if (!body4.success) {
            console.log('错误信息:', body4.error);
        }
    } catch (error) {
        console.log('❌ 测试4失败:', error.message);
    }

    console.log('\n🎉 测试完成！');
}

// 运行测试
if (require.main === module) {
    testServerlessFunctions()
        .then(() => {
            console.log('\n✅ 所有测试执行完毕');
            process.exit(0);
        })
        .catch(error => {
            console.error('\n❌ 测试过程中出现严重错误:', error);
            process.exit(1);
        });
}

module.exports = { testServerlessFunctions }; 