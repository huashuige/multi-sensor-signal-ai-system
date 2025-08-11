import os
import sys
import django

# 设置Django环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from polls.sensor_data_loader import load_trained_model
import glob

def test_model_config():
    """测试模型配置传递"""
    
    # 查找最新的模型文件
    model_files = glob.glob('models/multi_channel_lstm_*.pth')
    
    if not model_files:
        print("❌ 未找到任何模型文件")
        return
    
    # 使用最新的模型文件
    model_file = sorted(model_files)[-1]
    print(f"🔍 测试模型: {model_file}")
    
    try:
        trainer, metadata = load_trained_model(model_file)
        
        print(f"✅ 模型加载成功!")
        print(f"📊 完整metadata: {metadata}")
        
        # 检查model_config是否存在
        if 'model_config' in metadata:
            model_config = metadata['model_config']
            print(f"📊 model_config: {model_config}")
            
            if 'num_channels' in model_config:
                print(f"✅ num_channels存在: {model_config['num_channels']}")
            else:
                print(f"❌ num_channels不存在")
        else:
            print(f"❌ model_config不存在")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    test_model_config() 