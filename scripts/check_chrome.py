import os
import re
import subprocess

def get_chrome_version():
    paths = [
        r'C:\Program Files\Google\Chrome\Application\chrome.exe',
        r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
        os.path.expanduser('~') + r'\AppData\Local\Google\Chrome\Application\chrome.exe',
    ]
    
    for path in paths:
        if os.path.exists(path):
            try:
                cmd = 'wmic datafile where name="{}" get Version /value'.format(path.replace('\\', '\\\\'))
                info = subprocess.check_output(cmd, shell=True).decode()
                version = re.search(r'Version=(.+)', info)
                if version:
                    return version.group(1)
            except:
                continue
    
    return None

if __name__ == "__main__":
    version = get_chrome_version()
    if version:
        print(f"Chrome version: {version}")
    else:
        print("Could not determine Chrome version") 