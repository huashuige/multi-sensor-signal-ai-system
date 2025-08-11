// 实时图表初始化
document.addEventListener('DOMContentLoaded', () => {
  const ctx = document.getElementById('realtime-chart').getContext('2d');
  const chart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: [],
      datasets: [{
        label: '信号强度',
        data: [],
        borderColor: '#66D9FF',
        fill: false,
        tension: 0.1
      }]
    },
    options: {
      animation: false,
      scales: {
        x: {
          type: 'realtime',
          realtime: {
            duration: 20000, // 显示最近 20 秒数据
            refresh: 1000,
            delay: 2000
          }
        },
        y: {
          min: 0,
          max: 500
        }
      }
    }
  });

  // 通过 SSE 接收实时数据
  const source = new EventSource('/api/sensor-stream/');
  source.onmessage = (event) => {
    const data = JSON.parse(event.data);
    const now = new Date().toLocaleTimeString();

    // 更新图表
    chart.data.labels.push(now);
    chart.data.datasets[0].data.push(data.value);
    chart.update();

    // 仅保留最近 20 个数据点
    if (chart.data.labels.length > 20) {
      chart.data.labels.shift();
      chart.data.datasets[0].data.shift();
    }
  };
});