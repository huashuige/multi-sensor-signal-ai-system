import os
import sys
import django

# 设置Django环境
sys.path.append(os.path.join(os.path.dirname(__file__), 'multi'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from polls.models import TrainingSet

def test_training_status_api():
    """测试训练状态API"""
    
    print("🧪 测试训练状态API...")
    
    # 查找最新的训练集
    training_sets = TrainingSet.objects.filter(name__icontains='模拟数据').order_by('-created_at')
    
    if not training_sets.exists():
        print("❌ 没有找到模拟数据的训练集")
        return
    
    training_set = training_sets.first()
    training_set_id = training_set.training_set_id
    
    print(f"📊 训练集ID: {training_set_id}")
    print(f"📊 当前轮数: {training_set.current_epoch}")
    print(f"📊 总轮数: {training_set.total_epochs}")
    
    # 测试API调用
    try:
        from django.test import Client
        client = Client()
        
        # 调用API
        response = client.get(f'/polls/api/training-status/{training_set_id}/')
        
        print(f"📊 API响应状态码: {response.status_code}")
        print(f"📊 API响应内容: {response.content.decode()}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                training_status = data.get('training_status', {})
                print(f"✅ API调用成功")
                print(f"📊 返回的当前轮数: {training_status.get('current_epoch')}")
                print(f"📊 返回的总轮数: {training_status.get('total_epochs')}")
                print(f"📊 返回的训练状态: {training_status.get('status')}")
            else:
                print(f"❌ API返回失败: {data.get('message')}")
        else:
            print(f"❌ API调用失败，状态码: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 测试API时出错: {e}")

if __name__ == "__main__":
    test_training_status_api() 
import sys
import django

# 设置Django环境
sys.path.append(os.path.join(os.path.dirname(__file__), 'multi'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from polls.models import TrainingSet

def test_training_status_api():
    """测试训练状态API"""
    
    print("🧪 测试训练状态API...")
    
    # 查找最新的训练集
    training_sets = TrainingSet.objects.filter(name__icontains='模拟数据').order_by('-created_at')
    
    if not training_sets.exists():
        print("❌ 没有找到模拟数据的训练集")
        return
    
    training_set = training_sets.first()
    training_set_id = training_set.training_set_id
    
    print(f"📊 训练集ID: {training_set_id}")
    print(f"📊 当前轮数: {training_set.current_epoch}")
    print(f"📊 总轮数: {training_set.total_epochs}")
    
    # 测试API调用
    try:
        from django.test import Client
        client = Client()
        
        # 调用API
        response = client.get(f'/polls/api/training-status/{training_set_id}/')
        
        print(f"📊 API响应状态码: {response.status_code}")
        print(f"📊 API响应内容: {response.content.decode()}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                training_status = data.get('training_status', {})
                print(f"✅ API调用成功")
                print(f"📊 返回的当前轮数: {training_status.get('current_epoch')}")
                print(f"📊 返回的总轮数: {training_status.get('total_epochs')}")
                print(f"📊 返回的训练状态: {training_status.get('status')}")
            else:
                print(f"❌ API返回失败: {data.get('message')}")
        else:
            print(f"❌ API调用失败，状态码: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 测试API时出错: {e}")

if __name__ == "__main__":
    test_training_status_api() 
 
 