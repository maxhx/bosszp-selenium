#!/bin/bash

# Firefox和geckodriver版本检查脚本

echo "=== Firefox和geckodriver版本检查 ==="

# 检查Firefox版本
echo "1. 检查Firefox版本:"
if command -v firefox &> /dev/null; then
    firefox --version
else
    echo "❌ Firefox未安装或不在PATH中"
fi

if command -v firefox-esr &> /dev/null; then
    echo "Firefox ESR版本:"
    firefox-esr --version
fi

echo ""

# 检查geckodriver版本
echo "2. 检查geckodriver版本:"
if command -v geckodriver &> /dev/null; then
    geckodriver --version
else
    echo "❌ geckodriver未安装或不在PATH中"
fi

echo ""

# 检查Selenium版本
echo "3. 检查Selenium版本:"
python3 -c "import selenium; print('Selenium版本:', selenium.__version__)"

echo ""

# 检查兼容性
echo "4. 兼容性建议:"
echo "- Firefox 91+ 需要 geckodriver 0.30.0+"
echo "- Firefox 102+ 需要 geckodriver 0.32.0+"
echo "- Firefox 115+ 需要 geckodriver 0.33.0+"

echo ""
echo "如果版本不兼容，请运行:"
echo "wget https://github.com/mozilla/geckodriver/releases/download/v0.33.0/geckodriver-v0.33.0-linux64.tar.gz"
echo "tar -xzf geckodriver-v0.33.0-linux64.tar.gz"
echo "sudo mv geckodriver /usr/local/bin/"
echo "sudo chmod +x /usr/local/bin/geckodriver"
