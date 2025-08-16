"""Download a matching chromedriver for the installed Chrome browser.

This script can be used by Selenium projects to automatically fetch a
chromedriver binary whose major version matches the locally installed Google
Chrome/Chromium browser.  The original version of this file was limited to
Windows machines.  It relied on ``win32com`` to inspect the installed Chrome
executable and always downloaded the Windows driver.  Running the script on
Linux therefore resulted in an ``ImportError`` or an inability to detect the
browser version.  The updated implementation adds Linux support while keeping
the original Windows behaviour.

The platform is detected at runtime and the correct download URL and driver
name are selected automatically.  Chrome's version is determined using
``win32com`` on Windows and by invoking ``google-chrome --version`` (or similar
commands) on Linux.
"""

from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
import zipfile

import requests
import wget

# ``win32com`` is only available on Windows.  Importing it on other platforms
# would raise an ImportError and break the script.  The import is therefore done
# lazily based on the current operating system.
if platform.system() == "Windows":  # pragma: no cover - platform specific
    from win32com.client import Dispatch

# Public JSON with download information for chromedriver builds
CHROME_VERSIONS_URL = (
    "https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json"
)


def _get_chrome_version_windows() -> str | None:
    """Return the full Chrome version on Windows using COM APIs."""

    parser = Dispatch("Scripting.FileSystemObject")
    paths = [
        r"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
        r"C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
    ]
    for path in paths:
        try:
            version = parser.GetFileVersion(path)
        except Exception:  # pragma: no cover - depends on local installation
            continue
        if version:
            return version
    return None


def _get_chrome_version_linux() -> str | None:
    """Return the full Chrome/Chromium version on Linux.

    The function tries a set of common Chrome/Chromium executable names and
    returns the version of the first one that can be executed.
    """

    commands = [
        "google-chrome",
        "google-chrome-stable",
        "chromium-browser",
        "chromium",
    ]
    for cmd in commands:
        try:
            result = subprocess.run(
                [cmd, "--version"],
                capture_output=True,
                text=True,
                check=True,
            )
        except (FileNotFoundError, subprocess.CalledProcessError):
            continue
        # Typical output: "Google Chrome 116.0.5845.96"
        version = result.stdout.strip().split()[-1]
        if version:
            return version
    return None


def _download_driver(major_version: str) -> None:
    """Download and extract the driver for the current platform."""

    jsondata = requests.get(CHROME_VERSIONS_URL)
    versions = json.loads(jsondata.text)["versions"]

    system = platform.system()
    if system == "Windows":
        target_platform = "win64"
        driver_name = "chromedriver.exe"
    else:
        target_platform = "linux64"
        driver_name = "chromedriver"

    download_url = None
    for item in versions:
        if item["version"].startswith(major_version):
            for download in item["downloads"]["chromedriver"]:
                if download["platform"] == target_platform:
                    download_url = download["url"]
                    break
            if download_url:
                break
    if not download_url:
        return

    latest_driver_zip = wget.download(download_url, "chromedriver.zip")
    with zipfile.ZipFile(latest_driver_zip, "r") as zip_ref:
        zip_ref.extractall()
    os.remove(latest_driver_zip)

    extracted_dir = f"chromedriver-{target_platform}"
    shutil.move(os.path.join(extracted_dir, driver_name), driver_name)

    if system != "Windows":
        # Ensure the binary is executable on Unix systems.
        os.chmod(driver_name, 0o755)


def getChromeDriver() -> None:
    """Ensure a matching chromedriver executable is present.

    The function determines the installed Chrome/Chromium version, downloads
    the corresponding driver for the current platform and places it in the
    current working directory.  If the driver already exists, nothing happens.
    """

    system = platform.system()
    driver_name = "chromedriver.exe" if system == "Windows" else "chromedriver"
    if driver_name in os.listdir():
        return

    if system == "Windows":
        version = _get_chrome_version_windows()
    else:
        version = _get_chrome_version_linux()

    if not version:
        raise FileNotFoundError("Google Chrome not found in default locations")

    major_version = version.split(".")[0]
    _download_driver(major_version)


if __name__ == "__main__":
    getChromeDriver()

