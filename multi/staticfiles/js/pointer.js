// 指针识别模块 JavaScript
// 文件名: pointer.js
// 功能: 相机控制、数据采集、参数设置等

document.addEventListener('DOMContentLoaded', function() {
    // 初始化图标
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
    
    // 全局变量
    let isCameraEnabled = false;
    let isCollecting = false;
    let collectionInterval = null;
    let collectedCount = 0;
    
    // 获取DOM元素
    const cameraToggle = document.getElementById('cameraToggle');
    const cameraStatus = document.getElementById('cameraStatus');
    const cameraDisplay = document.getElementById('cameraDisplay');
    const cameraSelect = document.getElementById('cameraSelect');
    const refreshCamerasBtn = document.getElementById('refreshCameras');
    
    // 检查必要元素是否存在
    if (!cameraToggle || !cameraStatus || !cameraDisplay || !cameraSelect || !refreshCamerasBtn) {
        console.error('必要的DOM元素未找到');
        return;
    }
    
    // 页面加载时检测可用相机
    loadAvailableCameras();
    
    // 事件监听器
    cameraToggle.addEventListener('click', function() {
        if (!isCameraEnabled) {
            enableCamera();
        } else {
            disableCamera();
        }
    });

    refreshCamerasBtn.addEventListener('click', function() {
        // 设置强制刷新标志
        localStorage.setItem('forceCameraRefresh', 'true');
        loadAvailableCameras();
    });
    
    // 相机列表加载函数
    function loadAvailableCameras() {
        // 检查是否需要强制刷新
        const forceRefresh = localStorage.getItem('forceCameraRefresh') === 'true';
        const timestamp = new Date().getTime();
        const url = `/api/camera/available/?t=${timestamp}${forceRefresh ? '&force_refresh=true' : ''}`;
        console.log('正在请求相机列表:', url);
        
        fetch(url)
        .then(response => {
            console.log('相机列表响应状态:', response.status);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('相机列表数据:', data);
            if (data.success) {
                updateCameraSelect(data.cameras);
                // 清除强制刷新标志
                if (forceRefresh) {
                    localStorage.removeItem('forceCameraRefresh');
                }
            } else {
                console.error('获取相机列表失败:', data.message);
                cameraSelect.innerHTML = '<option value="">无可用相机</option>';
            }
        })
        .catch(error => {
            console.error('检测相机时出错:', error);
            cameraSelect.innerHTML = '<option value="">检测失败</option>';
        });
    }
    
    // 更新相机选择下拉框
    function updateCameraSelect(cameras) {
        cameraSelect.innerHTML = '';
        
        if (cameras.length === 0) {
            cameraSelect.innerHTML = '<option value="">无可用相机</option>';
            return;
        }
        
        cameras.forEach(camera => {
            const option = document.createElement('option');
            option.value = camera.id;
            option.textContent = camera.name;
            if (camera.is_default) {
                option.selected = true;
            }
            cameraSelect.appendChild(option);
        });
    }
    
    // 启用相机
    function enableCamera() {
        const selectedCameraIndex = cameraSelect.value;
        if (!selectedCameraIndex) {
            alert('请先选择一个相机');
            return;
        }
        
        const url = '/api/camera/enable/';
        console.log('正在启用相机:', url);
        
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                camera_index: parseInt(selectedCameraIndex)
            })
        })
        .then(response => {
            console.log('启用相机响应状态:', response.status);
            return response.json();
        })
        .then(data => {
            console.log('启用相机响应数据:', data);
            if (data.success) {
                isCameraEnabled = true;
                cameraStatus.textContent = `已连接 (相机${data.camera_index})`;
                cameraStatus.className = 'px-3 py-1 text-sm font-medium rounded-full bg-green-100 text-green-800';
                cameraToggle.innerHTML = '<i data-lucide="camera-off" class="w-4 h-4"></i><span>禁用相机</span>';
                if (typeof lucide !== 'undefined') {
                    lucide.createIcons();
                }
                startCameraStream();
            } else {
                alert('启用相机失败: ' + data.message);
            }
        })
        .catch(error => {
            console.error('启用相机时出错:', error);
            alert('启用相机时出错，请检查相机连接');
        });
    }
    
    // 禁用相机
    function disableCamera() {
        const url = '/api/camera/disable/';
        console.log('正在禁用相机:', url);
        
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => {
            console.log('禁用相机响应状态:', response.status);
            return response.json();
        })
        .then(data => {
            console.log('禁用相机响应数据:', data);
            if (data.success) {
                isCameraEnabled = false;
                cameraStatus.textContent = '未连接';
                cameraStatus.className = 'px-3 py-1 text-sm font-medium rounded-full bg-yellow-100 text-yellow-800';
                cameraToggle.innerHTML = '<i data-lucide="camera" class="w-4 h-4"></i><span>启用相机</span>';
                if (typeof lucide !== 'undefined') {
                    lucide.createIcons();
                }
                stopCameraStream();
            }
        })
        .catch(error => {
            console.error('禁用相机时出错:', error);
        });
    }
    
    // 开始相机流
    function startCameraStream() {
        console.log('开始相机流更新');
        // 获取帧数设置，默认为10FPS (100ms)
        const frameRate = parseInt(localStorage.getItem('cameraFrameRate')) || 10;
        const interval = 1000 / frameRate; // 转换为毫秒
        
        console.log(`相机帧数设置为: ${frameRate}FPS (${interval}ms间隔)`);
        
        // 相机流更新
        setInterval(() => {
            if (isCameraEnabled) {
                updateCameraDisplay();
            }
        }, interval);
    }
    
    // 停止相机流
    function stopCameraStream() {
        console.log('停止相机流更新');
        cameraDisplay.innerHTML = `
            <div class="text-center text-gray-400">
                <i data-lucide="camera-off" class="w-16 h-16 mx-auto mb-4"></i>
                <p>相机未启用</p>
            </div>
        `;
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    }
    
    // 更新相机显示
    function updateCameraDisplay() {
        const url = `/api/camera/status/`;
        console.log('正在更新相机显示:', url);
        
        fetch(url)
        .then(response => {
            console.log('相机状态响应状态:', response.status);
            return response.json();
        })
        .then(data => {
            console.log('相机状态数据:', data);
            if (data.enabled && data.status === '正常') {
                // 显示实时图像
                if (data.image_url) {
                    // 获取实时图像
                    fetch(data.image_url)
                    .then(response => response.json())
                    .then(imageData => {
                        if (imageData.success) {
                            cameraDisplay.innerHTML = `
                                <img src="${imageData.image}" alt="实时相机画面" 
                                     class="w-full h-full object-contain rounded-lg">
                            `;
                        } else {
                            // 如果获取图像失败，显示状态信息
                            cameraDisplay.innerHTML = `
                                <div class="text-center text-gray-400">
                                    <i data-lucide="camera" class="w-16 h-16 mx-auto mb-4"></i>
                                    <p>相机运行中 (实时显示)</p>
                                    <p class="text-xs mt-2">角度: ${data.angle || '--'}° | 读数: ${data.reading || '--'}</p>
                                </div>
                            `;
                        }
                        if (typeof lucide !== 'undefined') {
                            lucide.createIcons();
                        }
                    })
                    .catch(error => {
                        console.error('获取图像失败:', error);
                        // 显示状态信息作为备选
                        cameraDisplay.innerHTML = `
                            <div class="text-center text-gray-400">
                                <i data-lucide="camera" class="w-16 h-16 mx-auto mb-4"></i>
                                <p>相机运行中 (实时显示)</p>
                                <p class="text-xs mt-2">角度: ${data.angle || '--'}° | 读数: ${data.reading || '--'}</p>
                            </div>
                        `;
                        if (typeof lucide !== 'undefined') {
                            lucide.createIcons();
                        }
                    });
                } else {
                    // 没有图像URL时显示状态信息
                    cameraDisplay.innerHTML = `
                        <div class="text-center text-gray-400">
                            <i data-lucide="camera" class="w-16 h-16 mx-auto mb-4"></i>
                            <p>相机运行中 (实时显示)</p>
                            <p class="text-xs mt-2">角度: ${data.angle || '--'}° | 读数: ${data.reading || '--'}</p>
                        </div>
                    `;
                    if (typeof lucide !== 'undefined') {
                        lucide.createIcons();
                    }
                }
                updateProcessingResult(data);
            } else if (data.enabled && data.status === '等待模板') {
                // 显示实时图像（即使没有模板）
                if (data.image_url) {
                    fetch(data.image_url)
                    .then(response => response.json())
                    .then(imageData => {
                        if (imageData.success) {
                            cameraDisplay.innerHTML = `
                                <img src="${imageData.image}" alt="实时相机画面" 
                                     class="w-full h-full object-contain rounded-lg">
                                <div class="absolute top-4 left-4 bg-yellow-500 bg-opacity-75 text-white p-2 rounded-lg text-sm">
                                    等待模板加载
                                </div>
                            `;
                        } else {
                            cameraDisplay.innerHTML = `
                                <div class="text-center text-gray-400">
                                    <i data-lucide="camera" class="w-16 h-16 mx-auto mb-4"></i>
                                    <p>相机运行中 (等待模板)</p>
                                    <p class="text-xs mt-2">请加载模板图像</p>
                                </div>
                            `;
                        }
                        if (typeof lucide !== 'undefined') {
                            lucide.createIcons();
                        }
                    })
                    .catch(error => {
                        console.error('获取图像失败:', error);
                        cameraDisplay.innerHTML = `
                            <div class="text-center text-gray-400">
                                <i data-lucide="camera" class="w-16 h-16 mx-auto mb-4"></i>
                                <p>相机运行中 (等待模板)</p>
                                <p class="text-xs mt-2">请加载模板图像</p>
                            </div>
                        `;
                        if (typeof lucide !== 'undefined') {
                            lucide.createIcons();
                        }
                    });
                } else {
                    cameraDisplay.innerHTML = `
                        <div class="text-center text-gray-400">
                            <i data-lucide="camera" class="w-16 h-16 mx-auto mb-4"></i>
                            <p>相机运行中 (等待模板)</p>
                            <p class="text-xs mt-2">请加载模板图像</p>
                        </div>
                    `;
                    if (typeof lucide !== 'undefined') {
                        lucide.createIcons();
                    }
                }
            } else if (data.enabled) {
                // 其他状态（如读取失败、处理错误等）
                if (data.image_url) {
                    fetch(data.image_url)
                    .then(response => response.json())
                    .then(imageData => {
                        if (imageData.success) {
                            cameraDisplay.innerHTML = `
                                <img src="${imageData.image}" alt="实时相机画面" 
                                     class="w-full h-full object-contain rounded-lg">
                                <div class="absolute top-4 left-4 bg-red-500 bg-opacity-75 text-white p-2 rounded-lg text-sm">
                                    ${data.status}
                                </div>
                            `;
                        } else {
                            cameraDisplay.innerHTML = `
                                <div class="text-center text-gray-400">
                                    <i data-lucide="camera" class="w-16 h-16 mx-auto mb-4"></i>
                                    <p>相机运行中</p>
                                    <p class="text-xs mt-2 text-red-400">${data.status}</p>
                                </div>
                            `;
                        }
                        if (typeof lucide !== 'undefined') {
                            lucide.createIcons();
                        }
                    })
                    .catch(error => {
                        console.error('获取图像失败:', error);
                        cameraDisplay.innerHTML = `
                            <div class="text-center text-gray-400">
                                <i data-lucide="camera" class="w-16 h-16 mx-auto mb-4"></i>
                                <p>相机运行中</p>
                                <p class="text-xs mt-2 text-red-400">${data.status}</p>
                            </div>
                        `;
                        if (typeof lucide !== 'undefined') {
                            lucide.createIcons();
                        }
                    });
                } else {
                    cameraDisplay.innerHTML = `
                        <div class="text-center text-gray-400">
                            <i data-lucide="camera" class="w-16 h-16 mx-auto mb-4"></i>
                            <p>相机运行中</p>
                            <p class="text-xs mt-2 text-red-400">${data.status}</p>
                        </div>
                    `;
                    if (typeof lucide !== 'undefined') {
                        lucide.createIcons();
                    }
                }
            }
        })
        .catch(error => {
            console.error('更新相机显示时出错:', error);
        });
    }
    
    // 更新处理结果
    function updateProcessingResult(data) {
        const processingResult = document.getElementById('processingResult');
        const angleValue = document.getElementById('angleValue');
        const readingValue = document.getElementById('readingValue');
        
        if (data.angle !== null && data.reading !== null) {
            angleValue.textContent = data.angle.toFixed(1);
            readingValue.textContent = data.reading.toFixed(2);
            processingResult.classList.remove('hidden');
        }
    }
    
    // 高级设置模态框
    const advancedSettingsBtn = document.getElementById('advancedSettings');
    const advancedSettingsModal = document.getElementById('advancedSettingsModal');
    const closeAdvancedSettings = document.getElementById('closeAdvancedSettings');
    
    if (advancedSettingsBtn && advancedSettingsModal && closeAdvancedSettings) {
        advancedSettingsBtn.addEventListener('click', function() {
            advancedSettingsModal.classList.remove('hidden');
        });
        
        closeAdvancedSettings.addEventListener('click', function() {
            advancedSettingsModal.classList.add('hidden');
        });
        
        // 点击模态框外部关闭
        advancedSettingsModal.addEventListener('click', function(e) {
            if (e.target === advancedSettingsModal) {
                advancedSettingsModal.classList.add('hidden');
            }
        });
    }
    
    // 数据采集控制
    const startCollectionBtn = document.getElementById('startCollection');
    const stopCollectionBtn = document.getElementById('stopCollection');
    const collectionStatus = document.getElementById('collectionStatus');
    const collectedCountElement = document.getElementById('collectedCount');
    const processingTimeElement = document.getElementById('processingTime');
    
    if (startCollectionBtn) {
        startCollectionBtn.addEventListener('click', function() {
            const samplingPoints = document.getElementById('samplingPoints').value;
            const samplingInterval = document.getElementById('samplingInterval').value;
            const saveAnnotatedImages = document.getElementById('saveAnnotatedImages').checked;
            const saveData = document.getElementById('saveData').checked;
            
            const url = '/api/camera/start_collection/';
            console.log('正在开始数据采集:', url);
            
            fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    sampling_points: samplingPoints,
                    sampling_interval: samplingInterval,
                    save_annotated_images: saveAnnotatedImages,
                    save_data: saveData
                })
            })
            .then(response => {
                console.log('开始采集响应状态:', response.status);
                return response.json();
            })
            .then(data => {
                console.log('开始采集响应数据:', data);
                if (data.success) {
                    isCollecting = true;
                    startCollectionBtn.classList.add('hidden');
                    stopCollectionBtn.classList.remove('hidden');
                    collectionStatus.textContent = '采集中';
                    startDataCollection();
                }
            })
            .catch(error => {
                console.error('开始采集时出错:', error);
            });
        });
    }
    
    if (stopCollectionBtn) {
        stopCollectionBtn.addEventListener('click', function() {
            const url = '/api/camera/stop_collection/';
            console.log('正在停止数据采集:', url);
            
            fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(response => {
                console.log('停止采集响应状态:', response.status);
                return response.json();
            })
            .then(data => {
                console.log('停止采集响应数据:', data);
                if (data.success) {
                    isCollecting = false;
                    stopCollectionBtn.classList.add('hidden');
                    startCollectionBtn.classList.remove('hidden');
                    collectionStatus.textContent = '已停止';
                    stopDataCollection();
                }
            })
            .catch(error => {
                console.error('停止采集时出错:', error);
            });
        });
    }
    
    // 开始数据采集
    function startDataCollection() {
        const interval = document.getElementById('samplingInterval').value * 1000;
        collectionInterval = setInterval(() => {
            if (isCollecting) {
                collectData();
            }
        }, interval);
    }
    
    // 停止数据采集
    function stopDataCollection() {
        if (collectionInterval) {
            clearInterval(collectionInterval);
            collectionInterval = null;
        }
    }
    
    // 采集数据
    function collectData() {
        const startTime = performance.now();
        const url = '/api/camera/collect_data/';
        console.log('正在采集数据:', url);
        
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => {
            console.log('采集数据响应状态:', response.status);
            return response.json();
        })
        .then(data => {
            console.log('采集数据响应数据:', data);
            if (data.success) {
                collectedCount++;
                collectedCountElement.textContent = collectedCount;
                
                const endTime = performance.now();
                const processingTime = (endTime - startTime).toFixed(1);
                processingTimeElement.textContent = processingTime + 'ms';
                
                // 检查是否达到采样点数
                const samplingPoints = document.getElementById('samplingPoints').value;
                if (collectedCount >= parseInt(samplingPoints)) {
                    stopCollectionBtn.click();
                }
            }
        })
        .catch(error => {
            console.error('采集数据时出错:', error);
        });
    }
    
    // 参数更新
    const updateImageBtn = document.getElementById('updateImage');
    const saveSettingsBtn = document.getElementById('saveSettings');
    
    if (updateImageBtn) {
        updateImageBtn.addEventListener('click', function() {
            updateParameters();
        });
    }
    
    if (saveSettingsBtn) {
        saveSettingsBtn.addEventListener('click', function() {
            saveParameters();
            advancedSettingsModal.classList.add('hidden');
        });
    }
    
    // 更新参数
    function updateParameters() {
        const params = {
            gaussian_size: document.getElementById('gaussianSize').value,
            binarization_offset: document.getElementById('binarizationOffset').value,
            hough_threshold: document.getElementById('houghThreshold').value,
            min_line_length: document.getElementById('minLineLength').value,
            max_line_gap: document.getElementById('maxLineGap').value,
            max_range: document.getElementById('maxRange').value,
            angle_range: document.getElementById('angleRange').value,
            start_angle: document.getElementById('startAngle').value,
            show_binarization: document.getElementById('showBinarization').checked,
            show_all_lines: document.getElementById('showAllLines').checked,
            show_pointer_result: document.getElementById('showPointerResult').checked
        };
        
        const url = '/api/camera/update_parameters/';
        console.log('正在更新参数:', url, params);
        
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(params)
        })
        .then(response => {
            console.log('更新参数响应状态:', response.status);
            return response.json();
        })
        .then(data => {
            console.log('更新参数响应数据:', data);
            if (data.success) {
                console.log('参数更新成功');
            }
        })
        .catch(error => {
            console.error('更新参数时出错:', error);
        });
    }
    
    // 保存参数
    function saveParameters() {
        // 保存参数到本地存储或服务器
        const params = {
            gaussian_size: document.getElementById('gaussianSize').value,
            binarization_offset: document.getElementById('binarizationOffset').value,
            hough_threshold: document.getElementById('houghThreshold').value,
            min_line_length: document.getElementById('minLineLength').value,
            max_line_gap: document.getElementById('maxLineGap').value,
            max_range: document.getElementById('maxRange').value,
            angle_range: document.getElementById('angleRange').value,
            start_angle: document.getElementById('startAngle').value
        };
        
        localStorage.setItem('pointerParameters', JSON.stringify(params));
        console.log('参数已保存到本地存储');
    }
    
    // 加载保存的参数
    function loadSavedParameters() {
        const savedParams = localStorage.getItem('pointerParameters');
        if (savedParams) {
            const params = JSON.parse(savedParams);
            Object.keys(params).forEach(key => {
                const element = document.getElementById(key.replace('_', '') + (key.includes('_') ? key.split('_')[1].charAt(0).toUpperCase() + key.split('_')[1].slice(1) : ''));
                if (element) {
                    element.value = params[key];
                }
            });
        }
    }
    
    // 获取CSRF Token
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
    
    // 帧数控制
    const cameraFrameRateSelect = document.getElementById('cameraFrameRate');
    if (cameraFrameRateSelect) {
        // 加载保存的帧数设置
        const savedFrameRate = localStorage.getItem('cameraFrameRate');
        if (savedFrameRate) {
            cameraFrameRateSelect.value = savedFrameRate;
        }
        
        // 监听帧数变化
        cameraFrameRateSelect.addEventListener('change', function() {
            const newFrameRate = this.value;
            localStorage.setItem('cameraFrameRate', newFrameRate);
            console.log(`相机帧数已更新为: ${newFrameRate}FPS`);
            
            // 如果相机正在运行，提示用户重启相机以应用新设置
            if (isCameraEnabled) {
                alert('帧数设置已保存。请重新启用相机以应用新的帧数设置。');
            }
        });
    }
    
    // 实时显示模式说明
    console.log('相机运行在实时显示模式：仅显示实时数据，不保存图像文件');
    
    // 初始化
    loadSavedParameters();
    
    // 导出全局函数（如果需要）
    window.pointerModule = {
        loadAvailableCameras,
        enableCamera,
        disableCamera,
        updateParameters,
        saveParameters
    };
    
    console.log('指针识别模块初始化完成');
}); 