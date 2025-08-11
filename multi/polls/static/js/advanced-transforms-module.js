// 高级变换模块 - 完整功能
window.AdvancedTransformsModule = {
  currentData: null,
  charts: null,
  echarts: null,
  selectedMethod: "cep",

  generateContent() {
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
                          <input type="radio" name="transformMethod" value="cep" id="cepMethod" class="mr-2" checked>
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
          <div id="cepParams" class="bg-gray-50 border border-gray-200 rounded-lg p-6">
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
  },

  init(currentData, charts, echarts) {
    this.currentData = currentData
    this.charts = charts
    this.echarts = echarts

    console.log("🔧 初始化高级变换模块...")

    // 绑定变换方法选择事件
    document.querySelectorAll(".transform-method").forEach((method) => {
      method.addEventListener("click", this.handleTransformMethodSelect.bind(this))
    })

    // 绑定执行变换按钮事件
    const executeBtn = document.getElementById("executeTransformBtn")
    if (executeBtn) {
      executeBtn.addEventListener("click", this.handleExecuteTransform.bind(this))
    }

    // 设置默认选中的方法
    this.selectedMethod = "cep"
    document.querySelector('[data-method="cep"]').classList.add("border-blue-500", "bg-blue-50")
  },

  handleTransformMethodSelect(event) {
    const method = event.currentTarget
    const radio = method.querySelector('input[type="radio"]')
    radio.checked = true
    this.selectedMethod = radio.value

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
  },

  async handleExecuteTransform() {
    const btn = document.getElementById("executeTransformBtn")
    const originalText = btn.innerHTML

    btn.innerHTML = '<div class="loading-spinner rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>计算中...'
    btn.disabled = true

    try {
      const params = this.getTransformParams()

      // 修正：确保频率范围参数传递到后端
      const requestBody = {
        data_encoded: this.currentData.data_encoded,
        sampling_rate: this.currentData.sampling_rate,
        data_dtype: this.currentData.data_dtype,
        method: this.selectedMethod,
        freq_display_min: params.freq_display_min,
        freq_display_max: params.freq_display_max,
        ...(this.selectedMethod === "cep" ? {
          t_start: params.cep_time_start,
          t_end: params.cep_time_end
        } : {}),
        ...(this.selectedMethod === "lcep" ? {
          freq_low: params.freq_low,
          freq_high: params.freq_high
        } : {}),
      };

      const response = await fetch("/api/perform-transform/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestBody),
      })

      if (response.ok) {
        const result = await response.json()
        if (result.success) {
          this.showTransformResult(result.transform_data)
          console.log("✅ 变换计算成功")
        } else {
          throw new Error(result.error)
        }
      } else {
        throw new Error("变换API调用失败")
      }
    } catch (error) {
      console.error("❌ 变换计算失败:", error.message)
      alert("变换计算失败: " + error.message)
    } finally {
      btn.innerHTML = originalText
      btn.disabled = false
    }
  },

  getTransformParams() {
    const params = {
      freq_display_min: Number.parseFloat(document.getElementById("freqDisplayMin").value) || 0,
      freq_display_max: Number.parseFloat(document.getElementById("freqDisplayMax").value) || 180,
    }

    if (this.selectedMethod === "cep") {
      params.cep_time_start = Number.parseFloat(document.getElementById("cepTimeStart").value) || 0.01
      params.cep_time_end = Number.parseFloat(document.getElementById("cepTimeEnd").value) || 0.05
    } else if (this.selectedMethod === "lcep") {
      params.freq_low = Number.parseFloat(document.getElementById("freqLow").value) || 10
      params.freq_high = Number.parseFloat(document.getElementById("freqHigh").value) || 1000
    }

    return params
  },

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
  },

  showTransformResult(transformData) {
    const chartContainer = document.getElementById("transformResultChart")

    try {
      // 清理现有图表
      if (this.charts.transform) {
        this.charts.transform.dispose()
        delete this.charts.transform
      }

      // 创建图表容器
      chartContainer.innerHTML = '<div id="transformChart" class="h-full w-full"></div>'

      // 初始化ECharts
      this.charts.transform = this.echarts.init(document.getElementById("transformChart"))

      // 绘制变换结果图表
      this.plotTransformChart(transformData)

      console.log("✅ 变换结果图表显示成功")
    } catch (error) {
      console.error("❌ 变换结果显示失败:", error)
    }
  },

  plotTransformChart(data) {
    if (!this.charts.transform) return

    const freqMin = Number.parseFloat(document.getElementById("freqDisplayMin").value) || 0
    const freqMax = Number.parseFloat(document.getElementById("freqDisplayMax").value) || 180

    const methodNames = {
      cep: "CEP",
      cpw: "CPW",
      lcep: "LCEP",
    }

    const option = {
      title: {
        text: `${methodNames[this.selectedMethod]} 变换结果 (${freqMin}-${freqMax}Hz)`,
        left: "center",
      },
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
          lineStyle: { color: "#f97316", width: 2 },
        },
      ],
      grid: { left: "12%", right: "10%", bottom: "15%" },
      animation: true,
      animationDuration: 1000,
    }

    this.charts.transform.setOption(option, true)
  },
}
