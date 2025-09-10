#!/bin/bash

# Boss直聘爬虫安装脚本

echo "开始安装Boss直聘爬虫依赖..."

# 更新包管理器
echo "更新包管理器..."
apt-get update

# 安装Firefox浏览器
echo "安装Firefox浏览器..."
apt-get install -y firefox-esr

# 安装geckodriver
echo "安装geckodriver..."
wget https://github.com/mozilla/geckodriver/releases/download/v0.33.0/geckodriver-v0.33.0-linux64.tar.gz
tar -xzf geckodriver-v0.33.0-linux64.tar.gz
mv geckodriver /usr/local/bin/
chmod +x /usr/local/bin/geckodriver
rm geckodriver-v0.33.0-linux64.tar.gz

# 安装Python依赖
echo "安装Python依赖..."
pip install selenium mysql-connector-python

# 创建必要的目录
echo "创建必要的目录..."
mkdir -p /var/log/boss_spider

echo "安装完成！"
echo "使用方法："
echo "1. 修改config.json配置文件"
echo "2. 运行: python boss_selenium_copy.py"
echo "3. 或者指定环境: python boss_selenium_copy.py testing"
