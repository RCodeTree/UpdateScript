import os
import requests
import shutil

# GitHub API endpoint for the latest release
api_url = "https://api.github.com/repos/roflmuffin/CounterStrikeSharp/releases/latest"
download_dir = "CounterStrikeSharp_linux_releases"

# Create download directory if it doesn't exist
os.makedirs(download_dir, exist_ok=True)

try:
    print("Fetching latest release information via GitHub API...")
    response = requests.get(api_url)
    response.raise_for_status()  # 检查请求是否成功
    release_data = response.json()

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
        filepath = os.path.join(download_dir, filename)
        
        print(f"Found latest Linux release: {filename}")
        print(f"Downloading from: {download_url}")
        
        # Download the file
        with requests.get(download_url, stream=True) as download_response:
            download_response.raise_for_status()
            with open(filepath, 'wb') as f:
                shutil.copyfileobj(download_response.raw, f)
                
        print(f"Successfully downloaded to: {filepath}")
    else:
        print("Could not find a suitable download link for the latest Linux version in the release assets.")

except requests.exceptions.RequestException as e:
    print(f"An error occurred while fetching the URL: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
