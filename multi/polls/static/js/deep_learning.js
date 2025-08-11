/**
 * 深度学习模块JavaScript
 * 处理数据管理、模型训练、预测评估等功能
 * 
 * 重要说明：
 * - 学习参数相关代码位于 saveTrainingSet() 方法中
 * - 修改学习参数时请只修改 saveTrainingSet() 方法中的相关部分
 * - 其他方法都是核心功能，请勿随意修改以避免兼容性问题
 */

class DeepLearningModule {
    constructor() {
        this.currentStep = 1;
        this.trainingData = {};
        this.selectedDataSource = null;
        this.currentPage = 1;
        this.itemsPerPage = 5;
        this.filteredDataSources = [];
        this.allDataSources = []; // 存储所有数据源，用于搜索
        
        // 弹窗相关属性
        this.modalDataSources = [];
        this.modalFilteredDataSources = [];
        this.modalCurrentPage = 1;
        
        this.init();
    }

    init() {
        this.bindEvents();
        this.setCurrentDateTime();
        this.loadDataSources();
        // 确保第一步正确显示
        this.showStep(1);
    }

    /**
     * 绑定所有事件监听器
     * 注意：这是核心功能，修改学习参数时请勿修改此方法
     */
    bindEvents() {
        // 绑定标签切换事件 - 核心功能，勿修改
        document.querySelectorAll('.tab-button').forEach(button => {
            button.addEventListener('click', (e) => {
                this.switchTab(e.target.getAttribute('data-tab'));
            });
        });

        // 绑定步骤导航事件 - 核心功能，勿修改
        this.addEventListenerSafely('nextStep1', 'click', () => this.nextStep(1));
        this.addEventListenerSafely('nextStep2', 'click', () => this.nextStep(2));
        this.addEventListenerSafely('nextStep3', 'click', () => this.nextStep(3));
        
        this.addEventListenerSafely('prevStep2', 'click', () => this.prevStep(2));
        this.addEventListenerSafely('prevStep3', 'click', () => this.prevStep(3));
        this.addEventListenerSafely('prevStep4', 'click', () => this.prevStep(4));

        // 绑定保存训练集事件 - 学习参数相关，可修改
        this.addEventListenerSafely('saveTrainingSet', 'click', () => this.saveTrainingSet());

        // 绑定查看数据源事件 - 核心功能，勿修改
        this.addEventListenerSafely('refreshDataBtn', 'click', () => this.openDataSourceManagementModal());

        // 绑定训练模式选择事件 - 学习参数相关，可修改
        document.querySelectorAll('input[name="trainingMode"]').forEach(radio => {
            radio.addEventListener('change', (e) => {
                this.toggleExpertParams(e.target.value === 'expert');
            });
        });

        // 绑定搜索事件 - 核心功能，勿修改
        this.addEventListenerSafely('searchCompletedName', 'input', (e) => this.searchCompletedTraining(e.target.value));
        this.addEventListenerSafely('searchCompletedDesc', 'input', (e) => this.searchCompletedTraining(e.target.value));
        
        // 绑定训练集合列表搜索事件 - 核心功能，勿修改
        this.addEventListenerSafely('searchTrainingSetName', 'input', (e) => this.searchTrainingSetList());
        this.addEventListenerSafely('searchTrainingSetDesc', 'input', (e) => this.searchTrainingSetList());
        this.addEventListenerSafely('searchTrainingSetBtn', 'click', () => this.searchTrainingSetList());
        
        // 绑定添加训练集按钮事件 - 核心功能，勿修改
        this.addEventListenerSafely('addTrainingSetBtn', 'click', () => this.switchToNewTraining());
        
        // 绑定数据源搜索事件 - 核心功能，勿修改
        this.addEventListenerSafely('dataSourceSearch', 'input', (e) => this.searchDataSources(e.target.value));
        
        // 绑定分页事件 - 核心功能，勿修改
        this.addEventListenerSafely('prevPage', 'click', () => this.prevPage());
        this.addEventListenerSafely('nextPage', 'click', () => this.nextPage());
        
        // 绑定更换数据源事件 - 核心功能，勿修改
        this.addEventListenerSafely('changeDataSource', 'click', () => this.changeDataSource());
        
        // 绑定选择数据源按钮事件 - 核心功能，勿修改
        this.addEventListenerSafely('selectDataSourceBtn', 'click', () => this.openDataSourceModal());
        
        // 绑定数据源弹窗相关事件 - 核心功能，勿修改
        this.addEventListenerSafely('closeModal', 'click', () => this.closeDataSourceModal());
        this.addEventListenerSafely('confirmSelection', 'click', () => this.confirmDataSourceSelection());
        this.addEventListenerSafely('modalSearch', 'input', (e) => this.searchModalDataSources(e.target.value));
        this.addEventListenerSafely('modalPrevPage', 'click', () => this.modalPrevPage());
        
        // 绑定数据源管理相关事件 - 核心功能，勿修改
        this.addEventListenerSafely('closeDataSourceManagementModal', 'click', () => this.closeDataSourceManagementModal());
        this.addEventListenerSafely('closeManagementModal', 'click', () => this.closeDataSourceManagementModal());
        this.addEventListenerSafely('managementSearch', 'input', (e) => this.searchManagementDataSources(e.target.value));
        this.addEventListenerSafely('managementPrevPage', 'click', () => this.managementPrevPage());
        this.addEventListenerSafely('managementNextPage', 'click', () => this.managementNextPage());
        this.addEventListenerSafely('cancelDelete', 'click', () => this.closeDeleteConfirmModal());
        this.addEventListenerSafely('confirmDelete', 'click', () => this.performDeleteDataSource());
        this.addEventListenerSafely('modalNextPage', 'click', () => this.modalNextPage());
        this.addEventListenerSafely('cancelSelection', 'click', () => this.closeDataSourceModal());
    }

    /**
     * 安全地添加事件监听器 - 防止元素不存在时的错误
     * @param {string} elementId 元素ID
     * @param {string} eventType 事件类型
     * @param {Function} callback 回调函数
     */
    addEventListenerSafely(elementId, eventType, callback) {
        const element = document.getElementById(elementId);
        if (element) {
            element.addEventListener(eventType, callback);
        } else {
            // 只在开发模式下显示警告，减少控制台噪音
            if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
                console.debug(`元素 ${elementId} 未找到，跳过事件绑定（这是正常行为）`);
            }
        }
    }

    /**
     * 切换标签页 - 核心功能，修改学习参数时请勿修改
     * @param {string} targetTab 目标标签页
     */
    switchTab(targetTab) {
        // 更新按钮状态 - 核心功能，勿修改
        document.querySelectorAll('.tab-button').forEach(btn => {
            btn.classList.remove('border-blue-500', 'text-blue-600');
            btn.classList.add('border-transparent', 'text-gray-500');
        });
        document.querySelector(`.tab-button[data-tab="${targetTab}"]`).classList.remove('border-transparent', 'text-gray-500');
        document.querySelector(`.tab-button[data-tab="${targetTab}"]`).classList.add('border-blue-500', 'text-blue-600');
        
        // 显示对应内容 - 核心功能，勿修改
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.add('hidden');
        });
        document.getElementById(`${targetTab}-content`).classList.remove('hidden');

        // 根据标签页加载相应数据 - 核心功能，勿修改
        switch(targetTab) {
            case 'new-training':
                this.loadDataSources();
                break;
            case 'training-set-list':
                this.loadTrainingSetList();
                break;

            case 'completed-training':
                this.loadCompletedTraining();
                break;
            case 'deployed-models':
                this.loadDeployedModels();
                break;
        }
    }

    setCurrentDateTime() {
        const now = new Date();
        
        // 获取本地时间的年月日时分
        const year = now.getFullYear();
        const month = String(now.getMonth() + 1).padStart(2, '0');
        const day = String(now.getDate()).padStart(2, '0');
        const hours = String(now.getHours()).padStart(2, '0');
        const minutes = String(now.getMinutes()).padStart(2, '0');
        
        // 格式化为 YYYY-MM-DDTHH:MM 格式（本地时间）
        const dateTimeString = `${year}-${month}-${day}T${hours}:${minutes}`;
        
        const startTimeInput = document.getElementById('startTime');
        if (startTimeInput) {
            startTimeInput.value = dateTimeString;
        } else {
            console.warn('startTime 输入框未找到');
        }
    }

    nextStep(currentStep) {
        if (this.validateStep(currentStep)) {
            this.currentStep = currentStep + 1;
            this.showStep(this.currentStep);
        }
    }

    prevStep(currentStep) {
        this.currentStep = currentStep - 1;
        this.showStep(this.currentStep);
    }

    validateStep(step) {
        switch(step) {
            case 1:
                const nameEl = document.getElementById('trainingSetName');
                const descriptionEl = document.getElementById('trainingSetDescription');
                const startTimeEl = document.getElementById('startTime');
                
                if (!nameEl || !startTimeEl) {
                    this.showToast('error', '验证失败', '表单元素未找到');
                    return false;
                }
                
                const name = nameEl.value.trim();
                const description = descriptionEl ? descriptionEl.value.trim() : '';
                const startTime = startTimeEl.value;

                if (!name) {
                    this.showToast('error', '验证失败', '请输入训练集名称');
                    return false;
                }
                if (!startTime) {
                    this.showToast('error', '验证失败', '请选择训练开始时间');
                    return false;
                }

                // 保存步骤1数据
                this.trainingData.basicInfo = {
                    name: name,
                    description: description,
                    startTime: startTime
                };
                break;

            case 2:
                const modelTypeEl = document.getElementById('modelType');
                const trainingMode = document.querySelector('input[name="trainingMode"]:checked');
                
                if (!modelTypeEl) {
                    this.showToast('error', '验证失败', '模型类型选择器未找到');
                    return false;
                }
                
                const modelType = modelTypeEl.value;

                if (!modelType) {
                    this.showToast('error', '验证失败', '请选择模型类型');
                    return false;
                }
                if (!trainingMode) {
                    this.showToast('error', '验证失败', '请选择训练模式');
                    return false;
                }

                // 保存步骤2数据
                this.trainingData.trainingMode = {
                    modelType: modelType,
                    mode: trainingMode.value
                };
                break;

            case 3:
                const selectedDataSource = this.selectedDataSource;
                const trainRatioEl = document.getElementById('trainRatio');
                const valRatioEl = document.getElementById('valRatio');
                const testRatioEl = document.getElementById('testRatio');
                
                if (!trainRatioEl || !valRatioEl || !testRatioEl) {
                    this.showToast('error', '验证失败', '数据分配比例输入框未找到');
                    return false;
                }
                
                const trainRatio = parseInt(trainRatioEl.value);
                const valRatio = parseInt(valRatioEl.value);
                const testRatio = parseInt(testRatioEl.value);

                if (!selectedDataSource) {
                    this.showToast('error', '验证失败', '请选择一个数据源');
                    return false;
                }
                if (trainRatio + valRatio + testRatio !== 100) {
                    this.showToast('error', '验证失败', '训练集、验证集、测试集比例之和必须为100%');
                    return false;
                }

                // 保存步骤3数据
                this.trainingData.dataSelection = {
                    dataSource: selectedDataSource,
                    trainRatio: trainRatio,
                    valRatio: valRatio,
                    testRatio: testRatio
                };
                break;
        }
        return true;
    }

    showStep(step) {
        // 隐藏所有步骤内容
        document.querySelectorAll('.step-content').forEach(content => {
            content.classList.add('hidden');
        });
        
        // 显示当前步骤内容
        const currentStepContent = document.getElementById(`step-${step}`);
        if (currentStepContent) {
            currentStepContent.classList.remove('hidden');
        } else {
            console.warn(`步骤 ${step} 的内容元素未找到`);
        }
        
        // 更新步骤指示器
        this.updateStepIndicator(step);
    }

    updateStepIndicator(currentStep) {
        console.log('更新步骤指示器到步骤:', currentStep);
        
        // 获取所有步骤指示器
        const stepIndicators = document.querySelectorAll('.step-indicator');
        console.log('找到步骤指示器数量:', stepIndicators.length);
        
        stepIndicators.forEach((indicator, index) => {
            const stepNumber = index + 1;
            const circle = indicator.querySelector('.step-circle');
            const text = indicator.querySelector('.step-text');
            
            console.log('步骤 ' + stepNumber + ':', { stepNumber: stepNumber, currentStep: currentStep, isActive: stepNumber <= currentStep });
            
            if (stepNumber <= currentStep) {
                // 已完成或当前步骤 - 蓝色
                circle.classList.remove('bg-gray-200', 'text-gray-500');
                circle.classList.add('bg-blue-600', 'text-white');
                text.classList.remove('text-gray-500');
                text.classList.add('text-blue-600');
                console.log('步骤 ' + stepNumber + ' 设置为蓝色');
            } else {
                // 未完成步骤 - 灰色
                circle.classList.remove('bg-blue-600', 'text-white');
                circle.classList.add('bg-gray-200', 'text-gray-500');
                text.classList.remove('text-blue-600');
                text.classList.add('text-gray-500');
                console.log('步骤 ' + stepNumber + ' 设置为灰色');
            }
        });
        
        // 更新连接线
        const borders = document.querySelectorAll('.flex-auto.border-t-2');
        borders.forEach((border, index) => {
            const stepNumber = index + 1;
            if (stepNumber < currentStep) {
                // 已完成步骤之间的连接线 - 蓝色
                border.classList.remove('border-gray-300');
                border.classList.add('border-blue-600');
            } else {
                // 未完成步骤之间的连接线 - 灰色
                border.classList.remove('border-blue-600');
                border.classList.add('border-gray-300');
            }
        });
    }

    async loadInitialData() {
        try {
            const response = await fetch('/api/get-monitor-data-for-dl/');
            const data = await response.json();
            
            if (data.success) {
                this.updateDataStats(data);
            }
        } catch (error) {
            console.error('加载初始数据失败:', error);
            this.showToast('error', '加载失败', '无法加载监控数据');
        }
    }

    updateDataStats(data) {
        // 更新统计数据
        console.log('更新数据统计:', data);
    }

    /**
     * 加载数据源 - 核心功能，修改学习参数时请勿修改
     * 此方法负责从后端API获取数据源列表，是数据选择功能的核心
     */
    async loadDataSources() {
        try {
            const response = await fetch('/api/get-monitor-data-for-dl/', {
                headers: {
                    'X-CSRFToken': this.getCookie('csrftoken')
                }
            });

            const data = await response.json();
            
            if (data.success) {
                this.allDataSources = data.data_list; // 存储所有数据源
                this.filteredDataSources = [...this.allDataSources]; // 初始化过滤后的数据源
                this.renderDataSources();
            } else {
                this.showToast('error', '加载失败', data.message);
            }
        } catch (error) {
            console.error('加载数据源失败:', error);
            this.showToast('error', '加载失败', '网络请求失败');
        }
    }

    /**
     * 搜索数据源 - 核心功能，修改学习参数时请勿修改
     * 此方法负责实时搜索和过滤数据源，是数据选择功能的核心
     */
    searchDataSources(searchTerm) {
        const searchLower = searchTerm.toLowerCase();
        
        // 过滤数据源
        this.filteredDataSources = this.allDataSources.filter(item => {
            const name = item.task_name.toLowerCase();
            const description = (item.task_description || '').toLowerCase();
            return name.includes(searchLower) || description.includes(searchLower);
        });
        
        // 重置到第一页
        this.currentPage = 1;
        
        // 重新渲染
        this.renderDataSources();
    }

    /**
     * 渲染数据源列表 - 核心功能，修改学习参数时请勿修改
     * 此方法负责渲染数据源列表的HTML，是数据选择功能的核心
     */
    renderDataSources() {
        const container = document.getElementById('dataSourceList');
        
        // 添加null检查
        if (!container) {
            // 只在开发模式下显示警告
            if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
                console.debug('dataSourceList 元素未找到，可能不在当前标签页（这是正常行为）');
            }
            return;
        }
        
        if (!this.filteredDataSources || this.filteredDataSources.length === 0) {
            container.innerHTML = `
                <div class="text-center py-8 text-gray-500">
                    <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                    </svg>
                    <p class="mt-2 text-sm">暂无可用数据源</p>
                    <p class="text-xs text-gray-400">请先在监控模块中创建数据采集任务</p>
                </div>
            `;
            this.updatePagination();
            return;
        }

        // 计算分页
        const startIndex = (this.currentPage - 1) * this.itemsPerPage;
        const endIndex = startIndex + this.itemsPerPage;
        const pageData = this.filteredDataSources.slice(startIndex, endIndex);
        
        container.innerHTML = pageData.map(item => `
            <div class="data-source-item bg-white border border-gray-200 rounded-lg p-4 hover:border-blue-300 hover:shadow-md transition-all duration-200 cursor-pointer" data-task-id="${item.task_id}">
                <div class="flex items-start space-x-3">
                    <div class="flex-shrink-0">
                        <input type="radio" name="dataSource" value="${item.task_id}" class="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300">
                    </div>
                    <div class="flex-1 min-w-0">
                        <div class="flex items-center justify-between">
                            <div class="flex-1">
                                <div class="data-source-name font-medium text-gray-900 text-sm">${item.task_name}</div>
                                <div class="data-source-desc text-gray-600 text-xs mt-1">${item.task_description || '无描述'}</div>
                            </div>
                            <div class="ml-4 flex-shrink-0">
                                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                                    ${item.file_size_mb} MB
                                </span>
                            </div>
                        </div>
                        <div class="mt-2 flex items-center text-xs text-gray-500 space-x-4">
                            <span class="flex items-center">
                                <svg class="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clip-rule="evenodd"></path>
                                </svg>
                                ${new Date(item.created_at).toLocaleDateString()}
                            </span>
                            <span class="flex items-center">
                                <svg class="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                                    <path fill-rule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zM3 10a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zM14 9a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 001-1v-6a1 1 0 00-1-1h-2z" clip-rule="evenodd"></path>
                                </svg>
                                ${item.total_data_points.toLocaleString()} 点
                            </span>
                            <span class="flex items-center">
                                <svg class="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                                    <path fill-rule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zM3 10a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zM14 9a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 001-1v-6a1 1 0 00-1-1h-2z" clip-rule="evenodd"></path>
                                </svg>
                                ${item.enabled_channels.length} 通道
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
        
        // 绑定单选事件
        container.querySelectorAll('input[name="dataSource"]').forEach(radio => {
            radio.addEventListener('change', (e) => {
                this.selectDataSource(e.target.value);
            });
        });
        
        // 绑定点击事件
        container.querySelectorAll('.data-source-item').forEach(item => {
            item.addEventListener('click', (e) => {
                if (e.target.type !== 'radio') {
                    const radio = item.querySelector('input[type="radio"]');
                    radio.checked = true;
                    this.selectDataSource(radio.value);
                }
            });
        });
        
        this.updatePagination();
    }

    selectDataSource(taskId) {
        const selectedItem = this.filteredDataSources.find(item => item.task_id === taskId);
        if (selectedItem) {
            this.selectedDataSource = selectedItem;
            this.showSelectedDataSource();
        }
    }

    showSelectedDataSource() {
        const container = document.getElementById('selectedDataSource');
        const info = document.getElementById('selectedDataSourceInfo');
        
        // 添加null检查
        if (!container || !info) {
            console.warn('selectedDataSource 或 selectedDataSourceInfo 元素未找到');
            return;
        }
        
        if (this.selectedDataSource) {
            info.textContent = `${this.selectedDataSource.task_name} - ${this.selectedDataSource.file_size_mb} MB - ${this.selectedDataSource.total_data_points.toLocaleString()} 点`;
            container.classList.remove('hidden');
        } else {
            container.classList.add('hidden');
        }
    }

    changeDataSource() {
        this.selectedDataSource = null;
        const selectedContainer = document.getElementById('selectedDataSource');
        if (selectedContainer) {
            selectedContainer.classList.add('hidden');
        }
        // 清除所有选择
        document.querySelectorAll('input[name="dataSource"]').forEach(radio => {
            radio.checked = false;
        });
    }

    updatePagination() {
        const totalItems = this.filteredDataSources.length;
        const totalPages = Math.ceil(totalItems / this.itemsPerPage);
        const startItem = (this.currentPage - 1) * this.itemsPerPage + 1;
        const endItem = Math.min(this.currentPage * this.itemsPerPage, totalItems);
        
        // 更新信息 - 添加null检查
        const currentPageInfo = document.getElementById('currentPageInfo');
        const totalItemsEl = document.getElementById('totalItems');
        const prevPageBtn = document.getElementById('prevPage');
        const nextPageBtn = document.getElementById('nextPage');
        
        if (currentPageInfo) currentPageInfo.textContent = `${startItem}-${endItem}`;
        if (totalItemsEl) totalItemsEl.textContent = totalItems;
        if (prevPageBtn) prevPageBtn.disabled = this.currentPage <= 1;
        if (nextPageBtn) nextPageBtn.disabled = this.currentPage >= totalPages;
        
        // 更新页码 - 添加null检查
        const pageNumbersContainer = document.getElementById('pageNumbers');
        if (pageNumbersContainer) {
            pageNumbersContainer.innerHTML = '';
            
            for (let i = 1; i <= totalPages; i++) {
                const button = document.createElement('button');
                button.className = `px-3 py-1 text-sm border rounded-md ${i === this.currentPage ? 'bg-blue-600 text-white border-blue-600' : 'border-gray-300 hover:bg-gray-50'}`;
                button.textContent = i;
                button.addEventListener('click', () => this.goToPage(i));
                pageNumbersContainer.appendChild(button);
            }
        }
    }

    prevPage() {
        if (this.currentPage > 1) {
            this.currentPage--;
            this.renderDataSources();
        }
    }

    nextPage() {
        const totalPages = Math.ceil(this.filteredDataSources.length / this.itemsPerPage);
        if (this.currentPage < totalPages) {
            this.currentPage++;
            this.renderDataSources();
        }
    }

    goToPage(page) {
        this.currentPage = page;
        this.renderDataSources();
    }



    async loadCompletedTraining() {
        try {
            const response = await fetch('/api/get-completed-training/', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCookie('csrftoken')
                }
            });

            const data = await response.json();
            
            if (data.success) {
                this.currentCompletedTrainingData = data.completed_data; // 存储当前数据
                this.renderCompletedTraining(data.completed_data);
            } else {
                console.error('获取训练完成数据集失败:', data.message);
                this.showToast('error', '加载失败', data.message);
            }
        } catch (error) {
            console.error('加载训练完成数据集失败:', error);
            this.showToast('error', '加载失败', '网络请求失败');
        }
    }

    renderCompletedTraining(completedData) {
        const container = document.getElementById('completedTrainingTable');
        

        
        if (!completedData || completedData.length === 0) {
            container.innerHTML = `
                <tr>
                    <td colspan="9" class="px-6 py-4 text-center text-gray-500">
                        暂无训练完成的数据集
                    </td>
                </tr>
            `;
            return;
        }

        const rows = completedData.map(item => `
            <tr class="hover:bg-gray-50">
                <td class="px-6 py-4 whitespace-nowrap">
                    <input type="checkbox" class="rounded border-gray-300 text-blue-600 focus:ring-blue-500">
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">${item.name}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${item.start_time || '未设置'}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${item.duration_minutes || 0}</td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <div class="flex items-center">
                        <div class="w-16 bg-gray-200 rounded-full h-2 mr-2">
                            <div class="bg-green-600 h-2 rounded-full" style="width: ${item.progress}%"></div>
                        </div>
                        <span class="text-sm text-gray-900">${item.progress}%</span>
                    </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${item.measurement_points || 0}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${item.record_count || 0}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${item.validation || '自测'}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <button class="text-blue-600 hover:text-blue-900 mr-2" onclick="deepLearningModule.viewCompletedTraining('${item.training_set_id}')">查看</button>
                    <button class="text-green-600 hover:text-green-900 mr-2">详情</button>
                    <button class="text-purple-600 hover:text-purple-900 mr-2">原始数据</button>
                    <button class="text-orange-600 hover:text-orange-900 mr-2">训练结果</button>
                    <button class="text-indigo-600 hover:text-indigo-900 mr-2">投运</button>
                    <button class="text-gray-600 hover:text-gray-900">...</button>
                </td>
            </tr>
        `).join('');

        container.innerHTML = rows;
        document.getElementById('completedTotalCount').textContent = completedData.length;
    }

    async loadDeployedModels() {
        try {
            const response = await fetch('/api/get-deployed-models/');
                const data = await response.json();
                
                if (data.success) {
                this.renderDeployedModels(data.deployed_models);
                }
            } catch (error) {
            console.error('加载已投运模型失败:', error);
        }
    }

    renderDeployedModels(models) {
        const container = document.getElementById('deployedModelsList');
        
        if (!models || models.length === 0) {
            container.innerHTML = `
                <div class="text-gray-500 text-center py-8">
                    <svg class="w-12 h-12 mx-auto text-gray-400 mb-2" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                    </svg>
                    <p>暂无已投运模型</p>
                    <p class="text-sm">请先完成模型训练并投运</p>
                </div>
            `;
            return;
        }

        const modelsHtml = models.map(model => `
            <div class="bg-white rounded-lg p-4 border border-gray-200 hover:border-green-300 transition-colors">
                <div class="flex items-center justify-between">
                    <div>
                        <h4 class="font-semibold text-gray-800">${model.model_name}</h4>
                        <p class="text-sm text-gray-600">类型: ${model.model_type.toUpperCase()}</p>
                        <div class="flex gap-4 mt-2 text-xs text-gray-500">
                            <span>准确率: ${(model.accuracy * 100).toFixed(1)}%</span>
                            <span>数据集: ${model.dataset_id}</span>
                        </div>
                    </div>
                    <div class="text-right">
                        <p class="text-sm text-gray-500">${new Date(model.deployed_at).toLocaleDateString()}</p>
                        <div class="flex gap-2 mt-2">
                            <button class="px-3 py-1 bg-blue-600 text-white text-xs rounded hover:bg-blue-700" onclick="deepLearningModule.predictModel('${model.model_id}')">预测</button>
                            <button class="px-3 py-1 bg-red-600 text-white text-xs rounded hover:bg-red-700" onclick="deepLearningModule.deleteModel('${model.model_id}')">删除</button>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');

        container.innerHTML = modelsHtml;
    }

    /**
     * 保存训练集配置 - 学习参数相关核心方法
     * 注意：这是学习参数的主要处理逻辑，添加新的学习参数时请在此方法中修改
     * 修改时请确保：
     * 1. 只修改 basicParams 和 expertParams 对象
     * 2. 保持现有的API调用结构不变
     * 3. 不要修改其他核心功能
     */
    async saveTrainingSet() {
        // 收集步骤4的基础参数 - 学习参数相关，可修改
        const basicParams = {
            learningRate: parseFloat(document.getElementById('learningRate').value),
            epochs: parseInt(document.getElementById('epochs').value),
            batchSize: parseInt(document.getElementById('batchSize').value),
            optimizer: document.getElementById('optimizer').value,
            windowSize: parseInt(document.getElementById('windowSize').value),
            horizon: parseInt(document.getElementById('horizon').value)
        };

        // 收集专家模式参数（如果启用） - 学习参数相关，可修改
        const trainingMode = this.trainingData.trainingMode?.mode;
        let expertParams = {};
        
        if (trainingMode === 'expert') {
            // 专家模式：使用用户设置的专家参数 - 学习参数相关，可修改
            expertParams = {
                weightDecay: parseFloat(document.getElementById('weightDecay').value),
                dropoutRate: parseFloat(document.getElementById('dropoutRate').value),
                lossFunction: document.getElementById('lossFunction').value,
                earlyStoppingPatience: parseInt(document.getElementById('earlyStoppingPatience').value),
                learningRateScheduler: document.getElementById('learningRateScheduler').value,
                randomSeed: parseInt(document.getElementById('randomSeed').value),
                lstmLayers: parseInt(document.getElementById('lstmLayers').value),
                hiddenSize: parseInt(document.getElementById('hiddenSize').value),
                evaluationMetric: document.getElementById('evaluationMetric').value
            };
        } else {
            // 用户自选模式：使用默认的专家参数 - 学习参数相关，可修改
            expertParams = {
                weightDecay: 0.0001,              // 默认0.0001
                dropoutRate: 0.1,                 // 默认0.1
                lossFunction: 'mse',              // 默认MSE
                earlyStoppingPatience: 5,         // 默认5轮
                learningRateScheduler: 'step',    // 默认StepLR
                randomSeed: 42,                   // 默认42
                lstmLayers: 1,                    // 默认1层
                hiddenSize: 64,                   // 默认64
                evaluationMetric: 'mse'           // 默认MSE
            };
        }

        // 组装学习参数 - 学习参数相关，可修改
        this.trainingData.learningParams = {
            basic: basicParams,
            expert: expertParams,
            mode: trainingMode
        };

        // 显示保存提示 - 核心功能，勿修改
        this.showToast('info', '保存训练集', '正在保存训练集配置...');

        try {
            // API调用 - 核心功能，勿修改
            const response = await fetch('/api/create-training-set/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCookie('csrftoken')
                },
                body: JSON.stringify(this.trainingData)
            });

            const data = await response.json();
            
            if (data.success) {
                this.showToast('success', '保存成功', '训练集配置已保存');
                // 重置表单 - 核心功能，勿修改
                this.resetForm();
                // 跳转到训练集列表页面 - 核心功能，勿修改
                this.switchTab('training-set-list');
            } else {
                this.showToast('error', '保存失败', data.message);
            }
        } catch (error) {
            console.error('保存训练集失败:', error);
            this.showToast('error', '保存失败', '网络请求失败');
        }
    }

    resetForm() {
        // 重置所有表单字段 - 添加null检查
        const trainingSetName = document.getElementById('trainingSetName');
        const trainingSetDescription = document.getElementById('trainingSetDescription');
        
        if (trainingSetName) trainingSetName.value = '';
        if (trainingSetDescription) trainingSetDescription.value = '';
        
        // 重置步骤指示器
        this.currentStep = 1;
        this.showStep(1);
        this.updateStepIndicator();
        
        // 重置学习参数字段
        const basicParamFields = ['learningRate', 'epochs', 'batchSize', 'windowSize', 'horizon', 'optimizer'];
        basicParamFields.forEach(fieldId => {
            const element = document.getElementById(fieldId);
            if (element) {
                if (fieldId === 'learningRate') element.value = '0.001';
                else if (fieldId === 'epochs') element.value = '100';
                else if (fieldId === 'batchSize') element.value = '32';
                else if (fieldId === 'windowSize') element.value = '24';
                else if (fieldId === 'horizon') element.value = '12';
                else if (fieldId === 'optimizer') element.value = 'adam';
            }
        });
        
        // 重置数据分配比例参数
        const dataRatioFields = ['trainRatio', 'valRatio', 'testRatio'];
        dataRatioFields.forEach(fieldId => {
            const element = document.getElementById(fieldId);
            if (element) {
                if (fieldId === 'trainRatio') element.value = '70';
                else if (fieldId === 'valRatio') element.value = '15';
                else if (fieldId === 'testRatio') element.value = '15';
            }
        });
        
        // 重置模型类型和训练模式
        const modelTypeEl = document.getElementById('modelType');
        if (modelTypeEl) modelTypeEl.value = 'lstm';
        
        // 重置训练模式选择
        const trainingModeRadios = document.querySelectorAll('input[name="trainingMode"]');
        trainingModeRadios.forEach(radio => {
            radio.checked = false;
        });
        
        // 隐藏专家参数区域
        this.toggleExpertParams(false);
        
        // 重置数据源选择
        this.selectedDataSource = null;
        const selectedDataSourceDiv = document.getElementById('selectedDataSource');
        if (selectedDataSourceDiv) selectedDataSourceDiv.classList.add('hidden');
        
        // 重置数据源选择按钮
        const selectDataSourceBtn = document.getElementById('selectDataSourceBtn');
        if (selectDataSourceBtn) selectDataSourceBtn.classList.remove('hidden');
        
        // 重置专家模式参数字段
        const expertParamFields = ['weightDecay', 'dropoutRate', 'lossFunction', 'earlyStoppingPatience', 'learningRateScheduler', 'randomSeed', 'lstmLayers', 'hiddenSize', 'evaluationMetric'];
        expertParamFields.forEach(fieldId => {
            const element = document.getElementById(fieldId);
            if (element) {
                if (fieldId === 'weightDecay') element.value = '0.0001';
                else if (fieldId === 'dropoutRate') element.value = '0.2';
                else if (fieldId === 'lossFunction') element.value = 'mse';
                else if (fieldId === 'earlyStoppingPatience') element.value = '10';
                else if (fieldId === 'learningRateScheduler') element.value = 'none';
                else if (fieldId === 'randomSeed') element.value = '42';
                else if (fieldId === 'lstmLayers') element.value = '1';
                else if (fieldId === 'hiddenSize') element.value = '64';
                else if (fieldId === 'evaluationMetric') element.value = 'mse';
            }
        });
        
        // 清空训练数据
        this.trainingData = {};
        
        // 重新设置当前时间
        this.setCurrentDateTime();
    }



    async searchCompletedTraining(name) {
        // 实现训练完成数据集的搜索过滤
        if (this.currentCompletedTrainingData) {
            const filteredData = this.currentCompletedTrainingData.filter(item => {
                const nameMatch = !name || item.name.toLowerCase().includes(name.toLowerCase());
                return nameMatch;
            });
            
            this.renderCompletedTraining(filteredData);
        }
    }

    async refreshData() {
        this.showToast('info', '刷新数据', '正在刷新可用数据源...');
        
        try {
            const response = await fetch('/api/get-monitor-data-for-dl/');
            const data = await response.json();
            
            if (data.success) {
                this.updateDataStats(data);
                this.showToast('success', '刷新成功', `找到 ${data.total_count} 个可用数据集`);
            } else {
                this.showToast('error', '刷新失败', data.message);
            }
        } catch (error) {
            console.error('刷新数据失败:', error);
            this.showToast('error', '刷新失败', '网络请求失败');
        }
    }

    /**
     * 显示Toast通知 - 核心功能，修改学习参数时请勿修改
     * 此方法负责显示各种类型的通知消息
     */
    showToast(type, title, message) {
        const toast = document.getElementById('toast');
        const icon = document.getElementById('toastIcon');
        const titleEl = document.getElementById('toastTitle');
        const messageEl = document.getElementById('toastMessage');

        let iconSvg = '';
        
        switch(type) {
            case 'success':
                iconSvg = '<svg class="w-6 h-6 text-green-600" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path></svg>';
                break;
            case 'error':
                iconSvg = '<svg class="w-6 h-6 text-red-600" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"></path></svg>';
                break;
            case 'info':
                iconSvg = '<svg class="w-6 h-6 text-blue-600" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"></path></svg>';
                break;
        }

        icon.innerHTML = iconSvg;
        titleEl.textContent = title;
        messageEl.textContent = message;

        toast.classList.remove('hidden');
        
        setTimeout(() => {
            toast.classList.add('hidden');
        }, 3000);
    }

    /**
     * 获取Cookie值 - 核心功能，修改学习参数时请勿修改
     * 此方法用于获取CSRF token等Cookie值
     */
    getCookie(name) {
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

    /**
     * 切换专家模式参数显示 - 学习参数相关，可修改
     * @param {boolean} isExpert 是否为专家模式
     */
    toggleExpertParams(isExpert) {
        const expertParams = document.getElementById('expertParams');
        if (expertParams) {
            if (isExpert) {
                expertParams.classList.remove('hidden');
            } else {
                expertParams.classList.add('hidden');
            }
        }
    }

    /**
     * 训练集合列表相关函数 - 核心功能，修改学习参数时请勿修改
     */
    async loadTrainingSetList() {
        try {
            const response = await fetch('/api/get-training-sets/', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCookie('csrftoken')
                }
            });

            const data = await response.json();
            
            if (data.success) {
                this.currentTrainingSetsData = data.training_sets; // 存储当前加载的训练集数据
                this.renderTrainingSetList(data.training_sets);
            } else {
                console.error('获取训练集合列表失败:', data.message);
                this.showToast('error', '加载失败', data.message);
            }
        } catch (error) {
            console.error('加载训练集合列表失败:', error);
            this.showToast('error', '加载失败', '网络请求失败');
        }
    }

    renderTrainingSetList(data) {
        const tableBody = document.getElementById('trainingSetListTable');
        const totalCount = document.getElementById('trainingSetTotalCount');
        
        // 添加null检查
        if (!tableBody) {
            // 只在开发模式下显示警告
            if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
                console.debug('trainingSetListTable 元素未找到，可能不在当前标签页（这是正常行为）');
            }
            return;
        }
        
        if (!totalCount) {
            // 只在开发模式下显示警告
            if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
                console.debug('trainingSetTotalCount 元素未找到，可能不在当前标签页（这是正常行为）');
            }
            return;
        }
        
        totalCount.textContent = data.length;
        
        if (data.length === 0) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="11" class="px-6 py-4 text-center text-gray-500">
                        暂无训练集合数据
                    </td>
                </tr>
            `;
            return;
        }
        
        tableBody.innerHTML = data.map(item => {

            
            // 格式化时间 - 修复时间显示问题
            let startTime = '未设置';
            let endTime = '未完成';
            
            try {
                if (item.start_time) {
                    const startDate = new Date(item.start_time);
                    if (!isNaN(startDate.getTime())) {
                        startTime = startDate.toLocaleString('zh-CN', {
                            year: 'numeric',
                            month: '2-digit',
                            day: '2-digit',
                            hour: '2-digit',
                            minute: '2-digit',
                            second: '2-digit'
                        });
                    }
                }
                
                if (item.end_time) {
                    const endDate = new Date(item.end_time);
                    if (!isNaN(endDate.getTime())) {
                        endTime = endDate.toLocaleString('zh-CN', {
                            year: 'numeric',
                            month: '2-digit',
                            day: '2-digit',
                            hour: '2-digit',
                            minute: '2-digit',
                            second: '2-digit'
                        });
                    }
                }
            } catch (error) {
                console.warn('时间格式化失败:', error);
                startTime = '时间格式错误';
                endTime = '时间格式错误';
            }
            
            // 格式化训练模式
            const modeText = item.training_mode === 'expert' ? '专家模式' : '用户自选';
            
            // 格式化状态
            const statusText = {
                'pending': '待开始',
                'training': '训练中',
                'completed': '已完成',
                'failed': '失败'
            }[item.status] || item.status;
            
            const statusClass = {
                'pending': 'bg-yellow-100 text-yellow-800',
                'training': 'bg-blue-100 text-blue-800',
                'completed': 'bg-green-100 text-green-800',
                'failed': 'bg-red-100 text-red-800'
            }[item.status] || 'bg-gray-100 text-gray-800';
            
            return `
                <tr class="hover:bg-gray-50">
                    <td class="px-6 py-4 whitespace-nowrap">
                        <input type="checkbox" class="rounded border-gray-300 text-blue-600 focus:ring-blue-500">
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">${item.name}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${item.description}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${modeText}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${startTime}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${item.measurement_points.toLocaleString()}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${item.record_count.toLocaleString()}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${item.creator}</td>
                    <td class="px-6 py-4 whitespace-nowrap">
                        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${statusClass}">
                            ${statusText}
                        </span>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <div class="flex items-center space-x-2">
                            <button class="text-blue-600 hover:text-blue-900" onclick="deepLearningModule.viewTrainingSet('${item.training_set_id}')">
                                查看
                            </button>
                            <button class="text-green-600 hover:text-green-900" onclick="deepLearningModule.startTraining('${item.training_set_id}')">
                                开始训练
                            </button>
                            <button class="text-red-600 hover:text-red-900" onclick="deepLearningModule.deleteTrainingSet('${item.training_set_id}')">
                                删除
                            </button>
                        </div>
                    </td>
                </tr>
            `;
        }).join('');
    }

    viewTrainingSet(id) {
        console.log('🔍 查看训练集，训练集ID:', id);
        
        // 从当前渲染的数据中找到对应的训练集信息
        const trainingSet = this.currentTrainingSetsData?.find(item => item.training_set_id === id);
        
        if (!trainingSet) {
            this.showToast('error', '查看失败', '未找到训练集信息');
            return;
        }
        
        // 根据训练状态决定行为
        if (trainingSet.status === 'completed') {
            // 已完成的训练集，跳转到查看页面
            const monitorUrl = `/training-monitor/?id=${id}`;
            window.open(monitorUrl, '_blank', 'width=1200,height=800,scrollbars=yes,resizable=yes');
            this.showToast('info', '查看训练结果', '正在打开训练完成页面...');
        } else if (trainingSet.status === 'training') {
            // 训练中的训练集，跳转到训练监控页面
            const monitorUrl = `/training-monitor/?id=${id}`;
            window.open(monitorUrl, '_blank', 'width=1200,height=800,scrollbars=yes,resizable=yes');
            this.showToast('info', '查看训练进度', '正在打开训练监控页面...');
        } else if (trainingSet.status === 'pending') {
            // 待开始的训练集
            this.showToast('info', '训练集状态', '此训练集尚未开始训练，请先点击"开始训练"');
        } else if (trainingSet.status === 'failed') {
            // 失败的训练集
            this.showToast('error', '训练失败', '此训练集训练失败，无法查看结果');
        } else {
            // 未知状态
            this.showToast('error', '查看失败', '训练集状态未知，无法查看');
        }
    }

    viewCompletedTraining(trainingSetId) {
        console.log('🔍 查看已完成的训练，训练集ID:', trainingSetId);
        
        // 跳转到训练监控页面，显示已完成状态
        const monitorUrl = `/training-monitor/?id=${trainingSetId}`;
        window.open(monitorUrl, '_blank', 'width=1200,height=800,scrollbars=yes,resizable=yes');
        
        this.showToast('info', '查看训练结果', '正在打开训练完成页面...');
    }

    predictModel(modelId) {
        console.log('🔍 开始模型预测，模型ID:', modelId);
        const predictionUrl = `/model-prediction/${modelId}/`;
        window.open(predictionUrl, '_blank', 'width=1200,height=800,scrollbars=yes,resizable=yes');
        this.showToast('info', '模型预测', '正在打开模型预测页面...');
    }

    deleteModel(modelId) {
        console.log('🔍 删除模型，模型ID:', modelId);
        if (confirm('确定要删除这个模型吗？此操作不可恢复。')) {
            this.performDeleteModel(modelId);
        }
    }

    async performDeleteModel(modelId) {
        try {
            const response = await fetch(`/api/delete-model/${modelId}/`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': this.getCookie('csrftoken')
                }
            });

            const data = await response.json();
            
            if (data.success) {
                this.showToast('success', '删除成功', '模型已成功删除');
                this.loadDeployedModels(); // 重新加载模型列表
            } else {
                this.showToast('error', '删除失败', data.message || '删除模型时发生错误');
            }
        } catch (error) {
            console.error('删除模型失败:', error);
            this.showToast('error', '删除失败', '网络错误，请稍后重试');
        }
    }


    async startTraining(id) {
        console.log('🚀 开始训练，训练集ID:', id);
        
        try {
            // 显示加载状态
            this.showToast('info', '开始训练', '正在启动训练进程...');
            
            // 发送开始训练请求
            const response = await fetch('/api/start-training-from-set/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCookie('csrftoken')
                },
                body: JSON.stringify({
                    training_set_id: id
                })
            });

            const data = await response.json();
            
            if (data.success) {
                this.showToast('success', '训练已启动', data.message);
                console.log('✅ 训练启动成功:', data);
                
                // 在新窗口中打开训练监控页面
                const monitorUrl = `/training-monitor/?id=${id}`;
                window.open(monitorUrl, '_blank', 'width=1200,height=800,scrollbars=yes,resizable=yes');
                
                // 刷新训练集列表以更新状态
                setTimeout(() => {
                    this.loadTrainingSetList();
                }, 2000);
                
            } else {
                this.showToast('error', '启动训练失败', data.message);
                console.error('❌ 训练启动失败:', data);
            }
            
        } catch (error) {
            console.error('❌ 启动训练时发生错误:', error);
            this.showToast('error', '启动训练失败', '网络请求失败，请检查控制台');
        }
    }

    deleteTrainingSet(id) {
        if (confirm('确定要删除这个训练集吗？')) {
            this.performDeleteTrainingSet(id);
        }
    }

    async performDeleteTrainingSet(id) {
        try {
            const response = await fetch(`/api/delete-training-set/${id}/`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCookie('csrftoken')
                }
            });

            const data = await response.json();
            
            if (data.success) {
                this.showToast('success', '删除成功', '训练集已删除');
                this.loadTrainingSetList(); // 重新加载列表
            } else {
                this.showToast('error', '删除失败', data.message);
            }
        } catch (error) {
            console.error('删除训练集失败:', error);
            this.showToast('error', '删除失败', '网络请求失败');
        }
    }

    searchTrainingSetList(searchTerm = '') {
        // 获取搜索输入框的值
        const nameSearch = document.getElementById('searchTrainingSetName')?.value || '';
        const descSearch = document.getElementById('searchTrainingSetDesc')?.value || '';
        
        // 如果两个搜索框都为空，重新加载所有数据
        if (!nameSearch && !descSearch) {
            this.loadTrainingSetList();
            return;
        }

        // 过滤当前数据
        if (this.currentTrainingSetsData) {
            const filteredData = this.currentTrainingSetsData.filter(item => {
                const nameMatch = !nameSearch || item.name.toLowerCase().includes(nameSearch.toLowerCase());
                const descMatch = !descSearch || (item.description && item.description.toLowerCase().includes(descSearch.toLowerCase()));
                return nameMatch && descMatch;
            });
            
            this.renderTrainingSetList(filteredData);
        }
    }

    switchToNewTraining() {
        // 切换到新建训练集标签页
        this.switchTab('new-training');
    }

    /**
     * 数据源选择弹窗相关方法 - 核心功能，勿修改
     */
    
    // 打开数据源选择弹窗
    openDataSourceModal() {
        console.log('打开数据源选择弹窗');
        const modal = document.getElementById('dataSourceModal');
        if (modal) {
            modal.classList.remove('hidden');
            // 加载数据源数据
            this.loadModalDataSources();
        } else {
            console.error('数据源弹窗元素未找到');
        }
    }

    // 关闭数据源选择弹窗
    closeDataSourceModal() {
        console.log('关闭数据源选择弹窗');
        const modal = document.getElementById('dataSourceModal');
        if (modal) {
            modal.classList.add('hidden');
        }
    }

    // 确认数据源选择
    confirmDataSourceSelection() {
        if (this.selectedDataSource) {
            console.log('确认选择数据源:', this.selectedDataSource.task_name);
            this.closeDataSourceModal();
            this.showSelectedDataSource();
        } else {
            this.showToast('error', '请选择数据源', '请先选择一个数据源');
        }
    }

    // 加载弹窗数据源列表
    async loadModalDataSources() {
        try {
            const response = await fetch('/api/get-monitor-data-for-dl/', {
                headers: {
                    'X-CSRFToken': this.getCookie('csrftoken')
                }
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.modalDataSources = data.data_list;
                this.modalFilteredDataSources = [...this.modalDataSources];
                this.modalCurrentPage = 1;
                this.renderModalDataSources();
            } else {
                this.showToast('error', '加载失败', data.message);
            }
        } catch (error) {
            console.error('加载弹窗数据源失败:', error);
            this.showToast('error', '加载失败', '网络请求失败');
        }
    }

    // 渲染弹窗数据源列表
    renderModalDataSources() {
        const container = document.getElementById('modalDataSourceList');
        if (!container) return;

        if (!this.modalFilteredDataSources || this.modalFilteredDataSources.length === 0) {
            container.innerHTML = `
                <div class="text-center py-8 text-gray-500">
                    <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                    </svg>
                    <p class="mt-2 text-sm">暂无可用数据源</p>
                    <p class="text-xs text-gray-400">请先在监控模块中创建数据采集任务</p>
                </div>
            `;
            return;
        }

        // 计算分页
        const itemsPerPage = 5;
        const startIndex = (this.modalCurrentPage - 1) * itemsPerPage;
        const endIndex = startIndex + itemsPerPage;
        const pageData = this.modalFilteredDataSources.slice(startIndex, endIndex);

        container.innerHTML = pageData.map(item => `
            <div class="data-source-item bg-white border border-gray-200 rounded-lg p-4 hover:border-blue-300 hover:shadow-md transition-all duration-200 cursor-pointer" data-task-id="${item.task_id}">
                <div class="flex items-start space-x-3">
                    <div class="flex-shrink-0">
                        <input type="radio" name="modalDataSource" value="${item.task_id}" class="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300">
                    </div>
                    <div class="flex-1 min-w-0">
                        <div class="flex items-center justify-between">
                            <div class="flex-1">
                                <div class="data-source-name font-medium text-gray-900 text-sm">${item.task_name}</div>
                                <div class="data-source-desc text-gray-600 text-xs mt-1">${item.task_description || '无描述'}</div>
                            </div>
                            <div class="ml-4 flex-shrink-0">
                                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                                    ${item.file_size_mb} MB
                                </span>
                            </div>
                        </div>
                        <div class="mt-2 flex items-center text-xs text-gray-500 space-x-4">
                            <span class="flex items-center">
                                <svg class="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clip-rule="evenodd"></path>
                                </svg>
                                ${new Date(item.created_at).toLocaleDateString()}
                            </span>
                            <span class="flex items-center">
                                <svg class="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                                    <path fill-rule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zM3 10a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zM14 9a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 001-1v-6a1 1 0 00-1-1h-2z" clip-rule="evenodd"></path>
                                </svg>
                                ${item.total_data_points.toLocaleString()} 点
                            </span>
                            <span class="flex items-center">
                                <svg class="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                                    <path fill-rule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zM3 10a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zM14 9a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 001-1v-6a1 1 0 00-1-1h-2z" clip-rule="evenodd"></path>
                                </svg>
                                ${item.enabled_channels.length} 通道
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');

        // 绑定单选事件
        container.querySelectorAll('input[name="modalDataSource"]').forEach(radio => {
            radio.addEventListener('change', (e) => {
                this.selectModalDataSource(e.target.value);
            });
        });

        // 绑定点击事件
        container.querySelectorAll('.data-source-item').forEach(item => {
            item.addEventListener('click', (e) => {
                if (e.target.type !== 'radio') {
                    const radio = item.querySelector('input[type="radio"]');
                    radio.checked = true;
                    this.selectModalDataSource(radio.value);
                }
            });
        });

        // 更新弹窗分页
        this.updateModalPagination();
    }

    // 选择弹窗数据源
    selectModalDataSource(taskId) {
        const selectedItem = this.modalFilteredDataSources.find(item => item.task_id === taskId);
        if (selectedItem) {
            this.selectedDataSource = selectedItem;
            console.log('弹窗中选择数据源:', selectedItem.task_name);
            // 立即更新确认按钮状态
            this.updateModalPagination();
        }
    }

    // 搜索弹窗数据源
    searchModalDataSources(searchTerm) {
        const searchLower = searchTerm.toLowerCase();
        
        this.modalFilteredDataSources = this.modalDataSources.filter(item => {
            const name = item.task_name.toLowerCase();
            const description = (item.task_description || '').toLowerCase();
            return name.includes(searchLower) || description.includes(searchLower);
        });
        
        this.modalCurrentPage = 1;
        // 搜索后清除之前的选择
        this.selectedDataSource = null;
        this.renderModalDataSources();
    }

    // 弹窗分页方法
    modalPrevPage() {
        if (this.modalCurrentPage > 1) {
            this.modalCurrentPage--;
            this.renderModalDataSources();
        }
    }

    modalNextPage() {
        const totalPages = Math.ceil(this.modalFilteredDataSources.length / 5);
        if (this.modalCurrentPage < totalPages) {
            this.modalCurrentPage++;
            this.renderModalDataSources();
        }
    }

    // 更新弹窗分页
    updateModalPagination() {
        const totalItems = this.modalFilteredDataSources.length;
        const totalPages = Math.ceil(totalItems / 5);
        const startItem = (this.modalCurrentPage - 1) * 5 + 1;
        const endItem = Math.min(this.modalCurrentPage * 5, totalItems);
        
        // 更新信息
        const modalCurrentPageInfo = document.getElementById('modalCurrentPageInfo');
        const modalTotalItems = document.getElementById('modalTotalItems');
        const modalPrevPageBtn = document.getElementById('modalPrevPage');
        const modalNextPageBtn = document.getElementById('modalNextPage');
        
        if (modalCurrentPageInfo) modalCurrentPageInfo.textContent = `${startItem}-${endItem}`;
        if (modalTotalItems) modalTotalItems.textContent = totalItems;
        if (modalPrevPageBtn) modalPrevPageBtn.disabled = this.modalCurrentPage <= 1;
        if (modalNextPageBtn) modalNextPageBtn.disabled = this.modalCurrentPage >= totalPages;
        
        // 更新选择状态
        const selectionStatus = document.getElementById('selectionStatus');
        const confirmSelectionBtn = document.getElementById('confirmSelection');
        
        if (this.selectedDataSource) {
            if (selectionStatus) selectionStatus.textContent = `已选择: ${this.selectedDataSource.task_name}`;
            if (confirmSelectionBtn) confirmSelectionBtn.disabled = false;
        } else {
            if (selectionStatus) selectionStatus.textContent = '请选择一个数据源';
            if (confirmSelectionBtn) confirmSelectionBtn.disabled = true;
        }
    }

    // ==================== 数据源管理功能 ====================
    
    /**
     * 初始化数据源管理功能
     */
    initDataSourceManagement() {
        // 绑定查看数据源按钮事件
        this.addEventListenerSafely('viewDataSourcesBtn', 'click', () => this.openDataSourceManagementModal());
        
        // 绑定数据源管理模态框事件
        this.addEventListenerSafely('closeManagementModal', 'click', () => this.closeDataSourceManagementModal());
        this.addEventListenerSafely('closeManagementBtn', 'click', () => this.closeDataSourceManagementModal());
        this.addEventListenerSafely('managementSearch', 'input', (e) => this.searchManagementDataSources(e.target.value));
        this.addEventListenerSafely('managementPrevPage', 'click', () => this.managementPrevPage());
        this.addEventListenerSafely('managementNextPage', 'click', () => this.managementNextPage());
        
        // 绑定删除确认模态框事件
        this.addEventListenerSafely('cancelDelete', 'click', () => this.closeDeleteConfirmModal());
        this.addEventListenerSafely('confirmDelete', 'click', () => this.performDeleteDataSource());
    }

    /**
     * 打开数据源管理模态框
     */
    openDataSourceManagementModal() {
        document.getElementById('dataSourceManagementModal').classList.remove('hidden');
        this.loadManagementDataSources();
    }

    /**
     * 关闭数据源管理模态框
     */
    closeDataSourceManagementModal() {
        document.getElementById('dataSourceManagementModal').classList.add('hidden');
        // 清空搜索框
        document.getElementById('managementSearch').value = '';
    }

    /**
     * 加载管理数据源列表
     */
    async loadManagementDataSources() {
        try {
            const response = await fetch('/api/get-data-sources/', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCookie('csrftoken')
                }
            });

            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    this.managementDataSources = data.data_sources;
                    this.managementFilteredDataSources = [...this.managementDataSources];
                    this.managementCurrentPage = 1;
                    this.renderManagementDataSources();
                    this.updateManagementPagination();
                } else {
                    this.showToast('error', '加载失败', data.message || '加载数据源失败');
                }
            } else {
                this.showToast('error', '加载失败', '网络请求失败');
            }
        } catch (error) {
            console.error('加载数据源失败:', error);
            this.showToast('error', '加载失败', '网络请求失败');
        }
    }

    /**
     * 渲染管理数据源列表
     */
    renderManagementDataSources() {
        const container = document.getElementById('managementDataSourceList');
        
        if (!container) {
            console.debug('managementDataSourceList 元素未找到');
            return;
        }
        
        if (!this.managementFilteredDataSources || this.managementFilteredDataSources.length === 0) {
            container.innerHTML = `
                <div class="text-center py-8 text-gray-500">
                    <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                    </svg>
                    <p class="mt-2 text-sm">暂无数据源</p>
                    <p class="text-xs text-gray-400">请先在监控模块中创建数据采集任务</p>
                </div>
            `;
            this.updateManagementPagination();
            return;
        }

        // 计算分页
        const startIndex = (this.managementCurrentPage - 1) * 10; // 每页显示10个
        const endIndex = startIndex + 10;
        const pageData = this.managementFilteredDataSources.slice(startIndex, endIndex);
        
        container.innerHTML = pageData.map(item => `
            <div class="data-source-management-item bg-white border border-gray-200 rounded-lg p-3 hover:border-blue-300 hover:shadow-sm transition-all duration-200 ${item.is_deleted ? 'opacity-50' : ''}" data-task-id="${item.task_id}">
                <div class="flex items-center justify-between">
                    <div class="flex-1 min-w-0">
                        <div class="flex items-center justify-between mb-1">
                            <div class="flex-1">
                                <div class="data-source-name font-medium text-gray-900 text-sm flex items-center gap-2">
                                    ${item.task_name}
                                    ${item.is_deleted ? '<span class="inline-flex items-center px-1.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">已删除</span>' : ''}
                                </div>
                                <div class="data-source-desc text-gray-600 text-xs mt-0.5">${item.task_description || '无描述'}</div>
                            </div>
                            <div class="ml-3 flex-shrink-0">
                                <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                                    ${item.file_size_mb} MB
                                </span>
                            </div>
                        </div>
                        <div class="flex items-center text-xs text-gray-500 space-x-3">
                            <span class="flex items-center">
                                <svg class="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clip-rule="evenodd"></path>
                                </svg>
                                ${new Date(item.created_at).toLocaleDateString()}
                            </span>
                            <span class="flex items-center">
                                <svg class="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                                    <path fill-rule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zM3 10a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zM14 9a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 001-1v-6a1 1 0 00-1-1h-2z" clip-rule="evenodd"></path>
                                </svg>
                                ${item.enabled_channels ? item.enabled_channels.length : 0} 通道
                            </span>
                            <span class="flex items-center">
                                <svg class="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                                    <path fill-rule="evenodd" d="M3 10a1 1 0 011-1h12a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6z" clip-rule="evenodd"></path>
                                </svg>
                                ${item.total_data_points ? item.total_data_points.toLocaleString() : 0} 数据点
                            </span>
                            <span>用户: ${item.user_name || '未知'}</span>
                            <span>•</span>
                            <span>${item.sample_rate || 0} Hz</span>
                        </div>
                    </div>
                    <div class="ml-3 flex-shrink-0">
                        ${!item.is_deleted ? `
                            <button class="delete-data-source-btn px-2 py-1 text-xs bg-red-100 text-red-700 rounded hover:bg-red-200 transition-colors" data-task-id="${item.task_id}" data-task-name="${item.task_name}">
                                删除
                            </button>
                        ` : ''}
                    </div>
                </div>
            </div>
        `).join('');

        // 绑定删除按钮事件
        container.querySelectorAll('.delete-data-source-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const taskId = btn.getAttribute('data-task-id');
                const taskName = btn.getAttribute('data-task-name');
                this.showDeleteConfirmModal(taskId, taskName);
            });
        });

        this.updateManagementPagination();
    }

    /**
     * 搜索管理数据源
     */
    searchManagementDataSources(searchTerm) {
        const searchLower = searchTerm.toLowerCase();
        
        // 过滤数据源
        this.managementFilteredDataSources = this.managementDataSources.filter(item => {
            const name = item.task_name.toLowerCase();
            const description = (item.task_description || '').toLowerCase();
            return name.includes(searchLower) || description.includes(searchLower);
        });
        
        // 重置到第一页
        this.managementCurrentPage = 1;
        
        // 重新渲染
        this.renderManagementDataSources();
    }

    /**
     * 管理分页功能
     */
    managementPrevPage() {
        if (this.managementCurrentPage > 1) {
            this.managementCurrentPage--;
            this.renderManagementDataSources();
        }
    }

    managementNextPage() {
        const totalPages = Math.ceil(this.managementFilteredDataSources.length / 10);
        if (this.managementCurrentPage < totalPages) {
            this.managementCurrentPage++;
            this.renderManagementDataSources();
        }
    }

    /**
     * 更新管理分页控件
     */
    updateManagementPagination() {
        const totalPages = Math.ceil(this.managementFilteredDataSources.length / 10);
        const startIndex = (this.managementCurrentPage - 1) * 10;
        const endIndex = startIndex + 10;
        
        // 安全地更新页码信息
        const currentPageInfo = document.getElementById('managementCurrentPageInfo');
        const totalItems = document.getElementById('managementTotalItems');
        const totalCount = document.getElementById('managementTotalCount');
        
        if (currentPageInfo) {
            currentPageInfo.textContent = `${startIndex + 1}-${Math.min(endIndex, this.managementFilteredDataSources.length)}`;
        }
        if (totalItems) {
            totalItems.textContent = this.managementFilteredDataSources.length;
        }
        if (totalCount) {
            totalCount.textContent = this.managementFilteredDataSources.length;
        }
        
        // 安全地更新分页按钮状态
        const prevPage = document.getElementById('managementPrevPage');
        const nextPage = document.getElementById('managementNextPage');
        
        if (prevPage) {
            prevPage.disabled = this.managementCurrentPage <= 1;
        }
        if (nextPage) {
            nextPage.disabled = this.managementCurrentPage >= totalPages;
        }
        
        // 安全地生成页码按钮
        const pageNumbersContainer = document.getElementById('managementPageNumbers');
        if (pageNumbersContainer) {
            pageNumbersContainer.innerHTML = '';
            
            const maxVisiblePages = 5;
            let startPage = Math.max(1, this.managementCurrentPage - Math.floor(maxVisiblePages / 2));
            let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);
            
            if (endPage - startPage + 1 < maxVisiblePages) {
                startPage = Math.max(1, endPage - maxVisiblePages + 1);
            }
            
            for (let i = startPage; i <= endPage; i++) {
                const pageButton = document.createElement('button');
                pageButton.className = `px-3 py-1 text-sm border rounded-md ${i === this.managementCurrentPage ? 'bg-blue-500 text-white border-blue-500' : 'border-gray-300 hover:bg-gray-50'}`;
                pageButton.textContent = i;
                pageButton.addEventListener('click', () => this.managementGoToPage(i));
                pageNumbersContainer.appendChild(pageButton);
            }
        }
    }

    managementGoToPage(page) {
        this.managementCurrentPage = page;
        this.renderManagementDataSources();
    }

    /**
     * 显示删除确认模态框
     */
    showDeleteConfirmModal(taskId, taskName) {
        document.getElementById('deleteConfirmName').textContent = taskName;
        document.getElementById('deleteConfirmModal').classList.remove('hidden');
        this.deleteTaskId = taskId;
    }

    /**
     * 关闭删除确认模态框
     */
    closeDeleteConfirmModal() {
        document.getElementById('deleteConfirmModal').classList.add('hidden');
        this.deleteTaskId = null;
    }

    /**
     * 执行删除数据源
     */
    async performDeleteDataSource() {
        if (!this.deleteTaskId) {
            this.closeDeleteConfirmModal();
            return;
        }

        try {
            const response = await fetch(`/api/delete-data-source/${this.deleteTaskId}/`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCookie('csrftoken')
                }
            });

            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    this.showToast('success', '删除成功', data.message);
                    this.closeDeleteConfirmModal();
                    // 重新加载数据源列表
                    this.loadManagementDataSources();
                } else {
                    this.showToast('error', '删除失败', data.message);
                }
            } else {
                this.showToast('error', '删除失败', '网络请求失败');
            }
        } catch (error) {
            console.error('删除数据源失败:', error);
            this.showToast('error', '删除失败', '网络请求失败');
        }
    }
}

// 页面加载完成后初始化深度学习模块
document.addEventListener('DOMContentLoaded', function() {
    window.deepLearningModule = new DeepLearningModule();
    // 初始化数据源管理功能
    window.deepLearningModule.initDataSourceManagement();
});