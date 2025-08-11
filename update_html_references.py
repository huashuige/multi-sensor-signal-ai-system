#!/usr/bin/env python3
"""
更新HTML模板中的外部引用路径
"""

import os
import re
from pathlib import Path

def update_html_file(file_path):
    """更新单个HTML文件中的外部引用"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 替换外部引用为本地引用
        replacements = [
            # Tailwind CSS
            {
                'pattern': r'<script src="https://cdn\.tailwindcss\.com"></script>',
                'replacement': '{% load static %}\n    <link rel="stylesheet" href="{% static \'css/tailwind.min.css\' %}">'
            },
            # ECharts
            {
                'pattern': r'<script src="https://cdn\.jsdelivr\.net/npm/echarts@5\.4\.3/dist/echarts\.min\.js"></script>',
                'replacement': '{% load static %}\n    <script src="{% static \'js/echarts.min.js\' %}"></script>'
            },
            # Lucide Icons
            {
                'pattern': r'<script src="https://unpkg\.com/lucide@latest/dist/umd/lucide\.js"></script>',
                'replacement': '{% load static %}\n    <script src="{% static \'js/lucide.min.js\' %}"></script>'
            },
            # Google Fonts
            {
                'pattern': r'<link href="https://fonts\.googleapis\.com/css2\?family=Orbitron:wght@500&family=Roboto\+Mono:wght@300;500&display=swap"[\s\S]*?rel="stylesheet">',
                'replacement': '{% load static %}\n    <link rel="stylesheet" href="{% static \'css/google-fonts.css\' %}">'
            },
            # Google Fonts preconnect (可以保留，因为字体文件可能还是需要从Google加载)
            {
                'pattern': r'<link rel="preconnect" href="https://fonts\.googleapis\.com">',
                'replacement': '<!-- Google Fonts preconnect -->'
            },
            {
                'pattern': r'<link rel="preconnect" href="https://fonts\.gstatic\.com" crossorigin>',
                'replacement': '<!-- Google Fonts preconnect -->'
            }
        ]
        
        # 应用所有替换
        for replacement in replacements:
            content = re.sub(replacement['pattern'], replacement['replacement'], content)
        
        # 如果内容有变化，写入文件
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ 已更新: {file_path}")
            return True
        else:
            print(f"⏭️ 无需更新: {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ 更新失败: {file_path} - {str(e)}")
        return False

def main():
    """主函数"""
    # 查找所有HTML文件
    html_files = []
    
    # 搜索polls/templates目录下的所有HTML文件
    templates_dir = Path("polls/templates")
    if templates_dir.exists():
        for html_file in templates_dir.rglob("*.html"):
            html_files.append(html_file)
    
    print("🚀 开始更新HTML模板中的外部引用...")
    print("=" * 60)
    
    updated_count = 0
    total_count = len(html_files)
    
    for html_file in html_files:
        if update_html_file(html_file):
            updated_count += 1
    
    print("=" * 60)
    print(f"📊 更新完成: {updated_count}/{total_count} 个文件")
    
    if updated_count > 0:
        print("✅ HTML模板更新成功！")
        print("\n📝 接下来需要运行 collectstatic 命令")
    else:
        print("ℹ️ 没有文件需要更新")

if __name__ == "__main__":
    main() 