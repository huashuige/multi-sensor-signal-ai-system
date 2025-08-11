/**
 * 模型预测系统
 */

// 全局变量
let modelId = null;
let selectedDataSource = null;
let charts = {};
let predictionResults = null;

// 数据源相关变量
let dataSources = [];
let filteredDataSources = [];
let currentPage = 1;
let itemsPerPage = 5;

// 初始化函数
function initModelPrediction() {
    console.log('🔍 初始化模型预测...');
    
    // 获取模型ID
    modelId = getModelId();
    console.log('🔍 模型ID:', modelId);
    
    // 绑定事件
    bindEvents();
    
    // 加载模型信息
    loadModelInfo();
    
    // 加载数据源列表
    loadDataSourceList();
    
    // 添加初始日志
    addLog('info', '模型预测系统已启动');
    addLog('info', `模型ID: ${modelId}`);
}

// 获取模型ID
function getModelId() {
    if (window.MODEL_ID) {
        return window.MODEL_ID;
    }
    
    const urlParams = new URLSearchParams(window.location.search);
    const id = urlParams.get('model_id');
    
    if (!id) {
        // 从URL路径中提取ID
        const pathParts = window.location.pathname.split('/');
        const idIndex = pathParts.indexOf('model-prediction');
        if (idIndex !== -1 && pathParts[idIndex + 1]) {
            return pathParts[idIndex + 1];
        }
    }
    
    return id;
}

// 绑定事件
function bindEvents() {
    console.log('🔍 绑定事件...');
    
    // 选择数据源按钮
    const selectDataSourceBtn = document.getElementById('selectDataSourceBtn');
    if (selectDataSourceBtn) {
        selectDataSourceBtn.addEventListener('click', () => {
            openDataSourceModal();
        });
    }

    // 关闭弹窗按钮
    const closeModalBtn = document.getElementById('closeDataSourceModal');
    if (closeModalBtn) {
        closeModalBtn.addEventListener('click', () => {
            closeDataSourceModal();
        });
    }

    // 点击弹窗背景关闭
    const modalOverlay = document.getElementById('dataSourceModal');
    if (modalOverlay) {
        modalOverlay.addEventListener('click', (e) => {
            if (e.target === modalOverlay) {
                closeDataSourceModal();
            }
        });
    }

    // 数据源搜索
    const dataSourceSearch = document.getElementById('dataSourceSearch');
    if (dataSourceSearch) {
        dataSourceSearch.addEventListener('input', (e) => {
            searchDataSources(e.target.value);
        });
    }

    // 刷新数据源按钮
    const refreshBtn = document.getElementById('refreshDataSourcesBtn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', () => {
            loadDataSourceList();
        });
    }

    // 更换数据源按钮
    const changeBtn = document.getElementById('changeDataSourceBtn');
    if (changeBtn) {
        changeBtn.addEventListener('click', () => {
            changeDataSource();
        });
    }
    
    // 开始预测按钮
    const startBtn = document.getElementById('startPredictionBtn');
    if (startBtn) {
        startBtn.addEventListener('click', () => {
            startPrediction();
        });
    }
    
    // 导出结果按钮
    const exportBtn = document.getElementById('exportResultsBtn');
    if (exportBtn) {
        exportBtn.addEventListener('click', () => {
            exportResults();
        });
    }
    
    // 查看通道详情按钮
    const detailsBtn = document.getElementById('viewChannelDetailsBtn');
    if (detailsBtn) {
        detailsBtn.addEventListener('click', () => {
            showChannelDetails();
        });
    }
}

// 加载模型信息
function loadModelInfo() {
    if (!modelId) {
        addLog('error', '模型ID不存在');
        return;
    }
    
    const url = `/api/get-saved-model/${modelId}/`;
    
    fetch(url)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const model = data.model;
                document.getElementById('modelName').textContent = model.name;
                addLog('info', `已加载模型: ${model.name}`);
            } else {
                addLog('error', `加载模型信息失败: ${data.message}`);
            }
        })
        .catch(error => {
            console.error('加载模型信息失败:', error);
            addLog('error', '加载模型信息失败');
        });
}

// 加载数据源列表
function loadDataSourceList() {
    addLog('info', '正在加载数据源列表...');
    
    const url = `/api/get-monitor-data-for-dl/`;
    
    fetch(url)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                dataSources = data.data_list;
                filteredDataSources = [...dataSources];
                currentPage = 1;
                renderDataSources();
                addLog('success', `已加载 ${dataSources.length} 个数据源`);
            } else {
                addLog('error', `加载数据源失败: ${data.message}`);
            }
        })
        .catch(error => {
            console.error('加载数据源失败:', error);
            addLog('error', '加载数据源失败');
        });
}

// 搜索数据源
function searchDataSources(searchTerm) {
    if (!searchTerm.trim()) {
        filteredDataSources = [...dataSources];
    } else {
        filteredDataSources = dataSources.filter(item => 
            item.task_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
            (item.task_description && item.task_description.toLowerCase().includes(searchTerm.toLowerCase()))
        );
    }
    currentPage = 1;
    renderDataSources();
}

// 渲染数据源列表
function renderDataSources() {
    const container = document.getElementById('dataSourceList');
    if (!container) return;
    
    if (!filteredDataSources || filteredDataSources.length === 0) {
        container.innerHTML = `
            <div class="text-center py-8 text-gray-500">
                <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                </svg>
                <p class="mt-2 text-sm">暂无可用数据源</p>
                <p class="text-xs text-gray-400">请先在监控模块中创建数据采集任务</p>
            </div>
        `;
        updatePagination();
        return;
    }
    
    // 计算分页
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    const pageData = filteredDataSources.slice(startIndex, endIndex);
    
    container.innerHTML = pageData.map(item => `
        <div class="data-source-item" data-task-id="${item.task_id}">
            <div class="data-source-name">${item.task_name}</div>
            <div class="data-source-desc">${item.task_description || '无描述'}</div>
            <div class="data-source-meta">
                <span>📅 ${new Date(item.created_at).toLocaleDateString()}</span>
                <span>📊 ${item.total_data_points.toLocaleString()} 点</span>
                <span>📁 ${item.file_size_mb} MB</span>
                <span>🔌 ${item.enabled_channels.length} 通道</span>
            </div>
        </div>
    `).join('');
    
    // 绑定点击事件
    container.querySelectorAll('.data-source-item').forEach(item => {
        item.addEventListener('click', () => {
            const taskId = item.dataset.taskId;
            selectDataSource(taskId);
        });
    });
    
    updatePagination();
}

// 选择数据源
function selectDataSource(taskId) {
    const selectedItem = filteredDataSources.find(item => item.task_id === taskId);
    if (selectedItem) {
        selectedDataSource = selectedItem;
        showSelectedDataSource();
        updateStartButton();
        
        // 更新选中状态
        document.querySelectorAll('.data-source-item').forEach(item => {
            item.classList.remove('selected');
        });
        document.querySelector(`[data-task-id="${taskId}"]`).classList.add('selected');
        
        addLog('info', `已选择数据源: ${selectedItem.task_name}`);
    }
}

// 打开数据源选择弹窗
function openDataSourceModal() {
    const modal = document.getElementById('dataSourceModal');
    if (modal) {
        modal.style.display = 'flex';
        loadDataSourceList();
    }
}

// 关闭数据源选择弹窗
function closeDataSourceModal() {
    const modal = document.getElementById('dataSourceModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

// 显示选中的数据源
function showSelectedDataSource() {
    const container = document.getElementById('selectedDataInfo');
    const text = document.getElementById('selectedDataText');
    
    if (!container || !text) return;
    
    if (selectedDataSource) {
        text.textContent = `${selectedDataSource.task_name} - ${selectedDataSource.file_size_mb} MB - ${selectedDataSource.total_data_points.toLocaleString()} 点`;
        container.style.display = 'flex';
        closeDataSourceModal();
    } else {
        container.style.display = 'none';
    }
}

// 更换数据源
function changeDataSource() {
    selectedDataSource = null;
    const selectedContainer = document.getElementById('selectedDataInfo');
    if (selectedContainer) {
        selectedContainer.style.display = 'none';
    }
    
    // 清除选中状态
    document.querySelectorAll('.data-source-item').forEach(item => {
        item.classList.remove('selected');
    });
    
    updateStartButton();
    addLog('info', '已清除数据源选择');
}

// 更新分页
function updatePagination() {
    const totalItems = filteredDataSources.length;
    const totalPages = Math.ceil(totalItems / itemsPerPage);
    const startItem = (currentPage - 1) * itemsPerPage + 1;
    const endItem = Math.min(currentPage * itemsPerPage, totalItems);
    
    const container = document.getElementById('dataSourcePagination');
    if (!container) return;
    
    if (totalPages <= 1) {
        container.innerHTML = '';
        return;
    }
    
    container.innerHTML = `
        <button class="pagination-btn" id="prevPage" ${currentPage <= 1 ? 'disabled' : ''}>上一页</button>
        <span class="pagination-info">第 ${startItem}-${endItem} 项，共 ${totalItems} 项</span>
        <button class="pagination-btn" id="nextPage" ${currentPage >= totalPages ? 'disabled' : ''}>下一页</button>
    `;
    
    // 绑定分页事件
    const prevBtn = document.getElementById('prevPage');
    const nextBtn = document.getElementById('nextPage');
    
    if (prevBtn) {
        prevBtn.addEventListener('click', () => {
            if (currentPage > 1) {
                currentPage--;
                renderDataSources();
            }
        });
    }
    
    if (nextBtn) {
        nextBtn.addEventListener('click', () => {
            if (currentPage < totalPages) {
                currentPage++;
                renderDataSources();
            }
        });
    }
}

// 更新开始按钮状态
function updateStartButton() {
    const startBtn = document.getElementById('startPredictionBtn');
    if (!startBtn) return;
    
    if (selectedDataSource) {
        startBtn.disabled = false;
    } else {
        startBtn.disabled = true;
    }
}

// 开始预测
function startPrediction() {
    console.log('🔍 开始预测...');
    
    if (!modelId) {
        addLog('error', '模型ID不存在');
        return;
    }
    
    if (!selectedDataSource) {
        addLog('error', '请先选择数据源');
        return;
    }
    
    // 禁用开始预测按钮
    const startBtn = document.getElementById('startPredictionBtn');
    startBtn.disabled = true;
    startBtn.textContent = '预测中...';
    
    addLog('info', '开始模型预测...');
    
    // 显示加载状态
    showLoadingState();
    
    // 调用预测API
    const url = `/api/model-predict/${modelId}/`;
    
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            data_source_id: selectedDataSource.task_id
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            addLog('success', '预测完成！');
            predictionResults = data;
            updateMetrics(data.metrics);
            updateCharts(data);
            enableExportButton();
        } else {
            addLog('error', `预测失败: ${data.message}`);
        }
    })
    .catch(error => {
        console.error('预测失败:', error);
        addLog('error', '预测失败: 网络错误');
    })
    .finally(() => {
        // 恢复开始预测按钮
        startBtn.disabled = false;
        startBtn.textContent = '开始预测';
        hideLoadingState();
    });
}

// 显示加载状态
function showLoadingState() {
    const chartsContainer = document.getElementById('chartsContainer');
    chartsContainer.innerHTML = `
        <div class="loading-spinner"></div>
        <p style="text-align: center; color: #bdc3c7; margin-top: 10px;">
            正在加载模型并进行预测...
        </p>
    `;
}

// 隐藏加载状态
function hideLoadingState() {
    // 加载状态会在updateCharts中清除
}

// 更新评估指标
function updateMetrics(metrics) {
    console.log('🔍 更新评估指标:', metrics);
    
    // 存储多通道指标数据供详情查看
    window.channelMetricsData = metrics;
    
    if (metrics.by_channel && metrics.by_channel.length > 0) {
        // 多通道模式：显示平均指标
        const avgMetrics = metrics.average;
        updateSingleChannelMetrics(avgMetrics);
        
        // 显示查看详情按钮
        const detailsBtn = document.getElementById('viewChannelDetailsBtn');
        if (detailsBtn) {
            detailsBtn.style.display = 'inline-flex';
        }
    } else if (metrics.r2 !== undefined) {
        // 单通道模式：直接显示指标
        updateSingleChannelMetrics(metrics);
        
        // 隐藏查看详情按钮
        const detailsBtn = document.getElementById('viewChannelDetailsBtn');
        if (detailsBtn) {
            detailsBtn.style.display = 'none';
        }
    }
}

// 根据通道数确定网格列数
function getGridColumns(channelCount) {
    if (channelCount <= 2) return 2;
    if (channelCount <= 4) return 2;
    if (channelCount <= 6) return 3;
    if (channelCount <= 9) return 3;
    return 4;
}

// 创建通道指标卡片
function createChannelMetricsCard(channelMetrics, channelIndex) {
    const card = document.createElement('div');
    card.className = 'metric-card';
    card.style.cssText = `
        background: #34495e;
        border-radius: 8px;
        padding: 15px;
        text-align: center;
        border: 1px solid #2c3e50;
    `;
    
    const channelName = `通道 ${channelIndex + 1}`;
    const r2Value = channelMetrics.r2.toFixed(4);
    const mseValue = channelMetrics.mse.toFixed(4);
    const maeValue = channelMetrics.mae.toFixed(4);
    
    card.innerHTML = `
        <h3 style="color: #ecf0f1; margin: 0 0 10px 0; font-size: 14px;">${channelName}</h3>
        <div style="margin-bottom: 8px;">
            <span style="color: #bdc3c7; font-size: 12px;">R²</span><br>
            <span style="color: ${getMetricColor(channelMetrics.r2, 'r2')}; font-size: 18px; font-weight: bold;">${r2Value}</span>
        </div>
        <div style="margin-bottom: 8px;">
            <span style="color: #bdc3c7; font-size: 12px;">MSE</span><br>
            <span style="color: ${getMetricColor(channelMetrics.mse, 'mse')}; font-size: 16px;">${mseValue}</span>
        </div>
        <div>
            <span style="color: #bdc3c7; font-size: 12px;">MAE</span><br>
            <span style="color: ${getMetricColor(channelMetrics.mae, 'mae')}; font-size: 16px;">${maeValue}</span>
        </div>
    `;
    
    return card;
}

// 创建平均指标卡片
function createAverageMetricsCard(averageMetrics) {
    const card = document.createElement('div');
    card.className = 'average-metrics-card';
    card.style.cssText = `
        background: #2c3e50;
        border-radius: 8px;
        padding: 15px;
        text-align: center;
        border: 2px solid #3498db;
        margin-top: 15px;
    `;
    
    const avgR2 = averageMetrics.r2.toFixed(4);
    const avgMse = averageMetrics.mse.toFixed(4);
    const avgMae = averageMetrics.mae.toFixed(4);
    
    card.innerHTML = `
        <h3 style="color: #3498db; margin: 0 0 10px 0; font-size: 16px;">平均指标</h3>
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px;">
            <div>
                <span style="color: #bdc3c7; font-size: 12px;">R²</span><br>
                <span style="color: ${getMetricColor(averageMetrics.r2, 'r2')}; font-size: 18px; font-weight: bold;">${avgR2}</span>
            </div>
            <div>
                <span style="color: #bdc3c7; font-size: 12px;">MSE</span><br>
                <span style="color: ${getMetricColor(averageMetrics.mse, 'mse')}; font-size: 16px;">${avgMse}</span>
            </div>
            <div>
                <span style="color: #bdc3c7; font-size: 12px;">MAE</span><br>
                <span style="color: ${getMetricColor(averageMetrics.mae, 'mae')}; font-size: 16px;">${avgMae}</span>
            </div>
        </div>
    `;
    
    return card;
}

// 兼容旧版本：单通道指标更新
function updateSingleChannelMetrics(metrics) {
    const r2Element = document.getElementById('r2Value');
    const mseElement = document.getElementById('mseValue');
    const maeElement = document.getElementById('maeValue');
    const rmseElement = document.getElementById('rmseValue');
    
    if (metrics.r2 !== undefined) {
        r2Element.textContent = metrics.r2.toFixed(4);
        r2Element.className = getMetricClass(metrics.r2, 'r2');
    }
    
    if (metrics.mse !== undefined) {
        mseElement.textContent = metrics.mse.toFixed(4);
        mseElement.className = getMetricClass(metrics.mse, 'mse');
    }
    
    if (metrics.mae !== undefined) {
        maeElement.textContent = metrics.mae.toFixed(4);
        maeElement.className = getMetricClass(metrics.mae, 'mae');
    }
    
    if (metrics.rmse !== undefined) {
        rmseElement.textContent = metrics.rmse.toFixed(4);
        rmseElement.className = getMetricClass(metrics.rmse, 'rmse');
    }
}

// 获取指标颜色
function getMetricColor(value, metricType) {
    if (metricType === 'r2') {
        if (value >= 0.8) return '#27ae60';  // 绿色
        if (value >= 0.6) return '#f39c12';  // 橙色
        return '#e74c3c';  // 红色
    } else {
        // MSE和MAE越小越好
        if (value <= 0.1) return '#27ae60';  // 绿色
        if (value <= 0.3) return '#f39c12';  // 橙色
        return '#e74c3c';  // 红色
    }
}

// 显示通道详情
function showChannelDetails() {
    if (!window.channelMetricsData || !window.channelMetricsData.by_channel) {
        addLog('warning', '没有可用的通道详情数据');
        return;
    }
    
    const channelData = window.channelMetricsData.by_channel;
    const channelCount = channelData.length;
    const gridColumns = getGridColumns(channelCount);
    
    // 创建模态框
    const modal = document.createElement('div');
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.8);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 1000;
    `;
    
    // 创建模态框内容
    const modalContent = document.createElement('div');
    modalContent.style.cssText = `
        background: #2c3e50;
        border-radius: 8px;
        padding: 20px;
        max-width: 90%;
        max-height: 90%;
        overflow-y: auto;
        border: 1px solid #34495e;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
    `;
    
    // 创建标题
    const title = document.createElement('h2');
    title.textContent = '各通道评估指标详情';
    title.style.cssText = `
        color: #ecf0f1;
        margin: 0 0 20px 0;
        text-align: center;
        font-size: 18px;
    `;
    
    // 创建网格容器
    const gridContainer = document.createElement('div');
    gridContainer.style.cssText = `
        display: grid;
        grid-template-columns: repeat(${gridColumns}, 1fr);
        gap: 15px;
        margin-bottom: 20px;
    `;
    
    // 为每个通道创建指标卡片
    channelData.forEach((channelMetrics, index) => {
        const channelCard = createChannelMetricsCard(channelMetrics, index);
        gridContainer.appendChild(channelCard);
    });
    
    // 创建关闭按钮
    const closeBtn = document.createElement('button');
    closeBtn.textContent = '关闭';
    closeBtn.style.cssText = `
        background: linear-gradient(135deg, #e74c3c, #c0392b);
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 4px;
        cursor: pointer;
        font-weight: 600;
        margin-top: 15px;
        width: 100%;
    `;
    closeBtn.addEventListener('click', () => {
        document.body.removeChild(modal);
    });
    
    // 组装模态框
    modalContent.appendChild(title);
    modalContent.appendChild(gridContainer);
    modalContent.appendChild(closeBtn);
    modal.appendChild(modalContent);
    
    // 添加到页面
    document.body.appendChild(modal);
    
    // 点击背景关闭
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            document.body.removeChild(modal);
        }
    });
    
    addLog('info', `显示 ${channelCount} 个通道的详细指标`);
}

// 获取指标样式类
function getMetricClass(value, metricType) {
    const baseClass = 'metric-value';
    
    if (metricType === 'r2') {
        // R²越高越好
        if (value >= 0.8) return `${baseClass} metric-good`;
        if (value >= 0.6) return `${baseClass} metric-medium`;
        return `${baseClass} metric-poor`;
    } else {
        // MSE、MAE、RMSE越低越好
        if (value <= 0.1) return `${baseClass} metric-good`;
        if (value <= 0.3) return `${baseClass} metric-medium`;
        return `${baseClass} metric-poor`;
    }
}

// 更新图表
function updateCharts(data) {
    console.log('🔍 更新图表:', data);
    
    if (!data.predictions || !data.actual_values || !data.channels) {
        addLog('error', '图表数据不完整');
        return;
    }
    
    const chartsContainer = document.getElementById('chartsContainer');
    chartsContainer.innerHTML = '';
    
    // 为每个通道创建图表
    data.channels.forEach((channel, index) => {
        const chartId = `chart-${index}`;
        const chartContainer = document.createElement('div');
        chartContainer.className = 'chart-container';
        chartContainer.id = chartId;
        chartsContainer.appendChild(chartContainer);
        
        // 创建图表
        const chart = echarts.init(chartContainer);
        charts[chartId] = chart;
        
        // 准备数据
        const actualData = data.actual_values[index] || [];
        const predictedData = data.predictions[index] || [];
        
        // 创建时间轴
        const timeAxis = Array.from({length: Math.max(actualData.length, predictedData.length)}, (_, i) => i);
        
        // 自适应显示策略：始终显示数据的1/5
        const displayRatio = 0.2; // 显示1/5的数据
        const displayPoints = Math.ceil(actualData.length * displayRatio);
        const startIndex = 0;
        const endIndex = displayPoints;
        
        const option = {
            title: {
                text: `通道 ${index + 1}: ${channel}`,
                textStyle: {
                    color: '#ecf0f1',
                    fontSize: 14
                }
            },
            tooltip: {
                trigger: 'axis',
                backgroundColor: 'rgba(52, 73, 94, 0.9)',
                borderColor: '#34495e',
                textStyle: {
                    color: '#ecf0f1'
                }
            },
            legend: {
                data: ['实际值', '预测值'],
                textStyle: {
                    color: '#ecf0f1'
                }
            },
            grid: {
                left: '3%',
                right: '4%',
                bottom: '15%',  // 增加底部空间给滑动条
                containLabel: true
            },
            dataZoom: [
                {
                    type: 'slider',
                    show: true,
                    xAxisIndex: [0],
                    start: 0,
                    end: displayRatio * 100, // 始终显示1/5
                    bottom: 10,
                    height: 20,
                    borderColor: '#34495e',
                    backgroundColor: '#2c3e50',
                    fillerColor: '#3498db',
                    handleStyle: {
                        color: '#3498db'
                    },
                    textStyle: {
                        color: '#ecf0f1'
                    }
                },
                {
                    type: 'inside',
                    xAxisIndex: [0],
                    start: 0,
                    end: displayRatio * 100 // 始终显示1/5
                }
            ],
            xAxis: {
                type: 'category',
                data: timeAxis,
                axisLabel: {
                    color: '#bdc3c7'
                },
                axisLine: {
                    lineStyle: {
                        color: '#34495e'
                    }
                }
            },
            yAxis: {
                type: 'value',
                axisLabel: {
                    color: '#bdc3c7'
                },
                axisLine: {
                    lineStyle: {
                        color: '#34495e'
                    }
                },
                splitLine: {
                    lineStyle: {
                        color: '#34495e'
                    }
                }
            },
            series: [
                {
                    name: '实际值',
                    type: 'line',
                    data: actualData,
                    color: '#3498db',
                    smooth: true,
                    lineStyle: {
                        width: 2
                    },
                    symbol: 'none'  // 不显示数据点，提高性能
                },
                {
                    name: '预测值',
                    type: 'line',
                    data: predictedData,
                    color: '#e74c3c',
                    smooth: true,
                    lineStyle: {
                        width: 2
                    },
                    symbol: 'none'  // 不显示数据点，提高性能
                }
            ]
        };
        
        chart.setOption(option);
        
        // 添加图表信息
        addLog('info', `通道 ${index + 1}: 共 ${actualData.length} 个数据点`);
    });
    
    addLog('success', `已创建 ${data.channels.length} 个通道的对比图表，支持滑动查看完整数据`);
}

// 启用导出按钮
function enableExportButton() {
    const exportBtn = document.getElementById('exportResultsBtn');
    exportBtn.disabled = false;
    addLog('info', '预测完成，可以导出结果');
}

// 导出结果
function exportResults() {
    if (!predictionResults) {
        addLog('error', '没有可导出的预测结果');
        return;
    }
    
    addLog('info', '开始导出预测结果...');
    
    const url = `/api/export-model-prediction-results/${modelId}/`;
    
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(predictionResults)
    })
    .then(response => {
        if (response.ok) {
            return response.blob();
        }
        throw new Error('导出失败');
    })
    .then(blob => {
        // 创建下载链接
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `model_prediction_results_${modelId}_${new Date().toISOString().slice(0, 10)}.csv`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        addLog('success', '预测结果已导出');
    })
    .catch(error => {
        console.error('导出失败:', error);
        addLog('error', '导出失败');
    });
}

// 返回模型列表
function goBackToModels() {
    window.location.href = '/deep-learning/';
}

// 添加日志
function addLog(type, message) {
    const logsContainer = document.getElementById('logsContainer');
    const logEntry = document.createElement('div');
    logEntry.className = 'log-entry';
    
    const time = new Date().toLocaleTimeString();
    const logClass = `log-${type}`;
    
    logEntry.innerHTML = `
        <span class="log-time">${time}</span>
        <span class="log-message ${logClass}">${message}</span>
    `;
    
    logsContainer.appendChild(logEntry);
    logsContainer.scrollTop = logsContainer.scrollHeight;
    
    console.log(`[${type.toUpperCase()}] ${message}`);
}

// 获取Cookie
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

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    initModelPrediction();
});

// 窗口大小改变时重新调整图表
window.addEventListener('resize', function() {
    Object.values(charts).forEach(chart => {
        if (chart) {
            chart.resize();
        }
    });
}); 