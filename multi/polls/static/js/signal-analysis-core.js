// 🔧 根据你的API路径修复核心应用类
if (typeof window.SignalAnalysisApp === "undefined") {
  class SignalAnalysisApp {
    constructor() {
      this.currentData = null
      this.isDataLoaded = false
      this.activeModule = ""
      this.charts = {}
      this.lucide = window.lucide
      this.echarts = window.echarts

      // 🔧 添加时域平均相关属性
      this.referenceData = null
      this.timeAverageState = {
        referenceUploaded: false,
        processing: false,
        results: null,
      }

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
        // 添加图标加载成功的标记
        document.body.classList.add('lucide-loaded')
      } else {
        console.warn("⚠️ Lucide图标库未加载，使用备用图标")
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
        const formData = new FormData()
        formData.append("file", fileInput.files[0])
        formData.append("sampling_rate", samplingRateInput.value)

        const response = await fetch("/api/upload-data/", {
          method: "POST",
          body: formData,
        })

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: 文件上传失败`)
        }

        const data = await response.json()

        if (data.success) {
          this.currentData = data
          this.isDataLoaded = true
          this.updateDataStatus()
          this.showDataOverview()

          console.log("✅ 数据加载成功:", this.currentData)

          if (this.activeModule) {
            setTimeout(() => {
              this.refreshActiveModule()
            }, 200)
          }
        } else {
          throw new Error(data.error || "文件处理失败")
        }
      } catch (error) {
        console.error("❌ 数据加载失败:", error.message)
        alert("数据加载失败: " + error.message)
      } finally {
        this.showLoading(false)
      }
    }

    handleModuleClick(event) {
      const card = event.currentTarget
      const moduleId = card.dataset.module

      if (!this.isDataLoaded) {
        alert("请先加载数据文件")
        return
      }

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

      // 根据模块类型加载对应的内容和功能
      switch (moduleId) {
        case "time-domain":
          content.innerHTML = window.TimeDomainModule
            ? window.TimeDomainModule.generateContent()
            : this.generateBasicTimeDomainContent()
          break
        case "frequency-domain":
          content.innerHTML = window.FrequencyDomainModule
            ? window.FrequencyDomainModule.generateContent(this.currentData)
            : this.generateBasicFrequencyContent()
          break
        case "time-average":
          content.innerHTML = this.generateBasicTimeAverageContent()
          break
        case "advanced-transforms":
          content.innerHTML = window.AdvancedTransformsModule
            ? window.AdvancedTransformsModule.generateContent()
            : this.generateBasicTransformContent()
          break
      }

      container.classList.remove("hidden")
      container.classList.add("fade-in")
      container.scrollIntoView({ behavior: "smooth", block: "start" })

      // 延迟初始化模块，确保DOM完全渲染
      setTimeout(() => {
        this.initializeModule(moduleId)
      }, 300)
    }

    generateBasicTimeDomainContent() {
      return `
        <div class="space-y-6">
          <div>
            <h4 class="text-lg font-semibold mb-4 flex items-center">
              <i data-lucide="activity" class="h-5 w-5 mr-2 text-blue-600"></i>
              时域波形显示
            </h4>
            <div class="h-96 w-full border border-gray-200 rounded-lg flex items-center justify-center bg-gray-50">
              <div class="text-center text-gray-500">
                <i data-lucide="activity" class="h-12 w-12 mx-auto mb-2 opacity-50"></i>
                <div>时域模块加载中...</div>
              </div>
            </div>
          </div>
        </div>
      `
    }

    generateBasicFrequencyContent() {
      return `
        <div class="space-y-6">
          <div class="flex items-center justify-between">
            <h4 class="text-lg font-semibold flex items-center">
              <i data-lucide="bar-chart-3" class="h-5 w-5 mr-2 text-green-600"></i>
              频域分析
            </h4>
            <button id="basicFftBtn" class="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg">
              执行FFT变换
            </button>
          </div>
          <div class="h-96 w-full border border-gray-200 rounded-lg flex items-center justify-center bg-gray-50">
            <div class="text-center text-gray-500">
              <i data-lucide="bar-chart-3" class="h-12 w-12 mx-auto mb-2 opacity-50"></i>
              <div>点击"执行FFT变换"开始分析</div>
            </div>
          </div>
        </div>
      `
    }

    generateBasicTimeAverageContent() {
      return `
        <div class="space-y-6">
          <div class="flex items-center">
            <i data-lucide="zap" class="h-5 w-5 mr-2 text-purple-600"></i>
            <h4 class="text-lg font-semibold">时域平均处理</h4>
          </div>

          <!-- 算法说明 -->
          <div class="bg-blue-50 border border-blue-200 rounded-lg p-3">
            <div class="flex items-start">
              <i data-lucide="info" class="h-4 w-4 mr-2 text-blue-600 mt-0.5"></i>
              <div class="text-sm text-blue-800">
                <strong>时域平均法原理：</strong>需要主信号和鉴相信号。鉴相信号用于确定平均的起始点，通过同步平均提高信噪比。
              </div>
            </div>
          </div>

          <!-- 主要布局：左侧控制面板，右侧图表显示 -->
          <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <!-- 左侧控制面板 -->
            <div class="lg:col-span-1 space-y-4">
              <!-- 信号状态 - 紧凑布局 -->
              <div class="space-y-3">
                <div class="bg-white border border-gray-200 rounded-lg p-3">
                  <h5 class="text-sm font-semibold mb-2 flex items-center">
                    <i data-lucide="file-text" class="h-4 w-4 mr-2 text-blue-600"></i>
                    主信号状态
                  </h5>
                  <div class="text-xs text-gray-600 space-y-1">
                    <div>状态: <span class="text-green-600 font-medium">已加载</span></div>
                    <div>采样率: <span id="mainSamplingRate">${this.currentData?.sampling_rate || "--"}</span> Hz</div>
                    <div>数据点: <span id="mainDataPoints">${this.currentData?.time_domain_data?.length || "--"}</span></div>
                  </div>
                </div>

                <div class="bg-white border border-gray-200 rounded-lg p-3">
                  <h5 class="text-sm font-semibold mb-2 flex items-center">
                    <i data-lucide="file-text" class="h-4 w-4 mr-2 text-orange-600"></i>
                    鉴相信号状态
                  </h5>
                  <div class="text-xs text-gray-600 space-y-1 mb-2">
                    <div>状态: <span id="refStatus" class="text-red-600 font-medium">未上传</span></div>
                    <div>采样率: <span id="refSamplingRate">--</span> Hz</div>
                    <div>数据点: <span id="refDataPoints">--</span></div>
                  </div>
                  <input type="file" id="referenceFileInput" accept=".mat,.csv,.npy" class="hidden">
                  <button id="uploadRefBtn" class="w-full bg-blue-500 hover:bg-blue-600 text-white px-3 py-2 rounded-lg text-sm transition-colors duration-200 flex items-center justify-center btn-hover-effect">
                    <i data-lucide="upload" class="h-4 w-4 mr-2"></i>
                    上传鉴相信号
                  </button>
                </div>
              </div>

              <!-- 处理参数 - 紧凑布局 -->
              <div class="bg-white border border-gray-200 rounded-lg p-3">
                <h5 class="text-sm font-semibold mb-3 flex items-center">
                  <i data-lucide="settings" class="h-4 w-4 mr-2"></i>
                  处理参数
                </h5>
                <div class="space-y-3">
                  <div>
                    <label for="averageCount" class="block text-xs font-medium text-gray-700 mb-1">平均次数</label>
                    <input type="number" id="averageCount" value="10" min="1" max="100"
                           class="block w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:ring-purple-500 focus:border-purple-500">
                    <div class="text-xs text-gray-500 mt-1">理论信噪比提升: <span id="snrImprovement">3.2x</span></div>
                  </div>
                  <div>
                    <label for="windowSize" class="block text-xs font-medium text-gray-700 mb-1">分析窗口大小</label>
                    <input type="number" id="windowSize" value="1024" min="64" max="8192" step="64"
                           class="block w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:ring-purple-500 focus:border-purple-500">
                    <div class="text-xs text-gray-500 mt-1">每个周期的数据点数</div>
                  </div>
                </div>
              </div>

              <!-- 处理按钮 -->
              <button id="timeAverageBtn" disabled class="w-full bg-purple-600 hover:bg-purple-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white px-4 py-2 rounded-lg transition-colors duration-200 flex items-center justify-center btn-hover-effect">
                <i data-lucide="play" class="h-4 w-4 mr-2"></i>
                开始时域平均
              </button>

              <!-- 结果统计 - 紧凑显示 -->
              <div class="grid grid-cols-1 gap-2">
                <div class="bg-white border border-gray-200 rounded-lg p-2 text-center">
                  <div id="avgCountDisplay" class="text-lg font-bold text-purple-600">10</div>
                  <div class="text-xs text-gray-600">平均次数</div>
                </div>
                <div class="bg-white border border-gray-200 rounded-lg p-2 text-center">
                  <div id="windowSizeDisplay" class="text-lg font-bold text-blue-600">1024</div>
                  <div class="text-xs text-gray-600">窗口大小</div>
                </div>
                <div class="bg-white border border-gray-200 rounded-lg p-2 text-center">
                  <div id="periodsFound" class="text-lg font-bold text-green-600">--</div>
                  <div class="text-xs text-gray-600">检测周期数</div>
                </div>
              </div>
            </div>

            <!-- 右侧图表显示区域 -->
            <div class="lg:col-span-2 space-y-4">
              <!-- 原始信号对比 -->
              <div class="bg-white border border-gray-200 rounded-lg p-4">
                <h5 class="text-sm font-semibold mb-3 flex items-center">
                  <i data-lucide="activity" class="h-4 w-4 mr-2 text-blue-600"></i>
                  原始信号对比
                </h5>
                <div id="originalSignalsChart" class="h-64 w-full"></div>
              </div>

              <!-- 时域平均结果 -->
              <div class="bg-white border border-gray-200 rounded-lg p-4">
                <h5 class="text-sm font-semibold mb-3 flex items-center">
                  <i data-lucide="zap" class="h-4 w-4 mr-2 text-purple-600"></i>
                  时域平均结果
                </h5>
                <div id="timeAverageResultChart" class="h-64 w-full"></div>
              </div>

              <!-- 信噪比改善对比 -->
              <div class="bg-white border border-gray-200 rounded-lg p-4">
                <h5 class="text-sm font-semibold mb-3 flex items-center">
                  <i data-lucide="trending-up" class="h-4 w-4 mr-2 text-green-600"></i>
                  信噪比改善对比
                </h5>
                <div id="snrComparisonChart" class="h-48 w-full"></div>
              </div>
            </div>
          </div>
        </div>
      `
    }

    generateBasicTransformContent() {
      return `
        <div class="space-y-6">
          <div class="flex items-center">
            <i data-lucide="settings" class="h-5 w-5 mr-2 text-orange-600"></i>
            <h4 class="text-lg font-semibold">高级变换分析</h4>
          </div>
          <div class="text-center py-8 text-gray-500">
            <i data-lucide="settings" class="h-12 w-12 mx-auto mb-2 opacity-50"></i>
            <div>高级变换模块加载中...</div>
          </div>
        </div>
      `
    }

    refreshActiveModule() {
      if (this.activeModule) {
        this.initializeModule(this.activeModule)
      }
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

    initializeModule(moduleId) {
      this.initializeIcons()

      switch (moduleId) {
        case "time-domain":
          if (window.TimeDomainModule) {
            window.TimeDomainModule.init(this.currentData, this.charts, this.echarts)
          } else {
            this.initBasicTimeDomain()
          }
          break
        case "frequency-domain":
          if (window.FrequencyDomainModule) {
            window.FrequencyDomainModule.init(this.currentData, this.charts, this.echarts)
          } else {
            this.initBasicFrequencyDomain()
          }
          break
        case "time-average":
          this.initTimeAverageModule()
          break
        case "advanced-transforms":
          if (window.AdvancedTransformsModule) {
            window.AdvancedTransformsModule.init(this.currentData, this.charts, this.echarts)
          }
          break
      }
    }

    // 🔧 时域平均模块初始化
    initTimeAverageModule() {
      console.log("🔧 初始化时域平均模块...")

      // 绑定鉴相信号上传事件
      const uploadBtn = document.getElementById("uploadRefBtn")
      const fileInput = document.getElementById("referenceFileInput")

      if (uploadBtn && fileInput) {
        uploadBtn.addEventListener("click", () => fileInput.click())
        fileInput.addEventListener("change", this.handleReferenceUpload.bind(this))
      }

      // 绑定时域平均处理事件
      const timeAverageBtn = document.getElementById("timeAverageBtn")
      if (timeAverageBtn) {
        timeAverageBtn.addEventListener("click", this.handleTimeAverage.bind(this))
      }

      // 绑定参数变化事件
      const avgCountInput = document.getElementById("averageCount")
      const windowSizeInput = document.getElementById("windowSize")

      if (avgCountInput) {
        avgCountInput.addEventListener("input", this.updateTimeAverageDisplayValues.bind(this))
      }
      if (windowSizeInput) {
        windowSizeInput.addEventListener("input", this.updateTimeAverageDisplayValues.bind(this))
      }

      // 初始化显示值
      this.updateTimeAverageDisplayValues()

      // 延迟初始化图表，确保DOM完全渲染
      setTimeout(() => {
        this.initTimeAverageCharts()
      }, 500)
    }

    // 🔧 图表初始化 - 添加完整的错误处理
    initTimeAverageCharts() {
      console.log("🔧 开始初始化时域平均图表...")

      if (!this.echarts) {
        console.error("❌ ECharts未加载")
        return
      }

      try {
        // 检查DOM元素是否存在
        const originalChartsEl = document.getElementById("originalSignalsChart")
        const resultChartEl = document.getElementById("timeAverageResultChart")
        const snrChartEl = document.getElementById("snrComparisonChart")

        if (!originalChartsEl || !resultChartEl || !snrChartEl) {
          console.warn("⚠️ 图表容器元素未找到，延迟初始化...")
          setTimeout(() => {
            this.initTimeAverageCharts()
          }, 500)
          return
        }

        console.log("✅ 找到所有图表容器元素，开始初始化...")

        // 初始化原始信号对比图表
        const originalChart = this.echarts.init(originalChartsEl)
        originalChart.setOption({
          title: {
            text: "主信号 vs 鉴相信号",
            textStyle: { fontSize: 14 },
          },
          tooltip: { trigger: "axis" },
          legend: {
            data: ["主信号", "鉴相信号"],
            textStyle: { fontSize: 12 },
          },
          grid: { left: "10%", right: "10%", bottom: "15%", top: "20%" },
          xAxis: {
            type: "value",
            name: "时间 (s)",
            nameTextStyle: { fontSize: 12 },
          },
          yAxis: {
            type: "value",
            name: "幅值",
            nameTextStyle: { fontSize: 12 },
          },
          series: [
            {
              name: "主信号",
              type: "line",
              data: [],
              lineStyle: { width: 1 },
              symbol: "none",
            },
            {
              name: "鉴相信号",
              type: "line",
              data: [],
              lineStyle: { width: 1 },
              symbol: "none",
            },
          ],
        })

        // 初始化时域平均结果图表
        const resultChart = this.echarts.init(resultChartEl)
        resultChart.setOption({
          title: {
            text: "时域平均前后对比",
            textStyle: { fontSize: 14 },
          },
          tooltip: { trigger: "axis" },
          legend: {
            data: ["平均前", "平均后"],
            textStyle: { fontSize: 12 },
          },
          grid: { left: "10%", right: "10%", bottom: "15%", top: "20%" },
          xAxis: {
            type: "value",
            name: "时间 (s)",
            nameTextStyle: { fontSize: 12 },
          },
          yAxis: {
            type: "value",
            name: "幅值",
            nameTextStyle: { fontSize: 12 },
          },
          series: [
            {
              name: "平均前",
              type: "line",
              data: [],
              lineStyle: { width: 1, color: "#ff6b6b" },
              symbol: "none",
            },
            {
              name: "平均后",
              type: "line",
              data: [],
              lineStyle: { width: 2, color: "#4ecdc4" },
              symbol: "none",
            },
          ],
        })

        // 初始化信噪比对比图表
        const snrChart = this.echarts.init(snrChartEl)
        snrChart.setOption({
          title: {
            text: "信噪比改善效果",
            textStyle: { fontSize: 14 },
          },
          tooltip: { trigger: "axis" },
          grid: { left: "15%", right: "10%", bottom: "15%", top: "20%" },
          xAxis: {
            type: "category",
            data: ["原始信号", "时域平均后"],
          },
          yAxis: {
            type: "value",
            name: "SNR (dB)",
            nameTextStyle: { fontSize: 12 },
          },
          series: [
            {
              type: "bar",
              data: [
                { value: 0, itemStyle: { color: "#ff6b6b" } },
                { value: 0, itemStyle: { color: "#4ecdc4" } },
              ],
              barWidth: "50%",
            },
          ],
        })

        // 保存图表实例
        this.charts.originalSignals = originalChart
        this.charts.timeAverageResult = resultChart
        this.charts.snrComparison = snrChart

        console.log("✅ 时域平均图表初始化完成")

        // 显示初始数据
        this.updateOriginalSignalsChart()
      } catch (error) {
        console.error("❌ 图表初始化失败:", error)
      }
    }

    // 🔧 更新原始信号图表
    updateOriginalSignalsChart() {
      if (!this.charts.originalSignals || !this.currentData) return

      try {
        // 自适应显示主信号数据点
        const totalMainPoints = this.currentData.time_domain_data.length
        let mainSignalData
        if (totalMainPoints <= 10000) {
          mainSignalData = this.currentData.time_domain_data.map((point, index) => {
            if (Array.isArray(point)) {
              return point
            } else {
              return [index / this.currentData.sampling_rate, point]
            }
          })
        } else {
          // 采样显示，最多10000个点
          const step = Math.ceil(totalMainPoints / 10000)
          mainSignalData = []
          for (let i = 0; i < totalMainPoints; i += step) {
            const point = this.currentData.time_domain_data[i]
            if (Array.isArray(point)) {
              mainSignalData.push(point)
            } else {
              mainSignalData.push([i / this.currentData.sampling_rate, point])
            }
          }
        }

        // 自适应显示鉴相信号数据点
        let refSignalData = []
        if (this.referenceData) {
          const totalRefPoints = this.referenceData.time_domain_data.length
          if (totalRefPoints <= 10000) {
            refSignalData = this.referenceData.time_domain_data
          } else {
            const step = Math.ceil(totalRefPoints / 10000)
            for (let i = 0; i < totalRefPoints; i += step) {
              refSignalData.push(this.referenceData.time_domain_data[i])
            }
          }
        }

        this.charts.originalSignals.setOption({
          series: [
            {
              name: "主信号",
              data: mainSignalData,
            },
            {
              name: "鉴相信号",
              data: refSignalData,
            },
          ],
        })

        console.log("✅ 原始信号图表更新完成")
      } catch (error) {
        console.error("❌ 更新原始信号图表失败:", error)
      }
    }

    // 🔧 鉴相信号上传处理
    async handleReferenceUpload(event) {
      const file = event.target.files[0]
      if (!file) return

      const uploadBtn = document.getElementById("uploadRefBtn")
      const originalText = uploadBtn.innerHTML

      uploadBtn.innerHTML =
        '<div class="loading-spinner rounded-full h-3 w-3 border-b-2 border-white mr-1"></div>上传中...'
      uploadBtn.disabled = true

      try {
        const formData = new FormData()
        formData.append("file", file)
        formData.append("sampling_rate", this.currentData.sampling_rate.toString())

        const response = await fetch("/api/upload-data/", {
          method: "POST",
          body: formData,
        })

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: 鉴相信号上传失败`)
        }

        const result = await response.json()

        if (result.success) {
          this.referenceData = {
            data_encoded: result.data_encoded,
            sampling_rate: result.sampling_rate,
            data_dtype: result.data_dtype,
            time_domain_data: result.time_domain_data,
            file_name: file.name,
          }

          this.updateReferenceSignalStatus()
          this.updateTimeAverageProcessButton()
          this.updateOriginalSignalsChart()

          console.log("✅ 鉴相信号上传成功")
        } else {
          throw new Error(result.error || "鉴相信号处理失败")
        }
      } catch (error) {
        console.error("❌ 鉴相信号上传失败:", error.message)
        alert("鉴相信号上传失败: " + error.message)
      } finally {
        uploadBtn.innerHTML = originalText
        uploadBtn.disabled = false
      }
    }

    // 🔧 更新鉴相信号状态
    updateReferenceSignalStatus() {
      if (this.referenceData) {
        const statusEl = document.getElementById("refStatus")
        const samplingRateEl = document.getElementById("refSamplingRate")
        const dataPointsEl = document.getElementById("refDataPoints")

        if (statusEl) {
          statusEl.textContent = "已加载"
          statusEl.className = "text-green-600 font-medium"
        }
        if (samplingRateEl) samplingRateEl.textContent = this.referenceData.sampling_rate.toLocaleString()
        if (dataPointsEl)
          dataPointsEl.textContent = this.referenceData.time_domain_data?.length.toLocaleString() || "N/A"

        this.timeAverageState.referenceUploaded = true
      }
    }

    // 🔧 更新处理按钮状态
    updateTimeAverageProcessButton() {
      const btn = document.getElementById("timeAverageBtn")
      if (btn && this.referenceData) {
        btn.disabled = false
        btn.className =
          "w-full bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg transition-colors duration-200 flex items-center justify-center"
      }
    }

    // 🔧 时域平均处理
    async handleTimeAverage() {
      if (!this.currentData || !this.referenceData) {
        alert("请确保主信号和鉴相信号都已加载")
        return
      }

      const btn = document.getElementById("timeAverageBtn")
      const originalText = btn.innerHTML

      btn.innerHTML = '<div class="loading-spinner rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>处理中...'
      btn.disabled = true

      try {
        const averageCount = Number.parseInt(document.getElementById("averageCount").value)
        const windowSize = Number.parseInt(document.getElementById("windowSize").value)

        const response = await fetch("/api/time-average/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            main_signal: {
              data_encoded: this.currentData.data_encoded,
              sampling_rate: this.currentData.sampling_rate,
              data_dtype: this.currentData.data_dtype,
            },
            reference_signal: {
              data_encoded: this.referenceData.data_encoded,
              sampling_rate: this.referenceData.sampling_rate,
              data_dtype: this.referenceData.data_dtype,
            },
            average_count: averageCount,
            window_size: windowSize,
          }),
        })

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: 时域平均API调用失败`)
        }

        const result = await response.json()

        if (result.success) {
          // 更新结果显示
          const periodsFoundEl = document.getElementById("periodsFound")
          if (periodsFoundEl) periodsFoundEl.textContent = result.periods_found

          this.timeAverageState.results = result

          // 异常提醒：实际平均次数小于设定值
          if (result.periods_found < averageCount) {
            this.showNonBlockingWarning(
              `注意：实际平均周期数为 ${result.periods_found}，小于设定的 ${averageCount}。已自动按可用周期数进行平均。`
            )
          }

          // 更新图表显示
          this.updateTimeAverageResultCharts(result)

          alert(
            `时域平均处理完成！\n` +
              `检测到 ${result.periods_found} 个周期\n` +
              `平均次数: ${result.periods_found}\n` +
              `信噪比提升: ${result.snr_improvement.toFixed(1)}x`,
          )
        } else {
          throw new Error(result.error || "时域平均处理失败")
        }
      } catch (error) {
        console.error("❌ 时域平均处理失败:", error.message)
        alert("时域平均处理失败: " + error.message)
      } finally {
        btn.innerHTML = originalText
        btn.disabled = false
      }
    }

    // 🔧 更新时域平均结果图表
    updateTimeAverageResultCharts(result) {
      if (!this.charts.timeAverageResult || !this.charts.snrComparison) return

      try {
        // 显示平均前（第一个周期段）和平均后
        if (result.averaged_data) {
          const beforeData = result.main_signal_segment || []
          this.charts.timeAverageResult.setOption({
            series: [
              { name: "平均前", data: beforeData },
              { name: "平均后", data: result.averaged_data },
            ],
          })
        }

        // 更新信噪比对比图表
        const snrBefore = 10 // 模拟原始SNR
        const snrAfter = snrBefore + 20 * Math.log10(result.snr_improvement) // 计算改善后的SNR

        this.charts.snrComparison.setOption({
          series: [
            {
              data: [
                { value: snrBefore, itemStyle: { color: "#ff6b6b" } },
                { value: snrAfter, itemStyle: { color: "#4ecdc4" } },
              ],
            },
          ],
        })

        console.log("✅ 时域平均结果图表更新完成")
      } catch (error) {
        console.error("❌ 更新时域平均结果图表失败:", error)
      }
    }

    // 🔧 更新显示值
    updateTimeAverageDisplayValues() {
      const averageCount = Number.parseInt(document.getElementById("averageCount")?.value) || 10
      const windowSize = Number.parseInt(document.getElementById("windowSize")?.value) || 1024

      // 更新显示值
      const avgCountDisplay = document.getElementById("avgCountDisplay")
      const windowSizeDisplay = document.getElementById("windowSizeDisplay")
      const snrImprovement = document.getElementById("snrImprovement")

      if (avgCountDisplay) avgCountDisplay.textContent = averageCount
      if (windowSizeDisplay) windowSizeDisplay.textContent = windowSize
      if (snrImprovement) snrImprovement.textContent = Math.sqrt(averageCount).toFixed(1) + "x"
    }

    // 基础FFT功能
    initBasicFrequencyDomain() {
      const fftBtn = document.getElementById("basicFftBtn")
      if (fftBtn) {
        fftBtn.addEventListener("click", this.handleBasicFFT.bind(this))
      }
    }

    async handleBasicFFT() {
      const btn = document.getElementById("basicFftBtn")
      const originalText = btn.innerHTML
      btn.innerHTML = '<div class="loading-spinner rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>计算中...'
      btn.disabled = true

      try {
        const response = await fetch("/api/perform-fft/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            data_encoded: this.currentData.data_encoded,
            sampling_rate: this.currentData.sampling_rate,
            data_dtype: this.currentData.data_dtype,
          }),
        })

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: FFT API调用失败`)
        }

        const result = await response.json()

        if (result.success) {
          alert("FFT计算完成！")
          console.log("✅ FFT计算成功:", result)
        } else {
          throw new Error(result.error || "FFT计算失败")
        }
      } catch (error) {
        console.error("❌ FFT计算失败:", error.message)
        alert("FFT计算失败: " + error.message)
      } finally {
        btn.innerHTML = originalText
        btn.disabled = false
      }
    }

    initBasicTimeDomain() {
      console.log("🔧 初始化基础时域功能")
    }

    closeActiveModule() {
      const container = document.getElementById("activeModuleContainer")
      container.classList.add("hidden")

      document.querySelectorAll(".module-card").forEach((c) => c.classList.remove("active"))
      this.activeModule = ""

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

    // 新增：非阻断式警告提醒
    showNonBlockingWarning(message) {
      let warnDiv = document.getElementById('nonBlockingWarning')
      if (!warnDiv) {
        warnDiv = document.createElement('div')
        warnDiv.id = 'nonBlockingWarning'
        warnDiv.style.position = 'fixed'
        warnDiv.style.top = '30px'
        warnDiv.style.right = '30px'
        warnDiv.style.zIndex = 9999
        warnDiv.style.background = '#fffbe6'
        warnDiv.style.color = '#ad8b00'
        warnDiv.style.border = '1px solid #ffe58f'
        warnDiv.style.padding = '12px 24px'
        warnDiv.style.borderRadius = '8px'
        warnDiv.style.boxShadow = '0 2px 8px rgba(0,0,0,0.08)'
        warnDiv.style.fontSize = '15px'
        warnDiv.style.display = 'none'
        document.body.appendChild(warnDiv)
      }
      warnDiv.textContent = message
      warnDiv.style.display = 'block'
      setTimeout(() => {
        warnDiv.style.display = 'none'
      }, 5000)
    }
  }

  // 初始化应用
  document.addEventListener("DOMContentLoaded", () => {
    if (!window.signalApp) {
      window.signalApp = new SignalAnalysisApp()
    }
  })

  // 导出到全局
  window.SignalAnalysisApp = SignalAnalysisApp
}
