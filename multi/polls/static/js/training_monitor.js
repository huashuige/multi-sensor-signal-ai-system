/**
 * LSTM训练监控系统 - 完全重写版本
 * 使用最简单可靠的方法
 */

// 全局变量
let trainingSetId = null;
let isMonitoring = false;
let monitoringInterval = null;
let charts = {};

// 显示训练准备模态框
function showTrainingPrepModal() {
    const modal = document.getElementById('trainingPrepModal');
    if (modal) {
        modal.style.display = 'flex';
    }
}

// 隐藏训练准备模态框
function hideTrainingPrepModal() {
    const modal = document.getElementById('trainingPrepModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

// 显示数据加载模态框
function showDataLoadingModal() {
    const modal = document.getElementById('dataLoadingModal');
    if (modal) {
        modal.style.display = 'flex';
    }
}

// 隐藏数据加载模态框
function hideDataLoadingModal() {
    const modal = document.getElementById('dataLoadingModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

// 显示训练完成模态框
function showTrainingCompleteModal() {
    const modal = document.getElementById('trainingCompleteModal');
    if (modal) {
        modal.style.display = 'flex';
    }
}

// 隐藏训练完成模态框
function hideTrainingCompleteModal() {
    const modal = document.getElementById('trainingCompleteModal');
    if (modal) {
        modal.style.display = 'none';
    }
    // 设置标志，防止再次显示
    window.trainingCompleteModalShown = true;
}

// 初始化函数
function initTrainingMonitor() {
    console.log('🔍 初始化训练监控...');
    
    // 获取训练集ID
    trainingSetId = getTrainingSetId();
    console.log('🔍 训练集ID:', trainingSetId);
    
    // 显示训练准备模态框
    showTrainingPrepModal();
    
    // 延迟初始化图表，确保DOM完全加载
    setTimeout(() => {
        initCharts();
    }, 100);
    
    // 绑定事件
    bindEvents();
    
    // 添加初始日志
    addLog('info', '训练监控系统已启动');
    addLog('info', `训练集ID: ${trainingSetId}`);
    
    // 立即执行一次状态更新，确保页面有初始数据
    setTimeout(() => {
        updateTrainingStatus();
    }, 500);
    
    // 开始监控
    startMonitoring();
}

// 获取训练集ID
function getTrainingSetId() {
    if (window.TRAINING_SET_ID) {
        return window.TRAINING_SET_ID;
    }
    
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('id') || '1';
}

// 初始化图表
function initCharts() {
    console.log('🔍 初始化图表...');
    
    // 确保DOM元素存在
    const chartElement = document.getElementById('lossChart');
    if (!chartElement) {
        console.error('❌ 找不到图表元素');
        return;
    }
    
    // 合并的损失图表
    charts.lossChart = echarts.init(chartElement);
    
    // 设置初始数据
    const option = getLossChartOption();
    charts.lossChart.setOption(option);
    
    console.log('✅ 图表初始化完成');

    // 强制刷新图表
    setTimeout(() => {
        if (charts.lossChart) {
            charts.lossChart.resize();
            console.log('🔄 图表已刷新');
        }
    }, 200);

    // 监听窗口大小变化
    window.addEventListener('resize', () => {
        if (charts.lossChart) {
            charts.lossChart.resize();
        }
    });
}

// 获取合并损失图表配置
function getLossChartOption() {
    return {
        backgroundColor: '#1a1a1a',
        title: {
            text: '',
            textStyle: {
                color: '#ecf0f1',
                fontSize: 16,
                fontWeight: 'bold'
            },
            left: 'center',
            top: 10
        },
        tooltip: {
            trigger: 'axis',
            backgroundColor: 'rgba(44, 62, 80, 0.9)',
            borderColor: '#3498db',
            borderWidth: 1,
            textStyle: {
                color: '#ecf0f1'
            },
            formatter: function(params) {
                let result = `轮数: ${params[0].name}<br/>`;
                params.forEach(param => {
                    result += `${param.seriesName}: ${param.value.toFixed(6)}<br/>`;
                });
                return result;
            }
        },
        legend: {
            data: ['训练损失', '验证损失'],
            textStyle: {
                color: '#ecf0f1'
            },
            top: 10
        },
        grid: {
            left: '10%',
            right: '10%',
            top: '15%',
            bottom: '15%',
            containLabel: true
        },
        xAxis: [{
            type: 'category',
            data: [],
            axisLine: {
                lineStyle: {
                    color: '#34495e'
                }
            },
            axisLabel: {
                color: '#bdc3c7',
                fontSize: 12
            },
            splitLine: {
                show: false
            }
        }],
        yAxis: [{
            type: 'value',
            name: '损失值',
            nameTextStyle: {
                color: '#bdc3c7',
                fontSize: 12
            },
            axisLine: {
                lineStyle: {
                    color: '#34495e'
                }
            },
            axisLabel: {
                color: '#bdc3c7',
                fontSize: 12
            },
            splitLine: {
                lineStyle: {
                    color: '#2c3e50',
                    type: 'dashed'
                }
            }
        }],
        series: [
            {
                name: '训练损失',
                type: 'line',
                data: [],
                smooth: true,
                symbol: 'circle',
                symbolSize: 6,
                lineStyle: {
                    width: 3,
                    color: '#3498db'
                },
                itemStyle: {
                    color: '#3498db',
                    borderColor: '#2980b9',
                    borderWidth: 2
                },
                areaStyle: {
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        { offset: 0, color: 'rgba(52, 152, 219, 0.2)' },
                        { offset: 1, color: 'rgba(52, 152, 219, 0.05)' }
                    ])
                },
                emphasis: {
                    itemStyle: {
                        color: '#2980b9',
                        borderColor: '#1f4e79',
                        borderWidth: 3
                    }
                }
            },
            {
                name: '验证损失',
                type: 'line',
                data: [],
                smooth: true,
                symbol: 'circle',
                symbolSize: 6,
                lineStyle: {
                    width: 3,
                    color: '#e74c3c'
                },
                itemStyle: {
                    color: '#e74c3c',
                    borderColor: '#c0392b',
                    borderWidth: 2
                },
                areaStyle: {
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        { offset: 0, color: 'rgba(231, 76, 60, 0.2)' },
                        { offset: 1, color: 'rgba(231, 76, 60, 0.05)' }
                    ])
                },
                emphasis: {
                    itemStyle: {
                        color: '#c0392b',
                        borderColor: '#a93226',
                        borderWidth: 3
                    }
                }
            }
        ],
        animation: true,
        animationDuration: 1000,
        animationEasing: 'cubicOut'
    };
}

// 绑定事件
function bindEvents() {
    console.log('🔍 绑定事件...');
    
    // 暂停训练
    document.getElementById('pauseBtn').addEventListener('click', () => {
        pauseTraining();
    });

    // 恢复训练
    document.getElementById('resumeBtn').addEventListener('click', () => {
        resumeTraining();
    });

    // 停止训练
    document.getElementById('stopBtn').addEventListener('click', () => {
        stopTraining();
    });

    // 最小化
    document.getElementById('minimizeBtn').addEventListener('click', () => {
        minimizeWindow();
    });
    
    // 保存模型按钮
    document.getElementById('saveModelBtn').addEventListener('click', () => {
        console.log('🔍 保存模型...');
        saveModel();
    });
    
    // 预测评估按钮
    document.getElementById('predictionBtn').addEventListener('click', () => {
        console.log('🔍 跳转到预测评估...');
        goToPredictionEvaluation();
    });
    
    // 绑定模态框按钮事件
    const saveModelConfirmBtn = document.getElementById('saveModelConfirmBtn');
    const cancelSaveBtn = document.getElementById('cancelSaveBtn');
    
    if (saveModelConfirmBtn) {
        saveModelConfirmBtn.addEventListener('click', () => {
            saveModel();
            hideTrainingCompleteModal();
        });
    }
    
    if (cancelSaveBtn) {
        cancelSaveBtn.addEventListener('click', () => {
            hideTrainingCompleteModal();
        });
    }

    // 页面关闭前确认
    window.addEventListener('beforeunload', (e) => {
        if (isMonitoring) {
            e.preventDefault();
            e.returnValue = '训练正在进行中，确定要关闭页面吗？';
            return e.returnValue;
        }
    });
}

// 开始监控
function startMonitoring() {
    // 开始监控训练进度
    
    isMonitoring = true;
    
    // 重置训练完成弹窗标志
    window.trainingCompleteModalShown = false;
    
    // 立即执行一次更新
    updateTrainingStatus();
    
    // 启动定时器
    monitoringInterval = setInterval(() => {
        if (isMonitoring) {
            updateTrainingStatus();
        } else {
            console.log('🔍 监控已停止，清除定时器');
            clearInterval(monitoringInterval);
        }
    }, 2000);
    
    addLog('info', '开始监控训练进度');
}

// 更新训练状态
function updateTrainingStatus() {
    console.log('🔍 开始更新训练状态...');
    
    // 检查训练集ID
    if (!trainingSetId) {
        console.error('❌ 训练集ID不存在');
        return;
    }
    
    console.log('🔍 训练集ID:', trainingSetId);
    
    // 构建URL
    const url = `/api/training-status/${trainingSetId}/`;
    console.log('🔍 请求URL:', url);
    
    // 使用XMLHttpRequest，更可靠
    const xhr = new XMLHttpRequest();
    xhr.open('GET', url, true);
    
    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4) {
            if (xhr.status === 200) {
                try {
                    const data = JSON.parse(xhr.responseText);
                    
                    if (data.success && data.training_status) {
                        const status = data.training_status;
                        
                        console.log('📊 收到训练状态:', status);
                        
                        // 更新训练状态显示
                        console.log('🔍 检查训练状态:', {
                            status: status.status,
                            current_epoch: status.current_epoch,
                            training_loss: status.training_loss,
                            validation_loss: status.validation_loss
                        });
                        
                        // 核心逻辑：只要轮数大于0就隐藏弹窗
                        if (status.current_epoch > 0) {
                            console.log('🔍 ✅ 轮数大于0，隐藏弹窗');
                            hideDataLoadingModal();
                            hideTrainingPrepModal();
                            updateTrainingStatusDisplay('training');
                        } else {
                            console.log('🔍 ❌ 轮数为0，保持弹窗');
                            updateTrainingStatusDisplay('unknown');
                        }
                        
                        // 检测训练完成
                        if (status.current_epoch !== undefined && status.total_epochs !== undefined && 
                            status.current_epoch >= status.total_epochs) {
                            updateTrainingStatusDisplay('completed');
                            
                            // 只在第一次检测到完成时显示弹窗
                            if (!window.trainingCompleteModalShown) {
                                showTrainingCompleteModal();
                                window.trainingCompleteModalShown = true;
                                addLog('success', '训练已完成！');
                            }
                            
                            // 停止监控，因为训练已完成
                            stopMonitoring();
                        }
                        
                        // 检测训练停止
                        if (status.status === 'stopped') {
                            updateTrainingStatusDisplay('stopped');
                            addLog('warning', '训练已被停止');
                            // 停止监控
                            stopMonitoring();
                            // 禁用控制按钮
                            document.getElementById('pauseBtn').disabled = true;
                            document.getElementById('resumeBtn').disabled = true;
                            document.getElementById('stopBtn').disabled = true;
                        }
                        
                        // 检测训练失败
                        if (status.status === 'failed') {
                            updateTrainingStatusDisplay('failed');
                            addLog('error', '训练失败');
                            // 停止监控
                            stopMonitoring();
                            // 禁用控制按钮
                            document.getElementById('pauseBtn').disabled = true;
                            document.getElementById('resumeBtn').disabled = true;
                            document.getElementById('stopBtn').disabled = true;
                        }
                        
                        // 更新训练集合名字
                        if (status.training_set_name !== undefined) {
                            const element = document.getElementById('setName');
                            if (element) {
                                element.textContent = status.training_set_name;
                            }
                        }
                        
                        // 更新按钮状态
                        updateButtonStates(status.status);
                        
                        // 更新进度信息
                        updateProgress(status);
                        
                        // 更新指标
                        if (status.current_epoch !== undefined) {
                            const element = document.getElementById('currentEpoch');
                            if (element) {
                                element.textContent = status.current_epoch;
                            }
                        }
                        if (status.total_epochs !== undefined) {
                            const element = document.getElementById('totalEpochs');
                            if (element) {
                                element.textContent = status.total_epochs;
                            }
                        }
                        if (status.training_loss !== undefined) {
                            const element = document.getElementById('trainingLoss');
                            if (element) {
                                element.textContent = status.training_loss.toFixed(6);
                            }
                        }
                        if (status.validation_loss !== undefined) {
                            const element = document.getElementById('validationLoss');
                            if (element) {
                                element.textContent = status.validation_loss.toFixed(6);
                            }
                        }
                        if (status.learning_rate !== undefined) {
                            const element = document.getElementById('learningRate');
                            if (element) {
                                element.textContent = status.learning_rate;
                            }
                        }
                        if (status.mse_metric !== undefined) {
                            const element = document.getElementById('mseMetric');
                            if (element) {
                                element.textContent = status.mse_metric.toFixed(6);
                            }
                        }
                        
                        // 更新图表
                        updateCharts(status);
                        
                        // 添加日志 - 只在轮次发生变化时显示
                        if (status.current_epoch !== undefined) {
                            // 检查轮次是否发生变化
                            const lastEpoch = window.lastLoggedEpoch || 0;
                            if (status.current_epoch > lastEpoch) {
                                addLog('info', `轮次 ${status.current_epoch}/${status.total_epochs} - 训练损失: ${status.training_loss?.toFixed(6) || 'N/A'}, 验证损失: ${status.validation_loss?.toFixed(6) || 'N/A'}`);
                                window.lastLoggedEpoch = status.current_epoch;
                            }
                        }
                        
                        // UI更新完成
                    } else {
                        console.error('❌ API返回数据格式错误:', data);
                    }
                } catch (error) {
                    console.error('❌ 解析响应失败:', error);
                }
            } else {
                console.error('❌ XHR错误:', xhr.status, xhr.statusText);
                // 如果请求失败，尝试隐藏模态框（可能是训练已经开始）
                if (xhr.status === 500) {
                    console.log('🔄 检测到服务器错误，尝试隐藏配置窗口');
                    hideDataLoadingModal();
                    updateTrainingStatusDisplay('training');
                }
            }
        }
    };
    
    xhr.onerror = function() {
        console.error('❌ XHR网络错误');
    };
    
    console.log('🔍 发送XHR请求...');
    xhr.send();
}

// 保存模型函数
function saveModel() {
    console.log('🔍 开始保存模型...');
    
    if (!trainingSetId) {
        console.error('❌ 训练集ID不存在');
        addLog('error', '保存模型失败：训练集ID不存在');
        return;
    }
    
    const url = `/api/save-model/${trainingSetId}/`;
    
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            addLog('success', '模型保存成功！');
            // 关闭训练完成弹窗
            hideTrainingCompleteModal();
            // 显示成功消息
            alert('模型保存成功！');
        } else {
            addLog('error', `保存模型失败：${data.message}`);
            alert(`保存模型失败：${data.message}`);
        }
    })
    .catch(error => {
        console.error('保存模型失败:', error);
        addLog('error', '保存模型失败：网络错误');
        alert('保存模型失败：网络错误');
    });
}



// 更新指标显示
function updateMetrics(status) {
    // 安全地获取所有指标元素
    const trainingLossElement = document.getElementById('trainingLoss');
    const validationLossElement = document.getElementById('validationLoss');
    const learningRateElement = document.getElementById('learningRate');
    const mseMetricElement = document.getElementById('mseMetric');
    const currentEpochElement = document.getElementById('currentEpoch');
    
    // 安全地更新训练损失
    if (trainingLossElement) {
        trainingLossElement.textContent = status.training_loss?.toFixed(4) || '0.0000';
    }
    
    // 安全地更新验证损失
    if (validationLossElement) {
        validationLossElement.textContent = status.validation_loss?.toFixed(4) || '0.0000';
    }
    
    // 安全地更新学习率
    if (learningRateElement) {
        learningRateElement.textContent = status.learning_rate?.toFixed(4) || '0.0010';
    }
    
    // 安全地更新MSE指标
    if (mseMetricElement) {
        mseMetricElement.textContent = status.mse_metric?.toFixed(4) || '0.0000';
    }
    
    // 安全地更新当前轮数
    if (currentEpochElement) {
        currentEpochElement.textContent = status.current_epoch || 0;
    }
}

// 更新ECharts图表
function updateCharts(status) {
    if (!charts.lossChart) {
        console.error('❌ 图表未初始化');
        return;
    }
    
    if (status.current_epoch && status.training_loss !== undefined) {
        console.log('📊 更新图表数据:', {
            epoch: status.current_epoch,
            training_loss: status.training_loss,
            validation_loss: status.validation_loss
        });
        
        // 更新合并的损失图表
        const lossOption = charts.lossChart.getOption();
        
        // 确保数组存在
        if (!lossOption.xAxis[0].data) {
            lossOption.xAxis[0].data = [];
        }
        if (!lossOption.series[0].data) {
            lossOption.series[0].data = [];
        }
        if (!lossOption.series[1].data) {
            lossOption.series[1].data = [];
        }
        
        // 检查是否已经存在这个轮次的数据
        const epochIndex = lossOption.xAxis[0].data.indexOf(status.current_epoch);
        
        if (epochIndex === -1) {
            // 新轮次，添加数据
            lossOption.xAxis[0].data.push(status.current_epoch);
            lossOption.series[0].data.push(status.training_loss);
            
            // 更新验证损失数据
            if (status.validation_loss !== undefined) {
                lossOption.series[1].data.push(status.validation_loss);
            }
        } else {
            // 已存在的轮次，更新数据
            lossOption.series[0].data[epochIndex] = status.training_loss;
            if (status.validation_loss !== undefined) {
                lossOption.series[1].data[epochIndex] = status.validation_loss;
            }
        }
        
        // 限制数据点数量
        if (lossOption.xAxis[0].data.length > 100) {
            lossOption.xAxis[0].data.shift();
            lossOption.series[0].data.shift();
            lossOption.series[1].data.shift();
        }
        
        charts.lossChart.setOption(lossOption);
        console.log('✅ 图表更新完成');
    }
}

// 更新进度条
function updateProgress(status) {
    // 安全地更新进度条
    const progressTextElement = document.getElementById('progressText');
    const progressFillElement = document.getElementById('progressFill');
    const etaTextElement = document.getElementById('etaText');
    
    if (status.current_epoch !== undefined && status.total_epochs !== undefined) {
        const progress = (status.current_epoch / status.total_epochs) * 100;
        
        // 安全地更新进度文本
        if (progressTextElement) {
            progressTextElement.textContent = `${status.current_epoch}/${status.total_epochs}`;
        }
        
        // 安全地更新进度条
        if (progressFillElement) {
            progressFillElement.style.width = `${progress}%`;
        }
        
        // 计算预计剩余时间
        if (status.eta && etaTextElement) {
            etaTextElement.textContent = `预计剩余: ${status.eta}`;
        }
    }
}

// 更新训练状态显示
function updateTrainingStatusDisplay(status = 'training') {
    const statusIndicator = document.getElementById('statusIndicator');
    const statusText = document.getElementById('statusText');
    
    // 安全检查元素是否存在
    if (!statusIndicator || !statusText) {
        console.warn('⚠️ 状态指示器元素不存在');
        return;
    }
    
    statusIndicator.className = 'status-indicator';
    
    switch (status) {
        case 'training':
            statusIndicator.classList.add('status-training');
            statusText.textContent = '训练中';
            break;
        case 'paused':
            statusIndicator.classList.add('status-paused');
            statusText.textContent = '已暂停';
            break;
        case 'completed':
            statusIndicator.classList.add('status-completed');
            statusText.textContent = '已完成';
            break;
        case 'stopped':
            statusIndicator.classList.add('status-error');
            statusText.textContent = '已停止';
            break;
        case 'failed':
            statusIndicator.classList.add('status-error');
            statusText.textContent = '训练失败';
            break;
        case 'unknown':
        default:
            statusIndicator.classList.add('status-unknown');
            statusText.textContent = '准备中';
            break;
    }
}

// 暂停训练
function pauseTraining() {
    console.log('🔍 发送暂停训练请求...');
    const url = `/api/pause-training/${trainingSetId}/`;
    
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        console.log('🔍 暂停训练响应:', data);
        if (data.success) {
            updateTrainingStatusDisplay('paused');
            document.getElementById('pauseBtn').style.display = 'none';
            document.getElementById('resumeBtn').style.display = 'block';
            addLog('warning', '训练已暂停');
            console.log('✅ 训练暂停成功');
        } else {
            console.error('❌ 暂停训练失败:', data.message);
            addLog('error', `暂停训练失败: ${data.message}`);
        }
    })
    .catch(error => {
        console.error('❌ 暂停训练请求失败:', error);
        addLog('error', '暂停训练失败');
    });
}

// 恢复训练
function resumeTraining() {
    console.log('🔍 发送恢复训练请求...');
    const url = `/api/resume-training/${trainingSetId}/`;
    
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        console.log('🔍 恢复训练响应:', data);
        if (data.success) {
            updateTrainingStatusDisplay('training');
            document.getElementById('pauseBtn').style.display = 'block';
            document.getElementById('resumeBtn').style.display = 'none';
            addLog('success', '训练已恢复');
            console.log('✅ 训练恢复成功');
        } else {
            console.error('❌ 恢复训练失败:', data.message);
            addLog('error', `恢复训练失败: ${data.message}`);
        }
    })
    .catch(error => {
        console.error('❌ 恢复训练请求失败:', error);
        addLog('error', '恢复训练失败');
    });
}

// 停止训练
function stopTraining() {
    if (!confirm('确定要停止训练吗？这将终止当前的训练过程。')) {
        return;
    }
    
    const url = `/api/stop-training/${trainingSetId}/`;
    
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            stopMonitoring();
            updateTrainingStatus('stopped');
            addLog('warning', '训练已停止');
            
            // 禁用控制按钮
            document.getElementById('pauseBtn').disabled = true;
            document.getElementById('resumeBtn').disabled = true;
            document.getElementById('stopBtn').disabled = true;
        }
    })
    .catch(error => {
        console.error('停止训练失败:', error);
        addLog('error', '停止训练失败');
    });
}

// 最小化窗口
function minimizeWindow() {
    addLog('info', '窗口已最小化');
}

// 停止监控
function stopMonitoring() {
    isMonitoring = false;
    if (monitoringInterval) {
        clearInterval(monitoringInterval);
        monitoringInterval = null;
    }
    addLog('info', '停止监控训练进度');
}

// 添加日志
function addLog(type, message) {
    const logsContainer = document.getElementById('logsContainer');
    
    // 安全检查日志容器是否存在
    if (!logsContainer) {
        console.warn('⚠️ 日志容器不存在，无法添加日志');
        return;
    }
    
    const logEntry = document.createElement('div');
    logEntry.className = 'log-entry';
    
    const now = new Date();
    const timeString = now.toLocaleString('zh-CN');
    
    logEntry.innerHTML = `
        <span class="log-time">[${timeString}]</span>
        <span class="log-message log-${type}">${message}</span>
    `;
    
    logsContainer.insertBefore(logEntry, logsContainer.firstChild);
    
    // 限制日志数量
    if (logsContainer.children.length > 100) {
        logsContainer.removeChild(logsContainer.lastChild);
    }
    
    // 保持滚动位置在顶部（最新日志）
    logsContainer.scrollTop = 0;
}

// 获取Cookie值
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// 更新按钮状态
function updateButtonStates(trainingStatus) {
    const pauseBtn = document.getElementById('pauseBtn');
    const resumeBtn = document.getElementById('resumeBtn');
    const stopBtn = document.getElementById('stopBtn');
    const saveModelBtn = document.getElementById('saveModelBtn');
    const predictionBtn = document.getElementById('predictionBtn');
    
    // 安全检查所有按钮元素是否存在
    if (!pauseBtn || !resumeBtn || !stopBtn || !saveModelBtn || !predictionBtn) {
        console.warn('⚠️ 某些按钮元素不存在，跳过按钮状态更新');
        return;
    }
    
    // 重置所有按钮状态
    pauseBtn.disabled = true;
    resumeBtn.disabled = true;
    stopBtn.disabled = true;
    saveModelBtn.disabled = true;
    predictionBtn.disabled = true;
    
    switch(trainingStatus) {
        case 'created':
            // 初始状态：只能停止
            stopBtn.disabled = false;
            break;
            
        case 'training':
            // 训练中：可以暂停/停止
            pauseBtn.disabled = false;
            stopBtn.disabled = false;
            break;
            
        case 'paused':
            // 暂停状态：可以恢复/停止
            resumeBtn.disabled = false;
            stopBtn.disabled = false;
            break;
            
        case 'completed':
            // 训练完成：可以保存模型和预测
            saveModelBtn.disabled = false;
            predictionBtn.disabled = false;
            break;
            
        case 'failed':
        case 'stopped':
            // 训练失败/停止：可以重新开始（通过刷新页面）
            break;
    }
    
    console.log(`🔍 按钮状态已更新，训练状态: ${trainingStatus}`);
}

// 跳转到预测评估页面
function goToPredictionEvaluation() {
    if (trainingSetId) {
        window.location.href = `/prediction-evaluation/${trainingSetId}/`;
    } else {
        alert('无法跳转到预测评估页面，训练集ID不存在。');
    }
}


// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    console.log('🔍 页面加载完成，开始初始化...');
    initTrainingMonitor();
}); 
 
 