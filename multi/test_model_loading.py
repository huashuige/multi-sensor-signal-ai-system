import os
import sys
import django

# 设置Django环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from polls.sensor_data_loader import load_trained_model
import glob

def test_model_loading():
    """测试模型加载功能"""
    
    # 查找所有模型文件
    model_files = glob.glob('models/multi_channel_lstm_*.pth')
    
    if not model_files:
        print("❌ 未找到任何模型文件")
        return
    
    print(f"📁 找到 {len(model_files)} 个模型文件:")
    for i, model_file in enumerate(model_files, 1):
        print(f"  {i}. {model_file}")
    
    # 测试每个模型
    for model_file in model_files:
        print(f"\n🔍 测试模型: {model_file}")
        try:
            trainer, metadata = load_trained_model(model_file)
            model = trainer.model
            
            print(f"✅ 模型加载成功!")
            print(f"📊 模型配置: {metadata.get('model_config', {})}")
            print(f"📊 模型参数数量: {sum(p.numel() for p in model.parameters())}")
            
            # 测试模型输入输出
            import torch
            import numpy as np
            
            # 获取模型配置
            model_config = metadata.get('model_config', {})
            num_channels = model_config.get('num_channels', 1)
            window_size = model_config.get('window_size', 24)
            horizon = model_config.get('horizon', 12)
            
            # 创建测试输入
            test_input = torch.randn(1, window_size, num_channels)
            print(f"📊 测试输入形状: {test_input.shape}")
            
            # 前向传播
            model.eval()
            with torch.no_grad():
                output = model(test_input)
                print(f"📊 模型输出形状: {output.shape}")
                print(f"📊 期望输出形状: (1, {num_channels}, {horizon})")
            
            if output.shape == (1, num_channels, horizon):
                print(f"✅ 模型输入输出形状正确!")
            else:
                print(f"❌ 模型输入输出形状不匹配!")
                
        except Exception as e:
            print(f"❌ 模型加载失败: {e}")

if __name__ == "__main__":
    test_model_loading() 