#!/usr/bin/env python3
"""
下载外部CSS和JS文件脚本
"""

import requests
import os

def download_file(url, local_path):
    """下载文件到本地"""
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        # 确保目录存在
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        
        # 写入文件
        with open(local_path, 'wb') as f:
            f.write(response.content)
        
        print(f"✅ 成功下载: {local_path}")
        return True
    except Exception as e:
        print(f"❌ 下载失败 {url}: {e}")
        return False

def main():
    # 定义要下载的文件
    files_to_download = [
        {
            'url': 'https://cdnjs.cloudflare.com/ajax/libs/tailwindcss/2.2.19/tailwind.min.css',
            'local_path': 'polls/static/css/tailwind.min.css'
        },
        {
            'url': 'https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js',
            'local_path': 'polls/static/js/echarts.min.js'
        },
        {
            'url': 'https://unpkg.com/lucide@latest/dist/umd/lucide.js',
            'local_path': 'polls/static/js/lucide.min.js'
        },
        {
            'url': 'https://fonts.googleapis.com/css2?family=Orbitron:wght@500&family=Roboto+Mono:wght@300;500&display=swap',
            'local_path': 'polls/static/css/google-fonts.css'
        }
    ]
    
    print("🚀 开始下载外部文件...")
    
    for file_info in files_to_download:
        download_file(file_info['url'], file_info['local_path'])
    
    print("✅ 下载完成！")

if __name__ == "__main__":
    main() 