// 完整的时域平均模块
window.TimeAverageModule = {
  currentData: null,
  referenceData: null,
  charts: null,
  echarts: null,

  generateContent() {
    return `
      <div class="space-y-6">
          <div class="flex items-center">
              <i data-lucide="zap" class="h-5 w-5 mr-2 text-purple-600"></i>
              <h4 class="text-lg font-semibold">时域平均处理</h4>
          </div>

          <!-- 算法说明 -->
          <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div class="flex items-start">
                  <i data-lucide="info" class="h-4 w-4 mr-2 text-blue-600 mt-0.5"></i>
                  <div class="text-sm text-blue-800">
                      <strong>时域平均法原理：</strong>需要主信号和鉴相信号。鉴相信号用于确定平均的起始点，通过同步平均提高信噪比。
                  </div>
              </div>
          </div>

          <!-- 信号状态 -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div class="bg-white border border-gray-200 rounded-lg p-4">
                  <h5 class="text-sm font-semibold mb-3 flex items-center">
                      <i data-lucide="file-text" class="h-4 w-4 mr-2 text-blue-600"></i>
                      主信号状态
                  </h5>
                  <div id="mainSignalStatus" class="text-sm text-gray-600">
                      <div>状态: <span class="text-green-600 font-medium">已加载</span></div>
                      <div>采样率: <span id="mainSamplingRate">--</span> Hz</div>
                      <div>数据点: <span id="mainDataPoints">--</span></div>
                  </div>
              </div>

              <div class="bg-white border border-gray-200 rounded-lg p-4">
                  <h5 class="text-sm font-semibold mb-3 flex items-center">
                      <i data-lucide="file-text" class="h-4 w-4 mr-2 text-orange-600"></i>
                      鉴相信号状态
                  </h5>
                  <div id="referenceSignalStatus" class="text-sm text-gray-600">
                      <div>状态: <span id="refStatus" class="text-red-600 font-medium">未上传</span></div>
                      <div>采样率: <span id="refSamplingRate">--</span> Hz</div>
                      <div>数据点: <span id="refDataPoints">--</span></div>
                  </div>
                  <div class="mt-3">
                      <input type="file" id="referenceFileInput" accept=".mat,.csv,.npy" class="hidden">
                      <button id="uploadRefBtn" class="w-full bg-blue-500 hover:bg-blue-600 text-white px-3 py-2 rounded-lg text-sm transition-colors duration-200 flex items-center justify-center btn-hover-effect">
                          <i data-lucide="upload" class="h-4 w-4 mr-2"></i>
                          上传鉴相信号
                      </button>
                  </div>
              </div>
          </div>

          <!-- 处理参数 -->
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
                      <div class="text-xs text-gray-500">理论信噪比提升: <span id="snrImprovement">3.2x</span></div>
                  </div>
                  <div class="space-y-2">
                      <label for="windowSize" class="block text-sm font-medium text-gray-700">分析窗口大小</label>
                      <input type="number" id="windowSize" value="1024" min="64" max="8192" step="64"
                             class="block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-purple-500 focus:border-purple-500">
                      <div class="text-xs text-gray-500">每个周期的数据点数</div>
                  </div>
              </div>
          </div>

          <!-- 处理按钮 -->
          <button id="timeAverageBtn" disabled class="bg-purple-600 hover:bg-purple-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white px-6 py-2 rounded-lg transition-colors duration-200 flex items-center btn-hover-effect">
              <i data-lucide="play" class="h-4 w-4 mr-2"></i>
              开始时域平均
          </button>

          <!-- 结果显示 -->
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div class="bg-white border border-gray-200 rounded-lg p-4 text-center">
                  <div id="avgCountDisplay" class="text-2xl font-bold text-purple-600">10</div>
                  <div class="text-sm text-gray-600">平均次数</div>
              </div>
              <div class="bg-white border border-gray-200 rounded-lg p-4 text-center">
                  <div id="windowSizeDisplay" class="text-2xl font-bold text-blue-600">1024</div>
                  <div class="text-sm text-gray-600">窗口大小</div>
              </div>
              <div class="bg-white border border-gray-200 rounded-lg p-4 text-center">
                  <div id="periodsFound" class="text-2xl font-bold text-green-600">--</div>
                  <div class="text-sm text-gray-600">检测周期数</div>
              </div>
          </div>
      </div>
    `
  },

  init(currentData, charts, echarts) {
    this.currentData = currentData
    this.charts = charts
    this.echarts = echarts

    console.log("🔧 初始化完整时域平均模块...")

    // 更新主信号状态
    this.updateMainSignalStatus()

    // 绑定事件
    this.bindEvents()
  },

  bindEvents() {
    // 鉴相信号上传
    const uploadBtn = document.getElementById("uploadRefBtn")
    const fileInput = document.getElementById("referenceFileInput")

    if (uploadBtn && fileInput) {
      uploadBtn.addEventListener("click", () => fileInput.click())
      fileInput.addEventListener("change", this.handleReferenceUpload.bind(this))
    }

    // 时域平均处理
    const timeAverageBtn = document.getElementById("timeAverageBtn")
    if (timeAverageBtn) {
      timeAverageBtn.addEventListener("click", this.handleTimeAverage.bind(this))
    }

    // 参数变化事件
    const avgCountInput = document.getElementById("averageCount")
    const windowSizeInput = document.getElementById("windowSize")

    if (avgCountInput) {
      avgCountInput.addEventListener("input", this.updateDisplayValues.bind(this))
    }
    if (windowSizeInput) {
      windowSizeInput.addEventListener("input", this.updateDisplayValues.bind(this))
    }
  },

  updateMainSignalStatus() {
    if (this.currentData) {
      const samplingRateEl = document.getElementById("mainSamplingRate")
      const dataPointsEl = document.getElementById("mainDataPoints")

      if (samplingRateEl) samplingRateEl.textContent = this.currentData.sampling_rate.toLocaleString()
      if (dataPointsEl) dataPointsEl.textContent = this.currentData.time_domain_data?.length.toLocaleString() || "N/A"
    }
  },

  async handleReferenceUpload(event) {
    const file = event.target.files[0]
    if (!file) return

    const uploadBtn = document.getElementById("uploadRefBtn")
    const originalText = uploadBtn.innerHTML

    uploadBtn.innerHTML =
      '<div class="loading-spinner rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>上传中...'
    uploadBtn.disabled = true

    try {
      const formData = new FormData()
      formData.append("file", file)
      formData.append("sampling_rate", this.currentData.sampling_rate.toString())

      const response = await fetch("/api/upload-data-file/", {
        method: "POST",
        body: formData,
      })

      if (response.ok) {
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
          this.updateProcessButton()

          console.log("✅ 鉴相信号上传成功")
        } else {
          throw new Error(result.error)
        }
      } else {
        throw new Error("上传请求失败")
      }
    } catch (error) {
      console.error("❌ 鉴相信号上传失败:", error.message)
      alert("鉴相信号上传失败: " + error.message)
    } finally {
      uploadBtn.innerHTML = originalText
      uploadBtn.disabled = false
    }
  },

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
      if (dataPointsEl) dataPointsEl.textContent = this.referenceData.time_domain_data?.length.toLocaleString() || "N/A"
    }
  },

  updateProcessButton() {
    const btn = document.getElementById("timeAverageBtn")
    if (btn && this.referenceData) {
      btn.disabled = false
      btn.className =
        "bg-purple-600 hover:bg-purple-700 text-white px-6 py-2 rounded-lg transition-colors duration-200 flex items-center"
    }
  },

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

      if (response.ok) {
        const result = await response.json()
        if (result.success) {
          // 更新结果显示
          const periodsFoundEl = document.getElementById("periodsFound")
          if (periodsFoundEl) periodsFoundEl.textContent = result.periods_found

          alert(
            `时域平均处理完成！\n` +
              `检测到 ${result.periods_found} 个周期\n` +
              `平均次数: ${averageCount}\n` +
              `信噪比提升: ${result.snr_improvement.toFixed(1)}x`,
          )
        } else {
          throw new Error(result.error)
        }
      } else {
        throw new Error("时域平均API调用失败")
      }
    } catch (error) {
      console.warn("⚠️ 时域平均API失败，使用模拟处理:", error.message)

      // 模拟处理
      await new Promise((resolve) => setTimeout(resolve, 2000))

      const mockPeriods = Math.floor(Math.random() * 20) + 10
      const periodsFoundEl = document.getElementById("periodsFound")
      if (periodsFoundEl) periodsFoundEl.textContent = mockPeriods

      alert(
        `时域平均处理完成（模拟）\n` +
          `模拟检测到 ${mockPeriods} 个周期\n` +
          `平均次数: ${document.getElementById("averageCount").value}\n` +
          `信噪比提升: ${Math.sqrt(Number.parseInt(document.getElementById("averageCount").value)).toFixed(1)}x`,
      )
    } finally {
      btn.innerHTML = originalText
      btn.disabled = false
    }
  },

  updateDisplayValues() {
    const averageCount = Number.parseInt(document.getElementById("averageCount").value) || 10
    const windowSize = Number.parseInt(document.getElementById("windowSize").value) || 1024

    // 更新显示值
    const avgCountDisplay = document.getElementById("avgCountDisplay")
    const windowSizeDisplay = document.getElementById("windowSizeDisplay")
    const snrImprovement = document.getElementById("snrImprovement")

    if (avgCountDisplay) avgCountDisplay.textContent = averageCount
    if (windowSizeDisplay) windowSizeDisplay.textContent = windowSize
    if (snrImprovement) snrImprovement.textContent = Math.sqrt(averageCount).toFixed(1) + "x"
  },
}
