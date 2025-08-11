// signal_upload.js
document.getElementById('uploadBtn').addEventListener('click', async () => {
  const fileInput = document.getElementById('signalFile');
  const status = document.getElementById('uploadStatus');

  if (!fileInput.files.length) {
    alert('请选择一个文件');
    return;
  }

  const file = fileInput.files[0];
  const formData = new FormData();
  formData.append('signal_file', file);

  status.classList.remove('hidden');

  try {
    const res = await fetch('/upload_signal/', {
      method: 'POST',
      body: formData
    });

    const data = await res.json();
    status.classList.add('hidden');

    if (data.success) {
      alert('上传成功，准备绘图');
      console.log('预览数据：', data.signal_preview);

      // 初始化时域图表展示
      const chartDom = document.getElementById('timeChart');
      const myChart = echarts.init(chartDom);
      const option = {
        title: { text: '时域波形预览' },
        tooltip: {},
        xAxis: { type: 'category', data: Array.from({length: data.signal_preview.length}, (_, i) => i) },
        yAxis: { type: 'value' },
        series: [{
          data: data.signal_preview,
          type: 'line',
          smooth: true,
          areaStyle: {}
        }]
      };
      myChart.setOption(option);

    } else {
      alert('上传失败：' + data.error);
    }
  } catch (error) {
    console.error(error);
    alert('文件上传失败');
    status.classList.add('hidden');
  }
});
