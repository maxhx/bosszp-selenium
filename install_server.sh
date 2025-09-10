#!/bin/bash

# Boss直聘爬虫服务器环境安装脚本

echo "=== Boss直聘爬虫服务器环境安装 ==="

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then
    echo "请使用root权限运行此脚本: sudo $0"
    exit 1
fi

# 更新包管理器
echo "1. 更新包管理器..."
apt-get update

# 安装必要的系统依赖
echo "2. 安装系统依赖..."
apt-get install -y \
    wget \
    curl \
    unzip \
    xvfb \
    dbus-x11 \
    libgtk-3-0 \
    libx11-xcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxrandr2 \
    libxss1 \
    libxtst6 \
    libnss3 \
    libxss1 \
    libgconf-2-4

# 安装Firefox ESR
echo "3. 安装Firefox ESR..."
apt-get install -y firefox-esr

# 安装geckodriver
echo "4. 安装geckodriver..."
GECKODRIVER_VERSION="v0.33.0"
GECKODRIVER_URL="https://github.com/mozilla/geckodriver/releases/download/${GECKODRIVER_VERSION}/geckodriver-${GECKODRIVER_VERSION}-linux64.tar.gz"

cd /tmp
wget -O geckodriver.tar.gz "$GECKODRIVER_URL"
tar -xzf geckodriver.tar.gz
mv geckodriver /usr/local/bin/
chmod +x /usr/local/bin/geckodriver
rm geckodriver.tar.gz

# 验证安装
echo "5. 验证安装..."
echo "Firefox版本:"
firefox-esr --version

echo "geckodriver版本:"
geckodriver --version

# 安装Python依赖
echo "6. 安装Python依赖..."
pip3 install selenium mysql-connector-python

# 创建虚拟显示环境
echo "7. 配置虚拟显示环境..."
echo 'export DISPLAY=:99' >> /etc/environment

# 创建启动脚本
echo "8. 创建启动脚本..."
cat > /usr/local/bin/start-spider.sh << 'EOF'
#!/bin/bash
# 启动虚拟显示
Xvfb :99 -screen 0 1024x768x24 &
export DISPLAY=:99

# 等待Xvfb启动
sleep 2

# 运行爬虫
cd /root/app/bosszp-selenium-master
python3 boss_selenium_copy.py "$@"
EOF

chmod +x /usr/local/bin/start-spider.sh

echo "安装完成！"
echo ""
echo "使用方法:"
echo "1. 运行诊断: python3 diagnose_server.py"
echo "2. 启动爬虫: start-spider.sh"
echo "3. 指定环境: start-spider.sh testing"
