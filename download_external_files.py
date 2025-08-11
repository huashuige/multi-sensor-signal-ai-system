#!/usr/bin/env python3
"""
下载外部CSS和JS文件脚本
"""

import os
import requests
import urllib.parse
from pathlib import Path

def download_file(url, local_path):
    """下载文件到指定路径"""
    try:
        print(f"正在下载: {url}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # 确保目录存在
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        
        # 写入文件
        with open(local_path, 'wb') as f:
            f.write(response.content)
        
        print(f"✅ 下载完成: {local_path}")
        return True
    except Exception as e:
        print(f"❌ 下载失败: {url} - {str(e)}")
        return False

def main():
    """主函数"""
    # 创建静态文件目录
    static_dir = Path("polls/static")
    css_dir = static_dir / "css"
    js_dir = static_dir / "js"
    fonts_dir = static_dir / "fonts"
    
    # 确保目录存在
    css_dir.mkdir(parents=True, exist_ok=True)
    js_dir.mkdir(parents=True, exist_ok=True)
    fonts_dir.mkdir(parents=True, exist_ok=True)
    
    # 定义要下载的文件
    files_to_download = [
        # CSS文件
        {
            "url": "https://cdn.tailwindcss.com",
            "local_path": "polls/static/css/tailwind.min.css",
            "type": "CSS"
        },
        
        # JavaScript文件
        {
            "url": "https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js",
            "local_path": "polls/static/js/echarts.min.js",
            "type": "JS"
        },
        {
            "url": "https://unpkg.com/lucide@latest/dist/umd/lucide.js",
            "local_path": "polls/static/js/lucide.min.js",
            "type": "JS"
        },
        
        # Google Fonts CSS
        {
            "url": "https://fonts.googleapis.com/css2?family=Orbitron:wght@500&family=Roboto+Mono:wght@300;500&display=swap",
            "local_path": "polls/static/css/google-fonts.css",
            "type": "CSS"
        }
    ]
    
    print("🚀 开始下载外部文件...")
    print("=" * 50)
    
    success_count = 0
    total_count = len(files_to_download)
    
    for file_info in files_to_download:
        success = download_file(file_info["url"], file_info["local_path"])
        if success:
            success_count += 1
        print()
    
    print("=" * 50)
    print(f"📊 下载完成: {success_count}/{total_count} 个文件")
    
    if success_count == total_count:
        print("✅ 所有文件下载成功！")
        print("\n📝 接下来需要更新HTML模板中的引用路径")
    else:
        print("⚠️ 部分文件下载失败，请检查网络连接")

if __name__ == "__main__":
    main() 