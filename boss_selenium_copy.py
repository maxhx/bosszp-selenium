#!/usr/bin/python
# -*- coding:utf-8 -*-
# @author  : jhzhong
# @time    : 2023/12/22 8:23
# @function: the script is used to do something.
# @version : V1
import datetime
import time
import json
import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from selenium import webdriver
from selenium.webdriver.common.by import By
from dbutils import DBUtils
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options

# 配置环境
ENVIRONMENT = 'production'  # 改成 'testing' 或 'production' 即可
DEBUG_MODE = False  # 设置为True启用调试模式

# 配置日志系统
def setup_logging():
    """设置日志系统"""
    # 创建日志目录
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, mode=0o755)  # Linux权限：rwxr-xr-x
    
    # 设置日志格式
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # 配置根日志器
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG if DEBUG_MODE else logging.INFO)
    
    # 清除已有的处理器
    logger.handlers.clear()
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(log_format, date_format)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # 文件处理器 - 所有日志
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, 'boss_spider.log'),
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(log_format, date_format)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # 错误日志文件处理器
    error_handler = RotatingFileHandler(
        os.path.join(log_dir, 'boss_spider_error.log'),
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_formatter)
    logger.addHandler(error_handler)
    
    # 爬虫专用日志文件
    spider_handler = RotatingFileHandler(
        os.path.join(log_dir, 'spider_data.log'),
        maxBytes=20*1024*1024,  # 20MB
        backupCount=10,
        encoding='utf-8'
    )
    spider_handler.setLevel(logging.INFO)
    spider_formatter = logging.Formatter('%(asctime)s - %(message)s', date_format)
    spider_handler.setFormatter(spider_formatter)
    
    # 创建爬虫专用日志器
    spider_logger = logging.getLogger('spider')
    spider_logger.setLevel(logging.INFO)
    spider_logger.addHandler(spider_handler)
    spider_logger.propagate = False  # 不传播到根日志器
    
    return logger

# 初始化日志系统
logger = setup_logging()

def set_log_file_permissions():
    """设置日志文件权限（Linux环境）"""
    try:
        import stat
        log_dir = 'logs'
        if os.path.exists(log_dir):
            # 设置日志目录权限
            os.chmod(log_dir, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)  # 755
            
            # 设置日志文件权限
            log_files = ['boss_spider.log', 'boss_spider_error.log', 'spider_data.log']
            for log_file in log_files:
                log_path = os.path.join(log_dir, log_file)
                if os.path.exists(log_path):
                    os.chmod(log_path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)  # 644
            logger.debug("日志文件权限设置完成")
    except Exception as e:
        logger.warning("设置日志文件权限失败: {}".format(e))

# 设置日志文件权限
set_log_file_permissions()

# 读取配置文件
def load_config():
    """加载配置文件"""
    try:
        with open('config.json', 'r') as f:
            configs = json.load(f)
        logger.info("配置文件加载成功，当前环境: {}".format(ENVIRONMENT))
        return configs.get(ENVIRONMENT)
    except FileNotFoundError:
        logger.warning("config.json文件未找到")
        return None
    except Exception as e:
        logger.error("配置文件加载失败: {}".format(e))
        return None

# 延迟加载配置，避免在导入时出错
db_config = None

# 连接数据库
# db = DBUtils(**db_config)    

def create_browser():
    """创建Firefox浏览器实例"""
    logger.info("正在创建Firefox浏览器实例...")
    
    try:
        options = Options()
        
        # 服务器环境优化选项
        if not DEBUG_MODE:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-plugins')
        if not DEBUG_MODE:
            options.add_argument('--disable-images')
            # 重要：不禁用JavaScript，Boss直聘需要JS
            # options.add_argument('--disable-javascript')  # 注释掉这行
        options.add_argument('--disable-web-security')
        options.add_argument('--disable-features=VizDisplayCompositor')
        
        # 设置超时和窗口大小
        options.add_argument('--timeout=30')
        options.add_argument('--window-size=1920,1080')
        
        # 尝试不同的Firefox路径
        firefox_paths = [
            "/usr/bin/firefox",
            "/usr/bin/firefox-esr", 
            "/snap/bin/firefox",
            "/opt/firefox/firefox",
            "/usr/local/bin/firefox"
        ]
        
        firefox_found = False
        for path in firefox_paths:
            if os.path.exists(path) and os.access(path, os.X_OK):
                logger.info("找到可执行的Firefox: {}".format(path))
                options.binary_location = path
                firefox_found = True
                break
        
        if not firefox_found:
            logger.warning("未找到可执行的Firefox浏览器，使用默认路径")
        
        # 检查geckodriver
        geckodriver_paths = [
            "/usr/local/bin/geckodriver",
            "/usr/bin/geckodriver",
            "/snap/bin/geckodriver"
        ]
        
        geckodriver_found = False
        geckodriver_path = None
        for path in geckodriver_paths:
            if os.path.exists(path) and os.access(path, os.X_OK):
                logger.info("找到可执行的geckodriver: {}".format(path))
                geckodriver_found = True
                geckodriver_path = path
                break
        
        if not geckodriver_found:
            logger.error("未找到可执行的geckodriver")
            logger.error("请运行: chmod +x update_geckodriver.sh && ./update_geckodriver.sh")
            logger.error("或手动安装: wget https://github.com/mozilla/geckodriver/releases/download/v0.33.0/geckodriver-v0.33.0-linux64.tar.gz")
            logger.error("解压后: chmod +x geckodriver && mv geckodriver /usr/local/bin/")
            return None
        
        # 测试geckodriver版本
        try:
            import subprocess
            result = subprocess.run([geckodriver_path, '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                logger.info("geckodriver版本: {}".format(result.stdout.strip()))
            else:
                logger.warning("geckodriver版本检查失败")
        except Exception as e:
            logger.warning("geckodriver版本检查出错: {}".format(e))
        
        # 检查虚拟显示环境
        display = os.environ.get('DISPLAY')
        if not display:
            logger.warning("未设置DISPLAY环境变量")
            logger.warning("建议运行: export DISPLAY=:99")
            logger.warning("或使用启动脚本: chmod +x start_ubuntu.sh && ./start_ubuntu.sh")
        
        logger.info("正在启动Firefox浏览器...")
        
        # 检查是否在Ubuntu服务器环境
        if os.path.exists('/etc/os-release'):
            with open('/etc/os-release', 'r') as f:
                os_info = f.read()
                if 'ubuntu' in os_info.lower():
                    logger.info("检测到Ubuntu环境，检查虚拟显示...")
                    display = os.environ.get('DISPLAY')
                    if not display:
                        logger.error("未设置DISPLAY环境变量")
                        logger.error("解决方案:")
                        logger.error("1. 使用xvfb-run: xvfb-run -a python3 boss_selenium_copy.py")
                        logger.error("2. 手动设置虚拟显示:")
                        logger.error("   apt-get install xvfb")
                        logger.error("   Xvfb :99 -screen 0 1024x768x24 -ac +extension GLX +render -noreset &")
                        logger.error("   export DISPLAY=:99")
                        logger.error("3. 使用提供的启动脚本: chmod +x run_with_xvfb.sh && ./run_with_xvfb.sh")
                        return None
                    else:
                        logger.info("DISPLAY环境变量已设置: {}".format(display))
        
        logger.info("正在启动Firefox浏览器...")
        browser = webdriver.Firefox(options=options)
        logger.info("Firefox浏览器启动成功!")
        return browser
        
    except Exception as e:
        logger.error("创建浏览器失败: {}".format(e))
        logger.error("详细错误信息:")
        logger.exception("异常堆栈:")
        logger.error("可能的解决方案:")
        logger.error("1. 安装Firefox: apt-get install firefox-esr")
        logger.error("2. 安装geckodriver: wget https://github.com/mozilla/geckodriver/releases/download/v0.33.0/geckodriver-v0.33.0-linux64.tar.gz")
        logger.error("3. 检查权限: chmod +x /usr/local/bin/geckodriver")
        logger.error("4. 使用xvfb-run: xvfb-run -a python3 boss_selenium_copy.py")
        logger.error("5. 使用启动脚本: chmod +x run_with_xvfb.sh && ./run_with_xvfb.sh")
        return None

city_map = {
    "北京": ["北京"],
    "天津": ["天津"],
    "山西": ["太原", "阳泉", "晋城", "长治", "临汾", "运城", "忻州", "吕梁", "晋中", "大同", "朔州"],
    "河北": ["沧州", "石家庄", "唐山", "保定", "廊坊", "衡水", "邯郸", "邢台", "张家口", "辛集", "秦皇岛", "定州",
             "承德", "涿州"],
    "山东": ["济南", "淄博", "聊城", "德州", "滨州", "济宁", "菏泽", "枣庄", "烟台", "威海", "泰安", "青岛", "临沂",
             "莱芜", "东营", "潍坊", "日照"],
    "河南": ["郑州", "新乡", "鹤壁", "安阳", "焦作", "濮阳", "开封", "驻马店", "商丘", "三门峡", "南阳", "洛阳", "周口",
             "许昌", "信阳", "漯河", "平顶山", "济源"],
    "广东": ["珠海", "中山", "肇庆", "深圳", "清远", "揭阳", "江门", "惠州", "河源", "广州", "佛山", "东莞", "潮州",
             "汕尾", "梅州", "阳江", "云浮", "韶关", "湛江", "汕头", "茂名"],
    "浙江": ["舟山", "温州", "台州", "绍兴", "衢州", "宁波", "丽水", "金华", "嘉兴", "湖州", "杭州"],
    "宁夏": ["中卫", "银川", "吴忠", "石嘴山", "固原"],
    "江苏": ["镇江", "扬州", "盐城", "徐州", "宿迁", "无锡", "苏州", "南通", "南京", "连云港", "淮安", "常州", "泰州"],
    "湖南": ["长沙", "邵阳", "怀化", "株洲", "张家界", "永州", "益阳", "湘西", "娄底", "衡阳", "郴州", "岳阳", "常德",
             "湘潭"],
    "吉林": ["长春", "长春", "通化", "松原", "四平", "辽源", "吉林", "延边", "白山", "白城"],
    "福建": ["漳州", "厦门", "福州", "三明", "莆田", "宁德", "南平", "龙岩", "泉州"],
    "甘肃": ["张掖", "陇南", "兰州", "嘉峪关", "白银", "武威", "天水", "庆阳", "平凉", "临夏", "酒泉", "金昌", "甘南",
             "定西"],
    "陕西": ["榆林", "西安", "延安", "咸阳", "渭南", "铜川", "商洛", "汉中", "宝鸡", "安康"],
    "辽宁": ["营口", "铁岭", "沈阳", "盘锦", "辽阳", "锦州", "葫芦岛", "阜新", "抚顺", "丹东", "大连", "朝阳", "本溪",
             "鞍山"],
    "江西": ["鹰潭", "宜春", "上饶", "萍乡", "南昌", "景德镇", "吉安", "抚州", "新余", "九江", "赣州"],
    "黑龙江": ["伊春", "七台河", "牡丹江", "鸡西", "黑河", "鹤岗", "哈尔滨", "大兴安岭", "绥化", "双鸭山", "齐齐哈尔",
               "佳木斯", "大庆"],
    "安徽": ["宣城", "铜陵", "六安", "黄山", "淮南", "合肥", "阜阳", "亳州", "安庆", "池州", "宿州", "芜湖", "马鞍山",
             "淮北", "滁州", "蚌埠"],
    "湖北": ["孝感", "武汉", "十堰", "荆门", "黄冈", "襄阳", "咸宁", "随州", "黄石", "恩施", "鄂州", "荆州", "宜昌",
             "潜江", "天门", "神农架", "仙桃"],
    "青海": ["西宁", "海西", "海东", "玉树", "黄南", "海南", "海北", "果洛"],
    "新疆": ["乌鲁木齐", "克州", "阿勒泰", "五家渠", "石河子", "伊犁", "吐鲁番", "塔城", "克拉玛依", "喀什", "和田",
             "哈密", "昌吉", "博尔塔拉", "阿克苏", "巴音郭楞", "阿拉尔", "图木舒克", "铁门关"],
    "贵州": ["铜仁", "黔东南", "贵阳", "安顺", "遵义", "黔西南", "黔南", "六盘水", "毕节"],
    "四川": ["遂宁", "攀枝花", "眉山", "凉山", "成都", "巴中", "广安", "自贡", "甘孜", "资阳", "宜宾", "雅安", "内江",
             "南充", "绵阳", "泸州", "凉山", "乐山", "广元", "甘孜", "德阳", "达州", "阿坝"],
    "上海": ["上海"],
    "广西": ["南宁", "贵港", "玉林", "梧州", "钦州", "柳州", "来宾", "贺州", "河池", "桂林", "防城港", "崇左", "北海",
             "百色"],
    "西藏": ["拉萨", "山南", "日喀则", "那曲", "林芝", "昌都", "阿里"],
    "云南": ["昆明", "红河", "大理", "玉溪", "昭通", "西双版纳", "文山", "曲靖", "普洱", "怒江", "临沧", "丽江", "红河",
             "迪庆", "德宏", "大理", "楚雄", "保山"],
    "内蒙古": ["呼和浩特", "乌兰察布", "兴安", "赤峰", "呼伦贝尔", "锡林郭勒", "乌海", "通辽", "巴彦淖尔", "阿拉善",
               "鄂尔多斯", "包头"],
    "海南": ["海口", "三沙", "三亚", "临高", "五指山", "陵水", "文昌", "万宁", "白沙", "乐东", "澄迈", "屯昌", "定安",
             "东方", "保亭", "琼中", "琼海", "儋州", "昌江"],
    "重庆": ["重庆"]
}

def main():
    """主函数"""
    logger.info("=== Boss直聘爬虫开始运行 ===")
    
    # 加载配置
    global db_config
    db_config = load_config()
    if not db_config:
        logger.error("无法加载数据库配置，程序退出")
        return
    
    # 创建浏览器实例
    browser = create_browser()
    if not browser:
        logger.error("无法创建浏览器实例，程序退出")
        return
    
    try:
        # 打开 boss 首页
        index_url = 'https://www.zhipin.com/guangzhou/?ka=city-sites-101280100'
        logger.info("正在访问Boss直聘首页: {}".format(index_url))
        browser.get(index_url)

        # 模拟点击 互联网/AI 展示出岗位分类
        logger.info("正在点击互联网/AI分类...")
        show_ele = browser.find_element(by=By.XPATH, value='//*[@id="main"]/div/div[1]/div/div[1]/dl[1]/dd/b')
        show_ele.click()

        today = datetime.date.today().strftime('%Y-%m-%d')
        logger.info("开始抓取职位数据，日期: {}".format(today))
        
        # 获取爬虫专用日志器
        spider_logger = logging.getLogger('spider')
        
        for i in range(85):
            current_a = browser.find_elements(by=By.XPATH, value='//*[@id="main"]/div/div[1]/div/div[1]/dl[1]/div/ul/li/div/a')[i]
            current_category = '后端开发'
            sub_category = current_a.accessible_name 

            # 只抓取java或python相关岗位
            if not (('java' in sub_category.lower()) or ('python' in sub_category.lower()) or ('rpa' in sub_category.lower()) or ('运维工程师' in sub_category)):
                logger.debug("跳过非目标岗位: {}".format(sub_category))
                continue

            logger.info("正在抓取{}--{}".format(current_category, sub_category))
            spider_logger.info("开始抓取: {} - {}".format(current_category, sub_category))
            browser.find_elements(by=By.XPATH, value='//*[@id="main"]/div/div[1]/div/div[1]/dl[1]/div/ul/li/div/a')[i].click()
            
            # 等待页面加载完成
            logger.debug("等待页面加载完成...")
            WebDriverWait(browser, 10).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            # 再判断 document.body 是否存在
            WebDriverWait(browser, 10).until(
                lambda d: d.execute_script("return document.body != null")
            )
            # 模拟滑动页面
            logger.debug("模拟滑动页面...")
            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(10)
            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            job_detail = browser.find_elements(by=By.XPATH,
                                               value='/html/body/div[1]/div[2]/div[3]/div/div/div[1]/ul/div')
            logger.info("找到{}个职位信息".format(len(job_detail)))
            for job in job_detail:
                # 获取数据库连接
                try:
                    db = DBUtils(
                        host=db_config["host"],
                        user=db_config["user"],
                        password=db_config["password"],
                        db=db_config["db"]
                    )
                except Exception as e:
                    logger.error("数据库连接失败: {}".format(e))
                    continue
                # 岗位名称
                try:
                   job_title = job.find_element(by=By.XPATH, value="./div/li/div[1]/div/a").text.strip()
                except Exception as e:
                    logger.debug("获取岗位名称失败: {}".format(e))
                    continue
                try:
                    # 融资情况
                    job_finance = job.find_element(by=By.XPATH, value="./div[1]/div/div[2]/ul/li[2]").text.strip()
                except Exception as e:
                    logger.debug("获取融资情况失败: {}".format(e))
                    job_finance = '无'
                try:
                    # 企业规模
                    job_scale = job.find_element(by=By.XPATH, value="./div[1]/div/div[2]/ul/li[3]").text.strip()
                except Exception as e:
                    logger.debug("获取企业规模失败: {}".format(e))
                    job_scale = "无"
                try:
                    # 企业福利
                    job_welfare = job.find_element(by=By.XPATH, value="./div[2]/div").text.strip()
                except Exception as e:
                    logger.debug("获取企业福利失败: {}".format(e))
                    job_welfare = '无'
                try:
                    # 薪资范围
                    job_salary_range = job.find_element(by=By.XPATH, value="./div/li/div[1]/div/span").text.strip()
                except Exception as e:
                    logger.debug("获取薪资范围失败: {}".format(e))
                    job_salary_range = '无'
                try:
                    # 工作年限
                    job_experience = job.find_element(by=By.XPATH, value="./div/li/div[1]/ul/li[1]").text.strip()
                except Exception as e:
                    logger.debug("获取工作年限失败: {}".format(e))
                    job_experience = '无'
                try:
                    # 学历要求
                    job_education = job.find_element(by=By.XPATH, value="./div/li/div[1]/ul/li[2]").text.strip()
                except Exception as e:
                    logger.debug("获取学历要求失败: {}".format(e))
                    job_education = '无'
                # 技能要求
                try:
                    job_skills = ','.join(
                        [skill.text.strip() for skill in job.find_elements(by=By.XPATH, value="./div[2]/ul/li")])
                except Exception as e:
                    logger.debug("获取技能要求失败: {}".format(e))
                    job_skills = '无'
                try:
                    # 行业类型
                    job_industry = job.find_element(by=By.XPATH, value="./div[1]/div/div[2]/ul/li[1]").text.strip()
                except Exception as e:
                    logger.debug("获取行业类型失败: {}".format(e))
                    job_industry = '无'       
                try:
                    # 企业名称
                    job_company = job.find_element(By.XPATH, './/span[@class="boss-name"]').text.strip()
                except Exception as e:
                    logger.debug("获取企业名称失败: {}".format(e))
                    job_company = '无'
                 # 工作地址
                try:
                    job_location = job.find_element(By.XPATH, './/span[@class="company-location"]').text.strip()
                except Exception as e:
                    logger.debug("获取工作地址失败: {}".format(e))
                    job_location = '无'    
              
                province = ''
                city = job_location.split('·')[0]
                for p, cities in city_map.items():
                    if city in cities:
                        province = p
                        break
                
                # 记录抓取到的职位信息
                logger.info("抓取到职位: {} - {} - {}".format(job_title, job_company, job_location))
                spider_logger.info("职位信息: {}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}".format(
                    current_category, sub_category, job_title, province, job_location, job_company, job_industry,
                    job_finance, job_scale, job_welfare, job_salary_range, job_experience, job_education, job_skills, today))
                
                # 保存到 MySQL 数据库
                try:
                    # 先查重
                    check_sql = "SELECT 1 FROM job_info WHERE job_title=%s AND job_company=%s AND job_location=%s"
                    if not db.select_one(check_sql, (job_title, job_company, job_location)):
                        db.insert_data(
                            "insert into job_info(category, sub_category,job_title,province,job_location,job_company,job_industry,job_finance,job_scale,job_welfare,job_salary_range,job_experience,job_education,job_skills,create_time) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                            args=(
                                current_category, sub_category, job_title, province, job_location, job_company, job_industry,
                                job_finance,
                                job_scale, job_welfare, job_salary_range, job_experience, job_education, job_skills, today))
                        logger.info("成功保存职位: {} - {}".format(job_title, job_company))
                    else:
                        logger.debug("职位已存在，跳过: {} - {}".format(job_title, job_company))
                except Exception as e:
                    logger.error("保存职位到数据库失败: {}".format(e))
                finally:
                    db.close()
            try:
                # 退回到首页
                logger.debug("返回首页...")
                browser.back()
                # 模拟点击 互联网/AI 展示出岗位分类
                show_ele = browser.find_element(by=By.XPATH, value='//*[@id="main"]/div/div[1]/div/div[1]/dl[1]/dd/b')
                show_ele.click()
            except Exception as e:
                logger.warning("返回首页失败，重新访问: {}".format(e))
                browser.get(index_url)
                # 模拟点击 互联网/AI 展示出岗位分类
                show_ele = browser.find_element(by=By.XPATH, value='//*[@id="main"]/div/div[1]/div/div[1]/dl[1]/dd/b')
                show_ele.click()
        logger.info("=== Boss直聘爬虫运行完成 ===")
        time.sleep(10)
    except Exception as e:
        logger.error("爬虫运行出错: {}".format(e))
        logger.exception("详细错误信息:")  # 记录完整的异常堆栈
    finally:
        if browser:
            logger.info("正在关闭浏览器...")
            browser.quit()
            logger.info("浏览器已关闭")

def test_browser_only():
    """仅测试浏览器创建，不运行爬虫"""
    logger.info("=== 浏览器测试模式 ===")
    
    # 加载配置（测试模式不需要数据库配置）
    logger.info("跳过数据库配置检查...")
    
    browser = create_browser()
    if browser:
        logger.info("✅ 浏览器创建成功!")
        try:
            browser.get("https://www.baidu.com")
            logger.info("✅ 页面访问成功!")
            browser.quit()
            logger.info("✅ 浏览器已关闭")
        except Exception as e:
            logger.error("❌ 页面访问失败: {}".format(e))
            browser.quit()
    else:
        logger.error("❌ 浏览器创建失败")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_browser_only()
    else:
        main()
