import os
import requests
import shutil
import time
from datetime import datetime

# 定义GitHub API的URL，用于获取最新版本信息
api_url = "https://api.github.com/repos/roflmuffin/CounterStrikeSharp/releases/latest"
download_dir = "CounterStrikeSharp_linux_releases"

# 确保下载目录存在
os.makedirs(download_dir, exist_ok=True)

def fetch_with_retry(url, max_retries=3, delay=60):
    """带重试机制的请求函数"""
    for attempt in range(max_retries):
        try:
            print(f"正在通过GitHub API获取最新版本信息... (第 {attempt + 1}/{max_retries} 次尝试)")
            
            # 添加User-Agent头部以避免被识别为机器人
            headers = {
                'User-Agent': 'CounterStrikeSharp-Downloader/1.0',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 403:
                # 检查是否是速率限制
                if 'rate limit' in response.text.lower():
                    if attempt < max_retries - 1:
                        print(f"API调用频率超限。等待 {delay} 秒后重试...")
                        time.sleep(delay)
                        continue
                    else:
                        print("API调用频率超限且已达到最大重试次数。")
                        return None
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.Timeout:
            print(f"第 {attempt + 1} 次请求超时")
            if attempt < max_retries - 1:
                time.sleep(5)
                continue
        except requests.exceptions.RequestException as e:
            print(f"第 {attempt + 1} 次请求失败: {e}")
            if attempt < max_retries - 1:
                time.sleep(5)
                continue
    
    return None

try:
    release_data = fetch_with_retry(api_url)
    
    if not release_data:
        print("所有重试后仍无法获取版本数据。")
        print("您可以稍后再试或手动访问仓库:")
        print("https://github.com/roflmuffin/CounterStrikeSharp/releases/latest")
        exit(1)

    # Find the download URL for the Linux version
    download_url = None
    filename = None
    
    # 遍历发布资产，寻找匹配的文件
    for asset in release_data['assets']:
        if "counterstrikesharp-with-runtime-linux-" in asset['name']:
            download_url = asset['browser_download_url']
            filename = asset['name']
            break
            
    if download_url:
        # 确保下载目录存在
        os.makedirs(download_dir, exist_ok=True)
        filepath = os.path.join(download_dir, filename)
        
        print(f"找到最新Linux版本: {filename}")
        print(f"下载地址: {download_url}")
        print(f"保存到: {filepath}")
        
        # Download the file with progress indication
        try:
            headers = {
                'User-Agent': 'CounterStrikeSharp-Downloader/1.0'
            }
            
            with requests.get(download_url, stream=True, headers=headers, timeout=300) as download_response:
                download_response.raise_for_status()
                
                # Get file size for progress tracking
                total_size = int(download_response.headers.get('content-length', 0))
                downloaded_size = 0
                
                with open(filepath, 'wb') as f:
                    for chunk in download_response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded_size += len(chunk)
                            
                            # Show progress
                            if total_size > 0:
                                progress = (downloaded_size / total_size) * 100
                                print(f"\r下载进度: {progress:.1f}% ({downloaded_size}/{total_size} 字节)", end='', flush=True)
                
                print(f"\n下载成功，保存到: {filepath}")
                print(f"文件大小: {downloaded_size} 字节")
                
        except requests.exceptions.RequestException as e:
            print(f"\n下载失败: {e}")
            # 清理部分下载的文件
            if os.path.exists(filepath):
                os.remove(filepath)
                print("已清理部分下载的文件。")
            raise
    else:
        print("在发布资源中找不到合适的最新Linux版本下载链接。")

except Exception as e:
    print(f"发生意外错误: {e}")
    print("您可以稍后再试或手动下载:")
    print("https://github.com/roflmuffin/CounterStrikeSharp/releases/latest")
