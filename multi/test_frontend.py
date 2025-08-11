import os
import sys
import django

# 设置Django环境
sys.path.append(os.path.join(os.path.dirname(__file__), 'multi'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from polls.models import TrainingSet

def test_frontend_fix():
    """测试前端修复"""
    
    print("🧪 测试前端修复...")
    
    # 查找最新的训练集
    training_sets = TrainingSet.objects.filter(name__icontains='模拟数据').order_by('-created_at')
    
    if not training_sets.exists():
        print("❌ 没有找到模拟数据的训练集")
        return
    
    training_set = training_sets.first()
    training_set_id = training_set.training_set_id
    
    print(f"📊 训练集: {training_set.name}")
    print(f"📊 训练集ID: {training_set_id}")
    print(f"📊 当前轮数: {training_set.current_epoch}")
    print(f"📊 总轮数: {training_set.total_epochs}")
    print(f"📊 训练状态: {training_set.training_status}")
    
    # 生成训练监控页面URL
    monitor_url = f"/polls/training-monitor/?id={training_set_id}"
    
    print(f"\n📊 训练监控页面URL:")
    print(f"   {monitor_url}")
    
    print(f"\n💡 现在可以访问训练监控页面:")
    print(f"1. 打开浏览器")
    print(f"2. 访问: http://localhost:8000{monitor_url}")
    print(f"3. 打开浏览器开发者工具查看控制台日志")
    print(f"4. 检查训练进度是否正确显示")
    
    # 检查API是否正常工作
    print(f"\n🔍 检查API状态...")
    
    try:
        from django.test import Client
        client = Client()
        
        # 测试训练状态API
        response = client.get(f'/polls/api/training-status/{training_set_id}/')
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                training_status = data.get('training_status', {})
                print(f"✅ API正常工作")
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
    test_frontend_fix() 
import sys
import django

# 设置Django环境
sys.path.append(os.path.join(os.path.dirname(__file__), 'multi'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from polls.models import TrainingSet

def test_frontend_fix():
    """测试前端修复"""
    
    print("🧪 测试前端修复...")
    
    # 查找最新的训练集
    training_sets = TrainingSet.objects.filter(name__icontains='模拟数据').order_by('-created_at')
    
    if not training_sets.exists():
        print("❌ 没有找到模拟数据的训练集")
        return
    
    training_set = training_sets.first()
    training_set_id = training_set.training_set_id
    
    print(f"📊 训练集: {training_set.name}")
    print(f"📊 训练集ID: {training_set_id}")
    print(f"📊 当前轮数: {training_set.current_epoch}")
    print(f"📊 总轮数: {training_set.total_epochs}")
    print(f"📊 训练状态: {training_set.training_status}")
    
    # 生成训练监控页面URL
    monitor_url = f"/polls/training-monitor/?id={training_set_id}"
    
    print(f"\n📊 训练监控页面URL:")
    print(f"   {monitor_url}")
    
    print(f"\n💡 现在可以访问训练监控页面:")
    print(f"1. 打开浏览器")
    print(f"2. 访问: http://localhost:8000{monitor_url}")
    print(f"3. 打开浏览器开发者工具查看控制台日志")
    print(f"4. 检查训练进度是否正确显示")
    
    # 检查API是否正常工作
    print(f"\n🔍 检查API状态...")
    
    try:
        from django.test import Client
        client = Client()
        
        # 测试训练状态API
        response = client.get(f'/polls/api/training-status/{training_set_id}/')
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                training_status = data.get('training_status', {})
                print(f"✅ API正常工作")
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
    test_frontend_fix() 
 
 