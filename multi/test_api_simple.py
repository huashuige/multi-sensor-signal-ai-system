#!/usr/bin/env python
"""
简单的API测试脚本
"""
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from polls.models import TrainingSet

def test_training_status():
    """测试训练状态API"""
    print("🔍 测试训练状态API...")
    
    try:
        # 获取第一个训练集
        training_sets = TrainingSet.objects.all()
        print(f"🔍 找到 {training_sets.count()} 个训练集")
        
        if training_sets.exists():
            training_set = training_sets.first()
            print(f"🔍 训练集ID: {training_set.training_set_id}")
            print(f"🔍 训练集名称: {training_set.name}")
            print(f"🔍 当前轮数: {training_set.current_epoch}")
            print(f"🔍 总轮数: {training_set.total_epochs}")
            print(f"🔍 训练状态: {training_set.training_status}")
            
            # 模拟API响应
            training_status = {
                'status': training_set.training_status,
                'current_epoch': training_set.current_epoch,
                'total_epochs': training_set.total_epochs,
                'training_loss': 0.0234 + (training_set.current_epoch * 0.0001),
                'validation_loss': 0.0256 + (training_set.current_epoch * 0.0001),
                'learning_rate': 0.001,
                'mse_metric': 0.0234 + (training_set.current_epoch * 0.0001),
                'eta': '15分钟'
            }
            
            print("🔍 模拟API响应:")
            print(f"  - 状态: {training_status['status']}")
            print(f"  - 当前轮数: {training_status['current_epoch']}")
            print(f"  - 总轮数: {training_status['total_epochs']}")
            print(f"  - 训练损失: {training_status['training_loss']:.4f}")
            print(f"  - 验证损失: {training_status['validation_loss']:.4f}")
            print(f"  - 学习率: {training_status['learning_rate']}")
            print(f"  - MSE指标: {training_status['mse_metric']:.4f}")
            print(f"  - 预计剩余: {training_status['eta']}")
            
            return training_set.training_set_id
        else:
            print("❌ 没有找到训练集")
            return None
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return None

if __name__ == "__main__":
    training_set_id = test_training_status()
    if training_set_id:
        print(f"\n🔍 测试URL: http://127.0.0.1:8000/polls/api/training-status/{training_set_id}/")
        print("🔍 请在浏览器中访问上述URL来测试API") 
"""
简单的API测试脚本
"""
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from polls.models import TrainingSet

def test_training_status():
    """测试训练状态API"""
    print("🔍 测试训练状态API...")
    
    try:
        # 获取第一个训练集
        training_sets = TrainingSet.objects.all()
        print(f"🔍 找到 {training_sets.count()} 个训练集")
        
        if training_sets.exists():
            training_set = training_sets.first()
            print(f"🔍 训练集ID: {training_set.training_set_id}")
            print(f"🔍 训练集名称: {training_set.name}")
            print(f"🔍 当前轮数: {training_set.current_epoch}")
            print(f"🔍 总轮数: {training_set.total_epochs}")
            print(f"🔍 训练状态: {training_set.training_status}")
            
            # 模拟API响应
            training_status = {
                'status': training_set.training_status,
                'current_epoch': training_set.current_epoch,
                'total_epochs': training_set.total_epochs,
                'training_loss': 0.0234 + (training_set.current_epoch * 0.0001),
                'validation_loss': 0.0256 + (training_set.current_epoch * 0.0001),
                'learning_rate': 0.001,
                'mse_metric': 0.0234 + (training_set.current_epoch * 0.0001),
                'eta': '15分钟'
            }
            
            print("🔍 模拟API响应:")
            print(f"  - 状态: {training_status['status']}")
            print(f"  - 当前轮数: {training_status['current_epoch']}")
            print(f"  - 总轮数: {training_status['total_epochs']}")
            print(f"  - 训练损失: {training_status['training_loss']:.4f}")
            print(f"  - 验证损失: {training_status['validation_loss']:.4f}")
            print(f"  - 学习率: {training_status['learning_rate']}")
            print(f"  - MSE指标: {training_status['mse_metric']:.4f}")
            print(f"  - 预计剩余: {training_status['eta']}")
            
            return training_set.training_set_id
        else:
            print("❌ 没有找到训练集")
            return None
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return None

if __name__ == "__main__":
    training_set_id = test_training_status()
    if training_set_id:
        print(f"\n🔍 测试URL: http://127.0.0.1:8000/polls/api/training-status/{training_set_id}/")
        print("🔍 请在浏览器中访问上述URL来测试API") 
 
 