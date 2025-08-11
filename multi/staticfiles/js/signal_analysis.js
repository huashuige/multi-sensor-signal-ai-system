// 全局状态管理
class SignalAnalysisApp {
  constructor() {
    this.currentData = null
    this.isDataLoaded = false
    this.activeModule = ""
    this.charts = {}
    this.lucide = window.lucide // Declare lucide variable
    this.echarts = window.echarts // Declare echarts variable

    this.init()
  }

  init() {
    this.bindEvents()
    this.initializeIcons()
  }

  bindEvents() {
    // 文件选择事件
    document.getElementById("dataFile").addEventListener("change", this.handleFileSelect.bind(this))

    // 加载数据按钮
    document.getElementById("loadDataBtn").addEventListener("click", this.handleLoadData.bind(this))

    // 模块卡片点击事件
    document.querySelectorAll(".module-card").forEach((card) => {
      card.addEventListener("click", this.handleModuleClick.bind(this))
    })

    // 关闭模块按钮
    document.getElementById("closeModuleBtn").addEventListener("click", this.closeActiveModule.bind(this))

    // 窗口大小改变时重新调整图表
    window.addEventListener("resize", this.resizeCharts.bind(this))
  }

  initializeIcons() {
    if (this.lucide) {
      this.lucide.createIcons()
    }
  }

  handleFileSelect(event) {
    const file = event.target.files[0]
    if (file) {
      const fileInfo = document.getElementById("fileInfo")
      const fileInfoText = document.getElementById("fileInfoText")

      fileInfoText.textContent = `已选择: ${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB)`
      fileInfo.classList.remove("hidden")
    }
  }

  async handleLoadData() {
    const fileInput = document.getElementById("dataFile")
    const samplingRateInput = document.getElementById("samplingRate")

    if (!fileInput.files[0]) {
      alert("请先选择数据文件")
      return
    }

    this.showLoading(true)

    try {
      // 模拟数据加载过程
      await this.simulateDataLoading()

      // 创建模拟数据
      const mockData = {
        data_encoded: "mock_encoded_data",
        sampling_rate: Number.parseInt(samplingRateInput.value),
        data_dtype: "float64",
        time_domain_data: this.generateMockTimeData(Number.parseInt(samplingRateInput.value)),
        file_name: fileInput.files[0].name,
      }

      this.currentData = mockData
      this.isDataLoaded = true
      this.updateDataStatus()
      this.showDataOverview()

      // 🔧 修复：如果当前正在查看时域模块，立即刷新图表
      if (this.activeModule === "time-domain") {
        console.log("数据加载完成，刷新时域模块...")
        setTimeout(() => {
          this.initTimeDomainModule()
        }, 200)
      }
    } catch (error) {
      alert("数据加载失败: " + error.message)
    } finally {
      this.showLoading(false)
    }
  }

  async simulateDataLoading() {
    return new Promise((resolve) => setTimeout(resolve, 2000))
  }

  generateMockTimeData(samplingRate) {
    const dataLength = Math.min(samplingRate * 2, 10000) // 2秒数据或最多10000点
    const data = []

    for (let i = 0; i < dataLength; i++) {
      const time = i / samplingRate
      const value =
        Math.sin(2 * Math.PI * 50 * time) + 0.5 * Math.sin(2 * Math.PI * 120 * time) + 0.1 * (Math.random() - 0.5)
      data.push([time, value])
    }

    return data
  }

  handleModuleClick(event) {
    const card = event.currentTarget
    const moduleId = card.dataset.module

    if (!this.isDataLoaded) {
      alert("请先加载数据文件")
      return
    }

    // 更新卡片状态
    document.querySelectorAll(".module-card").forEach((c) => c.classList.remove("active"))
    card.classList.add("active")

    this.activeModule = moduleId
    this.showActiveModule(moduleId)
  }

  showActiveModule(moduleId) {
    const container = document.getElementById("activeModuleContainer")
    const title = document.getElementById("activeModuleTitle")
    const content = document.getElementById("activeModuleContent")

    const moduleInfo = this.getModuleInfo(moduleId)
    title.textContent = moduleInfo.title

    // 生成模块内容
    content.innerHTML = this.generateModuleContent(moduleId)

    container.classList.remove("hidden")
    container.classList.add("fade-in")

    // 滚动到模块区域
    container.scrollIntoView({ behavior: "smooth", block: "start" })

    // 🔧 修复：增加延迟确保DOM渲染完成
    setTimeout(() => {
      this.initializeModule(moduleId)
    }, 100)
  }

  getModuleInfo(moduleId) {
    const modules = {
      "time-domain": { title: "时域信号分析", icon: "activity", color: "blue" },
      "frequency-domain": { title: "频域信号分析", icon: "bar-chart-3", color: "green" },
      "time-average": { title: "时域平均模块", icon: "zap", color: "purple" },
      "advanced-transforms": { title: "高级分析变换", icon: "settings", color: "orange" },
    }
    return modules[moduleId]
  }

  generateModuleContent(moduleId) {
    switch (moduleId) {
      case "time-domain":
        return this.generateTimeDomainContent()
      case "frequency-domain":
        return this.generateFrequencyDomainContent()
      case "time-average":
        return this.generateTimeAverageContent()
      case "advanced-transforms":
        return this.generateAdvancedTransformsContent()
      default:
        return "<div>模块内容加载中...</div>"
    }
  }

  generateTimeDomainContent() {
    return `
            <div class="space-y-6">
                <div>
                    <h4 class="text-lg font-semibold mb-4 flex items-center">
                        <i data-lucide="activity" class="h-5 w-5 mr-2 text-blue-600"></i>
                        时域波形显示
                    </h4>
                    <div id="timeDomainChart" class="h-96 w-full border border-gray-200 rounded-lg"></div>
                </div>
                
                <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div class="bg-white border border-gray-200 rounded-lg p-4 text-center">
                        <div class="text-2xl font-bold text-blue-600">${this.currentData.time_domain_data.length}</div>
                        <div class="text-sm text-gray-600">数据点数</div>
                    </div>
                    <div class="bg-white border border-gray-200 rounded-lg p-4 text-center">
                        <div class="text-2xl font-bold text-green-600">${(this.currentData.time_domain_data.length / this.currentData.sampling_rate).toFixed(3)}</div>
                        <div class="text-sm text-gray-600">时长 (秒)</div>
                    </div>
                    <div class="bg-white border border-gray-200 rounded-lg p-4 text-center">
                        <div class="text-2xl font-bold text-purple-600">${this.currentData.sampling_rate.toLocaleString()}</div>
                        <div class="text-sm text-gray-600">采样率 (Hz)</div>
                    </div>
                    <div class="bg-white border border-gray-200 rounded-lg p-4 text-center">
                        <div class="text-2xl font-bold text-orange-600">${this.currentData.data_dtype}</div>
                        <div class="text-sm text-gray-600">数据类型</div>
                    </div>
                </div>
            </div>
        `
  }

  generateFrequencyDomainContent() {
    return `
            <div class="space-y-6">
                <div class="flex items-center justify-between">
                    <h4 class="text-lg font-semibold flex items-center">
                        <i data-lucide="bar-chart-3" class="h-5 w-5 mr-2 text-green-600"></i>
                        频域分析
                    </h4>
                    <button id="fftBtn" class="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg transition-colors duration-200 flex items-center">
                        <i data-lucide="zap" class="h-4 w-4 mr-2"></i>
                        执行FFT变换
                    </button>
                </div>
                
                <div id="frequencyDomainChart" class="h-96 w-full border border-gray-200 rounded-lg">
                    <div class="flex items-center justify-center h-full bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
                        <div class="text-center text-gray-500">
                            <i data-lucide="bar-chart-3" class="h-12 w-12 mx-auto mb-2 opacity-50"></i>
                            <div>点击"执行FFT变换"开始频域分析</div>
                        </div>
                    </div>
                </div>
                
                <div id="frequencyStats" class="hidden grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div class="bg-white border border-gray-200 rounded-lg p-4 text-center">
                        <div id="freqPointsCount" class="text-2xl font-bold text-green-600">0</div>
                        <div class="text-sm text-gray-600">频率点数</div>
                    </div>
                    <div class="bg-white border border-gray-200 rounded-lg p-4 text-center">
                        <div id="maxFrequency" class="text-2xl font-bold text-blue-600">0</div>
                        <div class="text-sm text-gray-600">最大频率 (Hz)</div>
                    </div>
                    <div class="bg-white border border-gray-200 rounded-lg p-4 text-center">
                        <div class="text-2xl font-bold text-purple-600">${(this.currentData.sampling_rate / 2).toLocaleString()}</div>
                        <div class="text-sm text-gray-600">奈奎斯特频率 (Hz)</div>
                    </div>
                </div>
            </div>
        `
  }

  generateTimeAverageContent() {
    return `
            <div class="space-y-6">
                <div class="flex items-center">
                    <i data-lucide="zap" class="h-5 w-5 mr-2 text-purple-600"></i>
                    <h4 class="text-lg font-semibold">时域平均处理</h4>
                </div>
                
                <div class="bg-white border border-gray-200 rounded-lg p-6">
                    <h5 class="text-base font-semibold mb-4 flex items-center">
                        <i data-lucide="settings" class="h-4 w-4 mr-2"></i>
                        处理参数
                    </h5>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div class="space-y-2">
                            <label for="averageCount" class="block text-sm font-medium text-gray-700">平均次数</label>
                            <input type="number" id="averageCount" value="10" min="1" max="100"
                                   class="block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-purple-500 focus:border-purple-500">
                        </div>
                        <div class="space-y-2">
                            <label for="windowSize" class="block text-sm font-medium text-gray-700">窗口大小</label>
                            <input type="number" id="windowSize" value="1024" min="64" max="8192" step="64"
                                   class="block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-purple-500 focus:border-purple-500">
                        </div>
                    </div>
                </div>
                
                <button id="timeAverageBtn" class="bg-purple-600 hover:bg-purple-700 text-white px-6 py-2 rounded-lg transition-colors duration-200 flex items-center">
                    <i data-lucide="play" class="h-4 w-4 mr-2"></i>
                    开始时域平均
                </button>
                
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div class="bg-white border border-gray-200 rounded-lg p-4 text-center">
                        <div class="text-2xl font-bold text-purple-600">10</div>
                        <div class="text-sm text-gray-600">平均次数</div>
                    </div>
                    <div class="bg-white border border-gray-200 rounded-lg p-4 text-center">
                        <div class="text-2xl font-bold text-blue-600">1024</div>
                        <div class="text-sm text-gray-600">窗口大小</div>
                    </div>
                    <div class="bg-white border border-gray-200 rounded-lg p-4 text-center">
                        <div class="text-2xl font-bold text-green-600">3.2x</div>
                        <div class="text-sm text-gray-600">信噪比提升</div>
                    </div>
                </div>
            </div>
        `
  }

  generateAdvancedTransformsContent() {
    return `
            <div class="space-y-6">
                <div class="flex items-center">
                    <i data-lucide="settings" class="h-5 w-5 mr-2 text-orange-600"></i>
                    <h4 class="text-lg font-semibold">高级变换分析</h4>
                </div>
                
                <!-- Transform Method Selection -->
                <div class="bg-white border border-gray-200 rounded-lg p-6">
                    <h5 class="text-base font-semibold mb-4">变换方法选择</h5>
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div class="border border-gray-200 rounded-lg p-4 cursor-pointer hover:border-blue-500 transition-colors transform-method" data-method="cep">
                            <div class="flex items-center mb-2">
                                <input type="radio" name="transformMethod" value="cep" id="cepMethod" class="mr-2">
                                <label for="cepMethod" class="font-medium text-gray-800 cursor-pointer">CEP变换</label>
                            </div>
                            <p class="text-sm text-gray-600 mb-2">倒谱编辑处理，支持时间区间剔除</p>
                            <div class="space-y-1">
                                <div class="text-xs text-blue-600 flex items-center">
                                    <div class="w-1 h-1 bg-blue-600 rounded-full mr-2"></div>
                                    高精度故障特征提取
                                </div>
                                <div class="text-xs text-blue-600 flex items-center">
                                    <div class="w-1 h-1 bg-blue-600 rounded-full mr-2"></div>
                                    时间域编辑
                                </div>
                            </div>
                        </div>
                        
                        <div class="border border-gray-200 rounded-lg p-4 cursor-pointer hover:border-blue-500 transition-colors transform-method" data-method="cpw">
                            <div class="flex items-center mb-2">
                                <input type="radio" name="transformMethod" value="cpw" id="cpwMethod" class="mr-2">
                                <label for="cpwMethod" class="font-medium text-gray-800 cursor-pointer">CPW变换</label>
                            </div>
                            <p class="text-sm text-gray-600 mb-2">倒谱预白化处理</p>
                            <div class="space-y-1">
                                <div class="text-xs text-blue-600 flex items-center">
                                    <div class="w-1 h-1 bg-blue-600 rounded-full mr-2"></div>
                                    谱线预白化技术
                                </div>
                                <div class="text-xs text-blue-600 flex items-center">
                                    <div class="w-1 h-1 bg-blue-600 rounded-full mr-2"></div>
                                    频域平滑
                                </div>
                            </div>
                        </div>
                        
                        <div class="border border-gray-200 rounded-lg p-4 cursor-pointer hover:border-blue-500 transition-colors transform-method" data-method="lcep">
                            <div class="flex items-center mb-2">
                                <input type="radio" name="transformMethod" value="lcep" id="lcepMethod" class="mr-2">
                                <label for="lcepMethod" class="font-medium text-gray-800 cursor-pointer">LCEP变换</label>
                            </div>
                            <p class="text-sm text-gray-600 mb-2">局部倒谱编辑处理</p>
                            <div class="space-y-1">
                                <div class="text-xs text-blue-600 flex items-center">
                                    <div class="w-1 h-1 bg-blue-600 rounded-full mr-2"></div>
                                    局部频段分析
                                </div>
                                <div class="text-xs text-blue-600 flex items-center">
                                    <div class="w-1 h-1 bg-blue-600 rounded-full mr-2"></div>
                                    带通滤波
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Display Range Settings -->
                <div class="bg-white border border-gray-200 rounded-lg p-6">
                    <h5 class="text-base font-semibold mb-4">显示范围设置</h5>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div class="space-y-2">
                            <label for="freqDisplayMin" class="block text-sm font-medium text-gray-700">频率显示下限 (Hz)</label>
                            <input type="number" id="freqDisplayMin" value="0" min="0"
                                   class="block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-orange-500 focus:border-orange-500">
                        </div>
                        <div class="space-y-2">
                            <label for="freqDisplayMax" class="block text-sm font-medium text-gray-700">频率显示上限 (Hz)</label>
                            <input type="number" id="freqDisplayMax" value="180" min="1"
                                   class="block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-orange-500 focus:border-orange-500">
                        </div>
                    </div>
                </div>
                
                <!-- Method-specific Parameters -->
                <div id="cepParams" class="hidden bg-gray-50 border border-gray-200 rounded-lg p-6">
                    <h5 class="text-base font-semibold mb-4">CEP 参数设置</h5>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div class="space-y-2">
                            <label for="cepTimeStart" class="block text-sm font-medium text-gray-700">剔除起始时间 (秒)</label>
                            <input type="number" id="cepTimeStart" value="0.01" min="0" step="0.001"
                                   class="block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-orange-500 focus:border-orange-500">
                        </div>
                        <div class="space-y-2">
                            <label for="cepTimeEnd" class="block text-sm font-medium text-gray-700">剔除结束时间 (秒)</label>
                            <input type="number" id="cepTimeEnd" value="0.05" min="0" step="0.001"
                                   class="block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-orange-500 focus:border-orange-500">
                        </div>
                    </div>
                </div>
                
                <div id="lcepParams" class="hidden bg-gray-50 border border-gray-200 rounded-lg p-6">
                    <h5 class="text-base font-semibold mb-4">LCEP 参数设置</h5>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div class="space-y-2">
                            <label for="freqLow" class="block text-sm font-medium text-gray-700">频带下限 (Hz)</label>
                            <input type="number" id="freqLow" value="10" min="0"
                                   class="block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-orange-500 focus:border-orange-500">
                        </div>
                        <div class="space-y-2">
                            <label for="freqHigh" class="block text-sm font-medium text-gray-700">频带上限 (Hz)</label>
                            <input type="number" id="freqHigh" value="1000" min="1"
                                   class="block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-orange-500 focus:border-orange-500">
                        </div>
                    </div>
                </div>
                
                <button id="executeTransformBtn" class="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg transition-colors duration-200 flex items-center btn-hover-effect">
                    <i data-lucide="cpu" class="h-4 w-4 mr-2"></i>
                    执行变换分析
                </button>
                
                <!-- Transform Result Chart -->
                <div class="bg-white border border-gray-200 rounded-lg p-6">
                    <h5 class="text-base font-semibold mb-4">变换结果</h5>
                    <div id="transformResultChart" class="h-96 w-full">
                        <div class="flex items-center justify-center h-full bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
                            <div class="text-center text-gray-500">
                                <i data-lucide="settings" class="h-12 w-12 mx-auto mb-2 opacity-50"></i>
                                <div>点击"执行变换分析"查看结果</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `
  }

  initializeModule(moduleId) {
    // 重新初始化图标
    this.initializeIcons()

    switch (moduleId) {
      case "time-domain":
        this.initTimeDomainModule()
        break
      case "frequency-domain":
        this.initFrequencyDomainModule()
        break
      case "time-average":
        this.initTimeAverageModule()
        break
      case "advanced-transforms":
        this.initAdvancedTransformsModule()
        break
    }
  }

  // 🔧 修复：改进时域模块初始化
  initTimeDomainModule() {
    console.log("🔧 初始化时域模块...", {
      hasData: !!this.currentData,
      hasTimeData: !!this.currentData?.time_domain_data,
      hasEcharts: !!this.echarts,
    })

    // 检查必要条件
    if (!this.currentData) {
      console.warn("❌ 没有数据，无法初始化时域图表")
      return
    }

    if (!this.echarts) {
      console.warn("❌ ECharts未加载，无法初始化图表")
      return
    }

    const chartContainer = document.getElementById("timeDomainChart")
    if (!chartContainer) {
      console.warn("❌ 找不到图表容器")
      return
    }

    // 🔧 关键修复：延迟初始化，确保DOM完全渲染
    setTimeout(() => {
      // 如果图表已存在，先销毁
      if (this.charts.timeDomain) {
        this.charts.timeDomain.dispose()
        delete this.charts.timeDomain
      }

      // 重新初始化图表
      try {
        this.charts.timeDomain = this.echarts.init(chartContainer)

        // 如果有时域数据，立即绘制
        if (this.currentData.time_domain_data) {
          this.plotTimeDomainChart()
          console.log("✅ 时域图表初始化并绘制成功")
        } else {
          // 如果没有时域数据，显示提示
          this.showTimeDomainPlaceholder()
          console.log("⏳ 时域数据不存在，显示占位符")
        }
      } catch (error) {
        console.error("❌ 时域图表初始化失败:", error)
        this.showTimeDomainError("图表初始化失败")
      }
    }, 150) // 增加延迟时间确保DOM渲染完成
  }

  // 🔧 新增：显示占位符
  showTimeDomainPlaceholder() {
    if (!this.charts.timeDomain) return

    const option = {
      title: {
        text: "时域波形",
        left: "center",
        textStyle: { color: "#666" },
      },
      graphic: {
        type: "text",
        left: "center",
        top: "middle",
        style: {
          text: "时域数据加载中...\n请稍候",
          fontSize: 16,
          fill: "#999",
          textAlign: "center",
        },
      },
      xAxis: {
        type: "value",
        name: "时间 (s)",
        axisLabel: { formatter: (value) => value.toFixed(3) },
      },
      yAxis: {
        type: "value",
        name: "幅值",
        axisLabel: { formatter: (value) => value.toFixed(2) },
      },
      grid: { left: "12%", right: "10%", bottom: "15%" },
    }

    this.charts.timeDomain.setOption(option)
  }

  // 🔧 新增：显示错误信息
  showTimeDomainError(message) {
    if (!this.charts.timeDomain) return

    const option = {
      title: {
        text: "时域波形",
        left: "center",
        textStyle: { color: "#ef4444" },
      },
      graphic: {
        type: "text",
        left: "center",
        top: "middle",
        style: {
          text: `❌ ${message}\n点击重新加载数据`,
          fontSize: 16,
          fill: "#ef4444",
          textAlign: "center",
        },
      },
      xAxis: {
        type: "value",
        name: "时间 (s)",
        axisLabel: { formatter: (value) => value.toFixed(3) },
      },
      yAxis: {
        type: "value",
        name: "幅值",
        axisLabel: { formatter: (value) => value.toFixed(2) },
      },
      grid: { left: "12%", right: "10%", bottom: "15%" },
    }

    this.charts.timeDomain.setOption(option)
  }

  initFrequencyDomainModule() {
    // FFT按钮事件
    const fftBtn = document.getElementById("fftBtn")
    if (fftBtn) {
      fftBtn.addEventListener("click", this.handleFFT.bind(this))
    }
  }

  initTimeAverageModule() {
    // 时域平均按钮事件
    const timeAverageBtn = document.getElementById("timeAverageBtn")
    if (timeAverageBtn) {
      timeAverageBtn.addEventListener("click", this.handleTimeAverage.bind(this))
    }
  }

  initAdvancedTransformsModule() {
    // 变换方法选择事件
    document.querySelectorAll(".transform-method").forEach((method) => {
      method.addEventListener("click", this.handleTransformMethodSelect.bind(this))
    })

    // 执行变换按钮事件
    const executeBtn = document.getElementById("executeTransformBtn")
    if (executeBtn) {
      executeBtn.addEventListener("click", this.handleExecuteTransform.bind(this))
    }
  }

  // 🔧 修复：改进图表绘制方法
  plotTimeDomainChart() {
    if (!this.charts.timeDomain || !this.currentData?.time_domain_data) {
      console.warn("❌ 无法绘制时域图表：缺少图表实例或数据")
      return
    }

    console.log("📊 绘制时域图表，数据点数:", this.currentData.time_domain_data.length)

    const option = {
      title: { text: "时域波形", left: "center" },
      tooltip: {
        trigger: "axis",
        formatter: (params) => {
          const time = Number.parseFloat(params[0].axisValue).toFixed(4)
          const value = Number.parseFloat(params[0].value[1]).toFixed(3)
          return `时间: ${time}s<br/>幅值: ${value}`
        },
      },
      xAxis: {
        type: "value",
        name: "时间 (s)",
        axisLabel: {
          formatter: (value) => value.toFixed(3),
        },
      },
      yAxis: {
        type: "value",
        name: "幅值",
        axisLabel: {
          formatter: (value) => value.toFixed(2),
        },
      },
      series: [
        {
          type: "line",
          data: this.currentData.time_domain_data,
          sampling: "lttb",
          symbol: "none",
          lineStyle: { color: "#3b82f6", width: 1.5 },
        },
      ],
      grid: { left: "12%", right: "10%", bottom: "15%" },
      // 🔧 添加动画效果
      animation: true,
      animationDuration: 1000,
    }

    try {
      this.charts.timeDomain.setOption(option, true) // 第二个参数true表示不合并配置
      console.log("✅ 时域图表绘制成功")
    } catch (error) {
      console.error("❌ 时域图表绘制失败:", error)
      this.showTimeDomainError("图表绘制失败")
    }
  }

  async handleFFT() {
    const fftBtn = document.getElementById("fftBtn")
    const originalText = fftBtn.innerHTML

    // 更新按钮状态
    fftBtn.innerHTML = '<div class="loading-spinner rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>计算中...'
    fftBtn.disabled = true

    try {
      // 模拟FFT计算
      await new Promise((resolve) => setTimeout(resolve, 2000))

      // 生成模拟频域数据
      const frequencyData = this.generateMockFrequencyData()

      // 初始化频域图表
      const chartContainer = document.getElementById("frequencyDomainChart")
      chartContainer.innerHTML = '<div id="frequencyChart" class="h-full w-full"></div>'

      this.charts.frequency = this.echarts.init(document.getElementById("frequencyChart"))
      this.plotFrequencyChart(frequencyData)

      // 显示统计信息
      this.showFrequencyStats(frequencyData)
    } catch (error) {
      alert("FFT计算失败")
    } finally {
      fftBtn.innerHTML = originalText
      fftBtn.disabled = false
    }
  }

  generateMockFrequencyData() {
    const data = []
    const maxFreq = this.currentData.sampling_rate / 2
    const points = 500

    for (let i = 0; i < points; i++) {
      const freq = (i * maxFreq) / points
      let amplitude = 0

      // 添加一些峰值
      if (Math.abs(freq - 50) < 2) amplitude += 10
      if (Math.abs(freq - 120) < 2) amplitude += 5
      if (Math.abs(freq - 200) < 2) amplitude += 3

      // 添加基础噪声
      amplitude += Math.exp(-freq / 1000) * (1 + 0.5 * Math.random())

      data.push([freq, amplitude])
    }

    return data
  }

  plotFrequencyChart(data) {
    if (!this.charts.frequency) return

    const option = {
      title: { text: "频域波形", left: "center" },
      tooltip: {
        trigger: "axis",
        formatter: (params) => {
          const freq = Number.parseFloat(params[0].axisValue).toFixed(1)
          const value = Number.parseFloat(params[0].value[1]).toFixed(4)
          return `频率: ${freq}Hz<br/>幅值: ${value}`
        },
      },
      xAxis: {
        type: "value",
        name: "频率 (Hz)",
        axisLabel: {
          formatter: (value) => Math.round(value),
        },
      },
      yAxis: {
        type: "value",
        name: "幅值",
        axisLabel: {
          formatter: (value) => value.toFixed(2),
        },
      },
      series: [
        {
          type: "line",
          data: data,
          sampling: "lttb",
          symbol: "none",
          lineStyle: { color: "#10b981", width: 2 },
        },
      ],
      grid: { left: "12%", right: "10%", bottom: "15%" },
    }

    this.charts.frequency.setOption(option)
  }

  showFrequencyStats(data) {
    const statsContainer = document.getElementById("frequencyStats")
    const pointsCount = document.getElementById("freqPointsCount")
    const maxFreq = document.getElementById("maxFrequency")

    if (statsContainer && pointsCount && maxFreq) {
      pointsCount.textContent = data.length
      maxFreq.textContent = Math.max(...data.map((p) => p[0])).toFixed(1)
      statsContainer.classList.remove("hidden")
    }
  }

  async handleTimeAverage() {
    const btn = document.getElementById("timeAverageBtn")
    const originalText = btn.innerHTML

    btn.innerHTML = '<div class="loading-spinner rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>处理中...'
    btn.disabled = true

    try {
      await new Promise((resolve) => setTimeout(resolve, 1500))
      alert("时域平均处理完成")
    } catch (error) {
      alert("处理失败")
    } finally {
      btn.innerHTML = originalText
      btn.disabled = false
    }
  }

  handleTransformMethodSelect(event) {
    const method = event.currentTarget
    const radio = method.querySelector('input[type="radio"]')
    radio.checked = true

    // 显示/隐藏参数设置
    const cepParams = document.getElementById("cepParams")
    const lcepParams = document.getElementById("lcepParams")

    cepParams.classList.add("hidden")
    lcepParams.classList.add("hidden")

    if (radio.value === "cep") {
      cepParams.classList.remove("hidden")
    } else if (radio.value === "lcep") {
      lcepParams.classList.remove("hidden")
    }

    // 更新样式
    document.querySelectorAll(".transform-method").forEach((m) => {
      m.classList.remove("border-blue-500", "bg-blue-50")
    })
    method.classList.add("border-blue-500", "bg-blue-50")
  }

  async handleExecuteTransform() {
    const selectedMethod = document.querySelector('input[name="transformMethod"]:checked')
    if (!selectedMethod) {
      alert("请先选择变换方法")
      return
    }

    const btn = document.getElementById("executeTransformBtn")
    const originalText = btn.innerHTML

    btn.innerHTML = '<div class="loading-spinner rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>计算中...'
    btn.disabled = true

    try {
      await new Promise((resolve) => setTimeout(resolve, 3000))

      // 生成变换结果
      const transformData = this.generateMockTransformData()

      // 显示结果
      const chartContainer = document.getElementById("transformResultChart")
      chartContainer.innerHTML = '<div id="transformChart" class="h-full w-full"></div>'

      this.charts.transform = this.echarts.init(document.getElementById("transformChart"))
      this.plotTransformChart(transformData, selectedMethod.value)
    } catch (error) {
      alert("变换计算失败")
    } finally {
      btn.innerHTML = originalText
      btn.disabled = false
    }
  }

  generateMockTransformData() {
    const freqMin = Number.parseFloat(document.getElementById("freqDisplayMin").value) || 0
    const freqMax = Number.parseFloat(document.getElementById("freqDisplayMax").value) || 180
    const data = []
    const points = 200

    for (let i = 0; i < points; i++) {
      const freq = freqMin + (i * (freqMax - freqMin)) / points
      const amplitude = Math.exp(-i / 50) * (1 + 0.3 * Math.sin(i / 5))
      data.push([freq, amplitude])
    }

    return data
  }

  plotTransformChart(data, methodName) {
    if (!this.charts.transform) return

    const freqMin = Number.parseFloat(document.getElementById("freqDisplayMin").value) || 0
    const freqMax = Number.parseFloat(document.getElementById("freqDisplayMax").value) || 180

    const methodNames = {
      cep: "CEP",
      cpw: "CPW",
      lcep: "LCEP",
    }

    const option = {
      title: { text: `${methodNames[methodName]} 变换结果 (${freqMin}-${freqMax}Hz)`, left: "center" },
      tooltip: {
        trigger: "axis",
        formatter: (params) => {
          const freq = Number.parseFloat(params[0].axisValue).toFixed(1)
          const value = Number.parseFloat(params[0].value[1]).toFixed(4)
          return `频率: ${freq}Hz<br/>幅值: ${value}`
        },
      },
      xAxis: {
        type: "value",
        name: "频率 (Hz)",
        min: freqMin,
        max: freqMax,
        axisLabel: {
          formatter: (value) => Math.round(value),
        },
      },
      yAxis: {
        type: "value",
        name: "幅值",
        axisLabel: {
          formatter: (value) => value.toFixed(3),
        },
      },
      series: [
        {
          type: "line",
          data: data,
          sampling: "lttb",
          symbol: "none",
          lineStyle: { color: "#8b5cf6", width: 2 },
        },
      ],
      grid: { left: "12%", right: "10%", bottom: "15%" },
    }

    this.charts.transform.setOption(option)
  }

  closeActiveModule() {
    const container = document.getElementById("activeModuleContainer")
    container.classList.add("hidden")

    // 清除活动状态
    document.querySelectorAll(".module-card").forEach((c) => c.classList.remove("active"))
    this.activeModule = ""

    // 清理图表
    Object.values(this.charts).forEach((chart) => {
      if (chart && typeof chart.dispose === "function") {
        chart.dispose()
      }
    })
    this.charts = {}
  }

  updateDataStatus() {
    const statusElement = document.getElementById("dataStatus")
    if (this.isDataLoaded) {
      statusElement.textContent = "数据已加载"
      statusElement.className = "px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-600"
    } else {
      statusElement.textContent = "等待数据"
      statusElement.className = "px-2 py-1 text-xs font-medium rounded-full bg-gray-100 text-gray-600"
    }
  }

  showDataOverview() {
    const overview = document.getElementById("dataOverview")
    const samplingRate = document.getElementById("samplingRateDisplay")
    const dataType = document.getElementById("dataTypeDisplay")
    const dataPoints = document.getElementById("dataPointsDisplay")

    if (this.currentData) {
      samplingRate.textContent = this.currentData.sampling_rate.toLocaleString()
      dataType.textContent = this.currentData.data_dtype
      dataPoints.textContent = this.currentData.time_domain_data.length.toLocaleString()

      overview.classList.remove("hidden")
    }
  }

  showLoading(show) {
    const modal = document.getElementById("loadingModal")
    if (show) {
      modal.classList.remove("hidden")
      modal.classList.add("flex")
    } else {
      modal.classList.add("hidden")
      modal.classList.remove("flex")
    }
  }

  resizeCharts() {
    Object.values(this.charts).forEach((chart) => {
      if (chart && typeof chart.resize === "function") {
        chart.resize()
      }
    })
  }
}

// 初始化应用
document.addEventListener("DOMContentLoaded", () => {
  new SignalAnalysisApp()
})
