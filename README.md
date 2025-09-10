# Boss直聘爬虫 - 环境配置说明

## 环境配置

本项目支持多环境配置，通过JSON文件管理不同环境的MySQL数据库连接信息。

### 配置文件 (config.json)

```json
{
  "testing": {
    "host": "localhost",
    "user": "root",
    "password": "123456",
    "db": "spider_db_test",
    "port": 3306,
    "charset": "utf8mb4"
  },
  "production": {
    "host": "localhost",
    "user": "root",
    "password": "123456",
    "db": "spider_db",
    "port": 3306,
    "charset": "utf8mb4"
  },
  "development": {
    "host": "localhost",
    "user": "root",
    "password": "123456",
    "db": "spider_db_dev",
    "port": 3306,
    "charset": "utf8mb4"
  }
}
```

### 环境选择方式

#### 1. 命令行参数
```bash
# 使用测试环境
python boss_selenium_copy.py testing

# 使用生产环境
python boss_selenium_copy.py production

# 使用开发环境
python boss_selenium_copy.py development
```

#### 2. 环境变量
```bash
# Windows
set BOSS_ENV=testing
python boss_selenium_copy.py

# Linux/Mac
export BOSS_ENV=testing
python boss_selenium_copy.py
```

#### 3. 默认环境
如果不指定环境，默认使用 `production` 环境。

### 环境说明

- **testing**: 测试环境，使用测试数据库
- **production**: 生产环境，使用生产数据库
- **development**: 开发环境，使用开发数据库

### 注意事项

1. 确保配置文件 `config.json` 存在于脚本同目录下
2. 根据实际环境修改数据库连接信息
3. 确保对应环境的数据库已创建
4. Firefox浏览器路径会根据环境自动调整（生产环境使用指定路径）

### 数据库表结构

确保数据库中存在 `job_info` 表，包含以下字段：
- category (varchar)
- sub_category (varchar)
- job_title (varchar)
- province (varchar)
- job_location (varchar)
- job_company (varchar)
- job_industry (varchar)
- job_finance (varchar)
- job_scale (varchar)
- job_welfare (varchar)
- job_salary_range (varchar)
- job_experience (varchar)
- job_education (varchar)
- job_skills (varchar)
- create_time (date)

## 环境要求

- **Python版本**: 3.0+ (推荐3.6+)
- **操作系统**: Linux/Windows/macOS
- **浏览器**: Firefox
- **数据库**: MySQL

### 环境检查
运行环境检查脚本：
```bash
python check_env.py
```

## 安装依赖

### 自动安装（推荐）
```bash
chmod +x install.sh
./install.sh
```

### 手动安装
```bash
# 安装Python依赖
pip install -r requirements.txt

# 安装Firefox浏览器（Ubuntu/Debian）
sudo apt-get install firefox-esr

# 安装geckodriver
wget https://github.com/mozilla/geckodriver/releases/download/v0.33.0/geckodriver-v0.33.0-linux64.tar.gz
tar -xzf geckodriver-v0.33.0-linux64.tar.gz
sudo mv geckodriver /usr/local/bin/
sudo chmod +x /usr/local/bin/geckodriver
```

## 故障排除

### 1. Python版本兼容性问题
如果遇到 `SyntaxError: invalid syntax` 错误，可能是Python版本过低：

**解决方案：**
- 检查Python版本：`python --version`
- 运行环境检查：`python check_env.py`
- 升级到Python 3.6+：`sudo apt-get install python3.6`

### 2. WebDriverException错误
如果遇到 `selenium.common.exceptions.WebDriverException` 错误：

**解决方案：**
- 确保已安装Firefox浏览器：`firefox --version`
- 确保geckodriver在PATH中：`geckodriver --version`
- 检查Firefox路径是否正确

### 3. pytest测试失败
如果pytest报错，现在代码已经重构，不会在导入时启动浏览器。

**运行测试：**
```bash
# 运行所有测试
pytest -v

# 运行特定测试文件
pytest test_boss_spider.py -v

# 运行主文件（现在不会报错）
pytest boss_selenium_copy.py -v
```

**测试内容：**
- 配置文件加载测试
- 数据库配置验证
- 城市映射测试
- 浏览器创建函数测试
- 环境变量验证

### 4. 无头模式问题
代码默认使用无头模式运行，适合服务器环境。如果需要GUI模式，可以修改 `create_browser()` 函数中的 `--headless` 参数。

### 5. 数据库连接问题
确保：
- MySQL服务正在运行
- 数据库用户有足够权限
- 配置文件中的连接信息正确

### 6. 服务器环境问题
如果在服务器环境中遇到浏览器启动问题：

**诊断工具：**
```bash
# 运行服务器环境诊断
python3 diagnose_server.py

# 仅测试浏览器创建
python3 boss_selenium_copy.py test
```

**常见解决方案：**
1. 安装虚拟显示：`apt-get install xvfb`
2. 启动虚拟显示：`Xvfb :99 -screen 0 1024x768x24 &`
3. 设置显示环境：`export DISPLAY=:99`
4. 使用服务器安装脚本：`chmod +x install_server.sh && ./install_server.sh`

**调试模式：**
在代码中设置 `DEBUG_MODE = True` 可以禁用无头模式，便于调试。

### 7. Ubuntu服务器环境问题
如果在Ubuntu服务器上Firefox启动卡住：

**快速修复：**
```bash
# 运行快速修复脚本
chmod +x fix_ubuntu.sh
./fix_ubuntu.sh

# 然后运行爬虫
python3 boss_selenium_copy.py
```

**手动修复：**
```bash
# 1. 安装虚拟显示
apt-get install xvfb

# 2. 启动虚拟显示
Xvfb :99 -screen 0 1024x768x24 -ac +extension GLX +render -noreset &

# 3. 设置显示环境
export DISPLAY=:99

# 4. 运行爬虫
python3 boss_selenium_copy.py
```

**完整解决方案：**
```bash
# 使用完整的Ubuntu启动脚本
chmod +x start_ubuntu.sh
./start_ubuntu.sh
```

### 8. Ubuntu Firefox启动卡住问题
如果Firefox启动时卡住不动：

**一键解决方案（推荐）：**
```bash
# 运行一键设置脚本
chmod +x setup_display.sh
./setup_display.sh

# 然后运行爬虫
python3 boss_selenium_copy.py
```

**Python脚本解决方案：**
```bash
# 使用Python脚本设置
python3 setup_ubuntu_display.py

# 然后运行爬虫
python3 boss_selenium_copy.py
```

**问题原因：**
Ubuntu服务器环境缺少虚拟显示环境，Firefox无法启动图形界面。