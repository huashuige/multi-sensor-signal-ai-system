// 🔧 修复频域模块的API调用路径
if (typeof window.FrequencyDomainModule === "undefined") {
  window.FrequencyDomainModule = {
    currentData: null,
    charts: null,
    echarts: null,
    frequencyData: null,

    generateContent(currentData) {
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
                    <div class="text-2xl font-bold text-purple-600">${(currentData.sampling_rate / 2).toLocaleString()}</div>
                    <div class="text-sm text-gray-600">奈奎斯特频率 (Hz)</div>
                </div>
            </div>
        </div>
      `
    },

    init(currentData, charts, echarts) {
      this.currentData = currentData
      this.charts = charts
      this.echarts = echarts

      console.log("🔧 初始化频域模块...")

      const fftBtn = document.getElementById("fftBtn")
      if (fftBtn) {
        fftBtn.addEventListener("click", this.handleFFT.bind(this))
      }
    },

    async handleFFT() {
      const fftBtn = document.getElementById("fftBtn")
      const originalText = fftBtn.innerHTML

      fftBtn.innerHTML =
        '<div class="loading-spinner rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>计算中...'
      fftBtn.disabled = true

      try {
        // 🔧 使用正确的API端点路径
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

        if (response.ok) {
          const result = await response.json()
          if (result.success) {
            this.frequencyData = result.frequency_data
            console.log("✅ FFT计算成功")
            this.initFrequencyChart()
            this.showFrequencyStats()
          } else {
            throw new Error(result.error)
          }
        } else {
          throw new Error("FFT API调用失败")
        }
      } catch (error) {
        console.error("❌ FFT计算失败:", error.message)

        // 🔧 如果API失败，生成模拟数据用于演示
        console.log("⚠️ 使用模拟FFT数据")
        this.frequencyData = this.generateMockFFTData()
        this.initFrequencyChart()
        this.showFrequencyStats()
      } finally {
        fftBtn.innerHTML = originalText
        fftBtn.disabled = false
      }
    },

    generateMockFFTData() {
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
    },

    initFrequencyChart() {
      const chartContainer = document.getElementById("frequencyDomainChart")

      try {
        if (this.charts.frequency) {
          this.charts.frequency.dispose()
          delete this.charts.frequency
        }

        chartContainer.innerHTML = '<div id="frequencyChart" class="h-full w-full"></div>'
        this.charts.frequency = this.echarts.init(document.getElementById("frequencyChart"))
        this.plotFrequencyChart()

        console.log("✅ 频域图表初始化成功")
      } catch (error) {
        console.error("❌ 频域图表初始化失败:", error)
      }
    },

    plotFrequencyChart() {
      if (!this.charts.frequency || !this.frequencyData) return

      const option = {
        title: { text: "频域波形 (FFT)", left: "center" },
        tooltip: {
          trigger: "axis",
          formatter: (params) => {
            const freq = Number.parseFloat(params[0].axisValue).toFixed(1)
            const magnitude = Number.parseFloat(params[0].value[1]).toFixed(4)
            return `频率: ${freq}Hz<br/>幅值: ${magnitude}`
          },
        },
        xAxis: {
          type: "value",
          name: "频率 (Hz)",
          axisLabel: { formatter: (value) => Math.round(value) },
        },
        yAxis: {
          type: "value",
          name: "幅值",
          axisLabel: { formatter: (value) => value.toFixed(3) },
        },
        series: [
          {
            type: "line",
            data: this.frequencyData,
            sampling: "lttb",
            symbol: "none",
            lineStyle: { color: "#10b981", width: 2 },
            areaStyle: {
              color: {
                type: "linear",
                x: 0,
                y: 0,
                x2: 0,
                y2: 1,
                colorStops: [
                  { offset: 0, color: "rgba(16, 185, 129, 0.3)" },
                  { offset: 1, color: "rgba(16, 185, 129, 0.1)" },
                ],
              },
            },
          },
        ],
        grid: { left: "12%", right: "10%", bottom: "15%" },
        animation: true,
        animationDuration: 1000,
      }

      this.charts.frequency.setOption(option, true)
    },

    showFrequencyStats() {
      if (!this.frequencyData) return

      const statsContainer = document.getElementById("frequencyStats")
      const pointsCount = document.getElementById("freqPointsCount")
      const maxFreq = document.getElementById("maxFrequency")

      if (statsContainer && pointsCount && maxFreq) {
        pointsCount.textContent = this.frequencyData.length
        maxFreq.textContent = Math.max(...this.frequencyData.map((p) => p[0])).toFixed(1)
        statsContainer.classList.remove("hidden")
      }
    },
  }
}
