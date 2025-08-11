import os
import sys
import django

# 设置Django环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from polls.models import MonitorTask

def verify_sine_data():
    """验证正弦波数据是否正确保存在数据库中"""
    
    # 查找正弦波测试任务
    task = MonitorTask.objects.filter(task_name="正弦波单通道测试数据").first()
    
    if not task:
        print("❌ 未找到正弦波测试任务")
        return
    
    print(f"✅ 找到正弦波测试任务:")
    print(f"📊 任务ID: {task.task_id}")
    print(f"📊 任务名称: {task.task_name}")
    print(f"📊 任务描述: {task.task_description}")
    print(f"📊 开始时间: {task.start_time}")
    print(f"📊 结束时间: {task.end_time}")
    print(f"📊 总时长: {task.total_duration_minutes} 分钟")
    print(f"📊 采样率: {task.sample_rate}Hz")
    print(f"📊 总采集次数: {task.total_acquisitions}")
    print(f"📊 总数据点数: {task.total_data_points}")
    print(f"📊 启用通道: {task.enabled_channels}")
    print(f"📊 通道配置: {task.channel_configs}")
    print(f"📊 CSV文件路径: {task.csv_file_path}")
    print(f"📊 文件大小: {task.file_size_mb}MB")
    print(f"📊 是否完成: {task.is_completed}")
    print(f"📊 创建时间: {task.created_at}")
    print(f"📊 更新时间: {task.updated_at}")
    
    # 检查文件是否存在
    if os.path.exists(task.csv_file_path):
        print(f"✅ CSV文件存在: {task.csv_file_path}")
    else:
        print(f"❌ CSV文件不存在: {task.csv_file_path}")
    
    # 显示所有监控任务
    print(f"\n📋 数据库中的所有监控任务:")
    all_tasks = MonitorTask.objects.all().order_by('-created_at')
    for i, t in enumerate(all_tasks, 1):
        print(f"  {i}. {t.task_name} (ID: {t.task_id}) - {t.created_at}")

if __name__ == "__main__":
    verify_sine_data() 