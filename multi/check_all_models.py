import os
import sys
import django
import glob

# 设置Django环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from polls.sensor_data_loader import load_trained_model

def check_all_models():
    """检查所有模型的通道数配置"""
    
    # 查找所有模型文件
    model_files = glob.glob('models/multi_channel_lstm_*.pth')
    
    if not model_files:
        print("❌ 未找到任何模型文件")
        return
    
    print(f"📁 找到 {len(model_files)} 个模型文件:")
    
    # 按时间排序
    model_files.sort()
    
    for i, model_file in enumerate(model_files, 1):
        print(f"\n🔍 模型 {i}: {os.path.basename(model_file)}")
        try:
            trainer, metadata = load_trained_model(model_file)
            model_config = metadata.get('model_config', {})
            num_channels = model_config.get('num_channels', '未知')
            
            print(f"  📊 通道数: {num_channels}")
            print(f"  📊 隐藏层大小: {model_config.get('hidden_size', '未知')}")
            print(f"  📊 LSTM层数: {model_config.get('num_layers', '未知')}")
            print(f"  📊 预测步长: {model_config.get('horizon', '未知')}")
            
        except Exception as e:
            print(f"  ❌ 加载失败: {e}")

if __name__ == "__main__":
    check_all_models() 