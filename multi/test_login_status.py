#!/usr/bin/env python
"""
测试登录状态和训练流程
"""

import os
import sys
import django
import json

# 设置Django环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

def test_login_and_training():
    """测试登录状态和训练流程"""
    print("=" * 60)
    print("测试登录状态和训练流程")
    print("=" * 60)
    
    try:
        from polls.models import TrainingSet, Userinformation
        from django.test import RequestFactory
        from polls.views import Login0
        
        # 1. 检查用户
        print("\n1. 检查用户...")
        users = Userinformation.objects.all()
        print(f"找到 {users.count()} 个用户")
        
        if users.exists():
            user = users.first()
            print(f"用户信息: {user.user_name} ({user.user_email})")
            
            # 2. 创建模拟登录请求
            print("\n2. 创建模拟登录请求...")
            factory = RequestFactory()
            
            # 创建登录请求
            login_request = factory.post('/polls/login/', {
                'email': user.user_email,
                'password': user.user_pwd
            })
            
            # 调用登录视图
            response = Login0(login_request)
            print(f"登录响应状态码: {response.status_code}")
            
            # 3. 检查训练集
            print("\n3. 检查训练集...")
            training_sets = TrainingSet.objects.all()
            print(f"找到 {training_sets.count()} 个训练集")
            
            if training_sets.exists():
                training_set = training_sets.first()
                print(f"训练集: {training_set.name}")
                print(f"状态: {training_set.status}")
                
                # 4. 创建已登录的请求
                print("\n4. 创建已登录的请求...")
                logged_in_request = factory.post('/polls/api/start-training-from-set/', {
                    'training_set_id': training_set.id
                })
                logged_in_request.session = {
                    'is_login': True,
                    'username': user.user_name,
                    'user_email': user.user_email
                }
                
                # 5. 测试开始训练API
                print("\n5. 测试开始训练API...")
                from polls.deep_learning_views import start_training_from_training_set
                
                response = start_training_from_training_set(logged_in_request)
                print(f"训练API响应状态码: {response.status_code}")
                print(f"响应内容: {response.content.decode()}")
                
            else:
                print("❌ 没有找到训练集")
                
        else:
            print("❌ 没有找到用户")
            
        print("\n" + "=" * 60)
        print("✅ 登录和训练流程测试完成！")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_login_and_training() 
"""
测试登录状态和训练流程
"""

import os
import sys
import django
import json

# 设置Django环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

def test_login_and_training():
    """测试登录状态和训练流程"""
    print("=" * 60)
    print("测试登录状态和训练流程")
    print("=" * 60)
    
    try:
        from polls.models import TrainingSet, Userinformation
        from django.test import RequestFactory
        from polls.views import Login0
        
        # 1. 检查用户
        print("\n1. 检查用户...")
        users = Userinformation.objects.all()
        print(f"找到 {users.count()} 个用户")
        
        if users.exists():
            user = users.first()
            print(f"用户信息: {user.user_name} ({user.user_email})")
            
            # 2. 创建模拟登录请求
            print("\n2. 创建模拟登录请求...")
            factory = RequestFactory()
            
            # 创建登录请求
            login_request = factory.post('/polls/login/', {
                'email': user.user_email,
                'password': user.user_pwd
            })
            
            # 调用登录视图
            response = Login0(login_request)
            print(f"登录响应状态码: {response.status_code}")
            
            # 3. 检查训练集
            print("\n3. 检查训练集...")
            training_sets = TrainingSet.objects.all()
            print(f"找到 {training_sets.count()} 个训练集")
            
            if training_sets.exists():
                training_set = training_sets.first()
                print(f"训练集: {training_set.name}")
                print(f"状态: {training_set.status}")
                
                # 4. 创建已登录的请求
                print("\n4. 创建已登录的请求...")
                logged_in_request = factory.post('/polls/api/start-training-from-set/', {
                    'training_set_id': training_set.id
                })
                logged_in_request.session = {
                    'is_login': True,
                    'username': user.user_name,
                    'user_email': user.user_email
                }
                
                # 5. 测试开始训练API
                print("\n5. 测试开始训练API...")
                from polls.deep_learning_views import start_training_from_training_set
                
                response = start_training_from_training_set(logged_in_request)
                print(f"训练API响应状态码: {response.status_code}")
                print(f"响应内容: {response.content.decode()}")
                
            else:
                print("❌ 没有找到训练集")
                
        else:
            print("❌ 没有找到用户")
            
        print("\n" + "=" * 60)
        print("✅ 登录和训练流程测试完成！")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_login_and_training() 
 
 