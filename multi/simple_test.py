#!/usr/bin/env python
"""
简单的导入测试
"""

import os
import sys
import django

# 设置Django环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

def test_import():
    """测试导入"""
    try:
        # 测试导入
        from polls.models import MonitorTask
        print("✅ MonitorTask 导入成功")
        
        from polls import deep_learning_views
        print("✅ deep_learning_views 导入成功")
        
        print("🎉 导入测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        return False

if __name__ == "__main__":
    test_import() 
"""
简单的导入测试
"""

import os
import sys
import django

# 设置Django环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

def test_import():
    """测试导入"""
    try:
        # 测试导入
        from polls.models import MonitorTask
        print("✅ MonitorTask 导入成功")
        
        from polls import deep_learning_views
        print("✅ deep_learning_views 导入成功")
        
        print("🎉 导入测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        return False

if __name__ == "__main__":
    test_import() 
 
 