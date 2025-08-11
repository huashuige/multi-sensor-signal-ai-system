#!/usr/bin/env python
"""
简单测试训练流程
"""

import os
import sys
import django
import json

# 设置Django环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

def test_training_flow():
    """测试训练流程"""
    print("=" * 60)
    print("测试训练流程")
    print("=" * 60)
    
    try:
        from polls.models import TrainingSet, MonitorTask
        from polls.deep_learning_views import start_training_from_training_set
        from django.test import RequestFactory
        from django.contrib.auth.models import User
        
        # 1. 检查训练集
        print("\n1. 检查训练集...")
        training_sets = TrainingSet.objects.all()
        print(f"找到 {training_sets.count()} 个训练集")
        
        if training_sets.exists():
            training_set = training_sets.first()
            print(f"使用训练集: {training_set.name} (ID: {training_set.id})")
            print(f"状态: {training_set.status}")
            print(f"学习参数: {training_set.learning_params}")
            print(f"选中的数据源: {training_set.selected_data_sources}")
            
            # 2. 创建模拟请求
            print("\n2. 创建模拟请求...")
            factory = RequestFactory()
            
            # 创建用户（如果不存在）
            user, created = User.objects.get_or_create(
                username='testuser',
                defaults={'email': 'test@example.com'}
            )
            
            # 创建请求数据
            request_data = {
                'training_set_id': training_set.id
            }
            
            # 创建POST请求
            request = factory.post(
                '/polls/api/start-training-from-set/',
                data=json.dumps(request_data),
                content_type='application/json'
            )
            request.user = user
            
            print(f"请求数据: {request_data}")
            
            # 3. 调用视图函数
            print("\n3. 调用开始训练视图...")
            response = start_training_from_training_set(request)
            
            print(f"响应状态码: {response.status_code}")
            print(f"响应内容: {response.content.decode()}")
            
            # 4. 检查训练集状态
            print("\n4. 检查训练集状态...")
            training_set.refresh_from_db()
            print(f"更新后的状态: {training_set.status}")
            print(f"训练状态: {training_set.training_status}")
            
        else:
            print("❌ 没有找到训练集")
            
        print("\n" + "=" * 60)
        print("✅ 训练流程测试完成！")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_training_flow() 
"""
简单测试训练流程
"""

import os
import sys
import django
import json

# 设置Django环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

def test_training_flow():
    """测试训练流程"""
    print("=" * 60)
    print("测试训练流程")
    print("=" * 60)
    
    try:
        from polls.models import TrainingSet, MonitorTask
        from polls.deep_learning_views import start_training_from_training_set
        from django.test import RequestFactory
        from django.contrib.auth.models import User
        
        # 1. 检查训练集
        print("\n1. 检查训练集...")
        training_sets = TrainingSet.objects.all()
        print(f"找到 {training_sets.count()} 个训练集")
        
        if training_sets.exists():
            training_set = training_sets.first()
            print(f"使用训练集: {training_set.name} (ID: {training_set.id})")
            print(f"状态: {training_set.status}")
            print(f"学习参数: {training_set.learning_params}")
            print(f"选中的数据源: {training_set.selected_data_sources}")
            
            # 2. 创建模拟请求
            print("\n2. 创建模拟请求...")
            factory = RequestFactory()
            
            # 创建用户（如果不存在）
            user, created = User.objects.get_or_create(
                username='testuser',
                defaults={'email': 'test@example.com'}
            )
            
            # 创建请求数据
            request_data = {
                'training_set_id': training_set.id
            }
            
            # 创建POST请求
            request = factory.post(
                '/polls/api/start-training-from-set/',
                data=json.dumps(request_data),
                content_type='application/json'
            )
            request.user = user
            
            print(f"请求数据: {request_data}")
            
            # 3. 调用视图函数
            print("\n3. 调用开始训练视图...")
            response = start_training_from_training_set(request)
            
            print(f"响应状态码: {response.status_code}")
            print(f"响应内容: {response.content.decode()}")
            
            # 4. 检查训练集状态
            print("\n4. 检查训练集状态...")
            training_set.refresh_from_db()
            print(f"更新后的状态: {training_set.status}")
            print(f"训练状态: {training_set.training_status}")
            
        else:
            print("❌ 没有找到训练集")
            
        print("\n" + "=" * 60)
        print("✅ 训练流程测试完成！")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_training_flow() 
 
 