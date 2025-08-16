# getSuitableChromeDriver

`getDriver.py` automatically downloads a ChromeDriver binary that matches the installed Chrome/Chromium browser. It works on Windows and Linux, removing common version mismatch issues in Selenium projects.

## Usage

Run the script from the command line:

```bash
python getDriver.py
```

Or call it from Python code:

```python
from getDriver import getChromeDriver
getChromeDriver()
```

The appropriate `chromedriver` executable is saved to the current directory if it isn't already present.
