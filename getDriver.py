from win32com.client import Dispatch
import wget
import requests
import json
import zipfile
import os
import shutil

def get_version_via_com(filename):
    parser = Dispatch("Scripting.FileSystemObject")
    try:
        version = parser.GetFileVersion(filename)
    except Exception:
        return None
        
    jsondata = requests.get(
        "https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json"
    )
    jsonDic = json.loads(jsondata.text)
    versions = jsonDic['versions']

    # Only keep the major version (e.g. 116 from 116.0.5845.96)
    major_version = version.split(".")[0]

    download_url = None
    for item in versions:
        # Match the version by its major number
        if item["version"].startswith(major_version):
            # Find the Windows 64-bit download entry instead of assuming index 4
            for download in item["downloads"]["chromedriver"]:
                if download["platform"] == "win64":
                    download_url = download["url"]
                    break
            if download_url:
                break
    if not download_url:
        return None

    latest_driver_zip = wget.download(download_url,'chromedriver.zip')
    with zipfile.ZipFile(latest_driver_zip, 'r') as zip_ref:
        zip_ref.extractall() # you can specify the destination folder path here
    # delete the zip file downloaded above
    os.remove(latest_driver_zip)

    shutil.move("./chromedriver-win64/chromedriver.exe", "./chromedriver.exe")

    return major_version

def getChromeDriver():
    """Ensure a matching chromedriver is available.

    If ``chromedriver.exe`` is not present in the current directory, this
    function tries known Chrome installation paths and downloads the
    corresponding driver for the first path that exists.
    """

    if "chromedriver.exe" in os.listdir():
        return

    paths = [
        r"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
        r"C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
    ]
    for path in paths:
        version = get_version_via_com(path)
        if version:
            print(version)
            return

    raise FileNotFoundError("Google Chrome not found in default locations")

