import os
import urllib.request
import urllib.error
import zipfile
import ssl
import sys

def download_file(url, local_path):
    print(f"Downloading {url} to {local_path}")
    
    try:
        # 创建 SSL 上下文
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        # 下载文件
        with urllib.request.urlopen(url, context=ssl_context) as response:
            with open(local_path, 'wb') as f:
                while True:
                    chunk = response.read(8192)
                    if not chunk:
                        break
                    f.write(chunk)
    except urllib.error.URLError as e:
        print(f"Error downloading file: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

def main():
    try:
        # 创建 drivers 目录
        os.makedirs('drivers', exist_ok=True)
        
        # 下载 Chrome
        chrome_url = "https://storage.googleapis.com/chrome-for-testing-public/138.0.7204.92/win64/chrome-win64.zip"
        chrome_zip = "drivers/chrome-win64.zip"
        download_file(chrome_url, chrome_zip)
        
        # 解压 Chrome
        print(f"Extracting {chrome_zip}")
        with zipfile.ZipFile(chrome_zip, 'r') as zip_ref:
            zip_ref.extractall("drivers")
        
        print("Done!")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 