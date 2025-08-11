// 时域分析模块 - 专门处理时域信号分析
window.TimeDomainModule = {
  currentData: null,
  charts: null,
  echarts: null,
  timeFeatures: null, // 🆕 存储时域特征数据

  generateContent() {
    return `
      <div class="space-y-6">
          <div>
              <h4 class="text-lg font-semibold mb-4 flex items-center">
                  <i data-lucide="activity" class="h-5 w-5 mr-2 text-blue-600"></i>
                  时域波形显示
              </h4>
              <div id="timeDomainChart" class="h-96 w-full border border-gray-200 rounded-lg"></div>
          </div>

          <!-- 🆕 时域特征分析区域 -->
          <div>
              <div class="flex items-center justify-between mb-4">
                  <h4 class="text-lg font-semibold flex items-center">
                      <i data-lucide="trending-up" class="h-5 w-5 mr-2 text-purple-600"></i>
                      时域特征分析
                  </h4>
                  <button id="calculateFeaturesBtn" class="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg transition-colors duration-200 flex items-center">
                      <i data-lucide="calculator" class="h-4 w-4 mr-2"></i>
                      计算特征
                  </button>
              </div>

              <div id="timeFeaturesContainer" class="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <!-- 特征卡片将通过JS动态生成 -->
                  <div class="bg-gray-50 border border-gray-200 rounded-lg p-4 text-center">
                      <div class="text-lg text-gray-400">--</div>
                      <div class="text-sm text-gray-600">峰峰值</div>
                  </div>
                  <div class="bg-gray-50 border border-gray-200 rounded-lg p-4 text-center">
                      <div class="text-lg text-gray-400">--</div>
                      <div class="text-sm text-gray-600">时间长度 (秒)</div>
                  </div>
                  <div class="bg-gray-50 border border-gray-200 rounded-lg p-4 text-center">
                      <div class="text-lg text-gray-400">--</div>
                      <div class="text-sm text-gray-600">峭度</div>
                  </div>
                  <div class="bg-gray-50 border border-gray-200 rounded-lg p-4 text-center">
                      <div class="text-lg text-gray-400">--</div>
                      <div class="text-sm text-gray-600">均值</div>
                  </div>
              </div>
          </div>
      </div>
    `
  },

  async init(currentData, charts, echarts) {
    this.currentData = currentData
    this.charts = charts
    this.echarts = echarts

    console.log("🔧 初始化时域模块...")

    if (!this.currentData || !this.echarts) {
      console.warn("❌ 缺少必要条件")
      return
    }

    const chartContainer = document.getElementById("timeDomainChart")
    if (!chartContainer) {
      console.warn("❌ 找不到图表容器")
      return
    }

    // 绑定特征计算按钮事件
    const calculateBtn = document.getElementById("calculateFeaturesBtn")
    if (calculateBtn) {
      calculateBtn.addEventListener("click", this.calculateTimeFeatures.bind(this))
    }

    // 延迟初始化图表
    setTimeout(() => {
      this.initChart()
    }, 150)
  },

  initChart() {
    const chartContainer = document.getElementById("timeDomainChart")

    try {
      // 清理现有图表
      if (this.charts.timeDomain) {
        this.charts.timeDomain.dispose()
        delete this.charts.timeDomain
      }

      // 初始化新图表
      this.charts.timeDomain = this.echarts.init(chartContainer)

      if (this.currentData.time_domain_data) {
        this.plotChart()
        console.log("✅ 时域图表初始化成功")
      } else {
        this.showPlaceholder()
      }
    } catch (error) {
      console.error("❌ 时域图表初始化失败:", error)
      this.showError("图表初始化失败")
    }
  },

  plotChart() {
    if (!this.charts.timeDomain || !this.currentData?.time_domain_data) {
      console.warn("❌ 无法绘制图表")
      return
    }

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
        axisLabel: { formatter: (value) => value.toFixed(3) },
      },
      yAxis: {
        type: "value",
        name: "幅值",
        axisLabel: { formatter: (value) => value.toFixed(2) },
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
      animation: true,
      animationDuration: 1000,
    }

    try {
      this.charts.timeDomain.setOption(option, true)
      console.log("✅ 时域图表绘制成功")
    } catch (error) {
      console.error("❌ 图表绘制失败:", error)
    }
  },

  showPlaceholder() {
    if (!this.charts.timeDomain) return

    const option = {
      title: { text: "时域波形", left: "center", textStyle: { color: "#666" } },
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
      xAxis: { type: "value", name: "时间 (s)" },
      yAxis: { type: "value", name: "幅值" },
      grid: { left: "12%", right: "10%", bottom: "15%" },
    }

    this.charts.timeDomain.setOption(option)
  },

  showError(message) {
    if (!this.charts.timeDomain) return

    const option = {
      title: { text: "时域波形", left: "center", textStyle: { color: "#ef4444" } },
      graphic: {
        type: "text",
        left: "center",
        top: "middle",
        style: {
          text: `❌ ${message}`,
          fontSize: 16,
          fill: "#ef4444",
          textAlign: "center",
        },
      },
      xAxis: { type: "value", name: "时间 (s)" },
      yAxis: { type: "value", name: "幅值" },
      grid: { left: "12%", right: "10%", bottom: "15%" },
    }

    this.charts.timeDomain.setOption(option)
  },

  // 🆕 计算时域特征
  async calculateTimeFeatures() {
    const btn = document.getElementById("calculateFeaturesBtn")
    const originalText = btn.innerHTML

    btn.innerHTML = '<div class="loading-spinner rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>计算中...'
    btn.disabled = true

    try {
      // 🔧 调用真实的时域特征API
      const response = await fetch("/api/calculate-time-features/", {
        // 使用正确的端点
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          data_encoded: this.currentData.data_encoded,
          sampling_rate: this.currentData.sampling_rate,
          data_dtype: this.currentData.data_dtype, // 添加数据类型
        }),
      })

      if (response.ok) {
        const result = await response.json()
        if (result.success) {
          this.timeFeatures = result.features
          this.updateFeaturesDisplay()
          console.log("✅ 时域特征计算成功:", this.timeFeatures)
        } else {
          throw new Error(result.error)
        }
      } else {
        throw new Error("时域特征API调用失败")
      }
    } catch (error) {
      console.error("❌ 特征计算失败:", error.message)
      alert("特征计算失败: " + error.message)
    } finally {
      btn.innerHTML = originalText
      btn.disabled = false
    }
  },

  // 🆕 生成模拟特征数据（开发用）
  generateMockFeatures() {
    const data = this.currentData.time_domain_data.map((point) => point[1])
    const max = Math.max(...data)
    const min = Math.min(...data)
    const mean = data.reduce((sum, val) => sum + val, 0) / data.length

    // 简单的峭度计算
    const variance = data.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / data.length
    const kurtosis = data.reduce((sum, val) => sum + Math.pow(val - mean, 4), 0) / (data.length * Math.pow(variance, 2))

    return {
      peak_to_peak: max - min, // 峰峰值
      duration: this.currentData.time_domain_data.length / this.currentData.sampling_rate, // 时间长度
      kurtosis: kurtosis, // 峭度
      mean: mean, // 均值
    }
  },

  // 🆕 更新特征显示
  updateFeaturesDisplay() {
    if (!this.timeFeatures) return

    const container = document.getElementById("timeFeaturesContainer")
    container.innerHTML = `
      <div class="bg-white border border-gray-200 rounded-lg p-4 text-center shadow-sm">
          <div class="text-2xl font-bold text-blue-600">${this.timeFeatures.peak_to_peak.toFixed(3)}</div>
          <div class="text-sm text-gray-600">峰峰值</div>
      </div>
      <div class="bg-white border border-gray-200 rounded-lg p-4 text-center shadow-sm">
          <div class="text-2xl font-bold text-green-600">${this.timeFeatures.duration.toFixed(3)}</div>
          <div class="text-sm text-gray-600">时间长度 (秒)</div>
      </div>
      <div class="bg-white border border-gray-200 rounded-lg p-4 text-center shadow-sm">
          <div class="text-2xl font-bold text-purple-600">${this.timeFeatures.kurtosis.toFixed(3)}</div>
          <div class="text-sm text-gray-600">峭度</div>
      </div>
      <div class="bg-white border border-gray-200 rounded-lg p-4 text-center shadow-sm">
          <div class="text-2xl font-bold text-orange-600">${this.timeFeatures.mean.toFixed(3)}</div>
          <div class="text-sm text-gray-600">均值</div>
      </div>
    `

    // 重新初始化图标
    if (window.lucide) {
      window.lucide.createIcons()
    }
  },
}
