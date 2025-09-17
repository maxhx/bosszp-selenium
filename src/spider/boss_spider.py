#!/usr/bin/python
# -*- coding:utf-8 -*-
# @author  : AI Assistant
# @time    : 2024/01/01
# @function: 项目重构示例 - 基础爬虫类
# @version : V1

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from typing import Optional, List, Dict, Any
import time
import os

from src.utils.config import ConfigManager
from src.utils.logger import LoggerManager
from src.database.models import JobInfo, JobRepository
from src.constants.cities import CITY_MAP

class BaseSpider:
    """基础爬虫类"""
    
    def __init__(self, config_file: str = 'config.json', env: str = 'production'):
        self.config_manager = ConfigManager(config_file, env)
        self.logger_manager = LoggerManager(debug_mode=(env == 'development'))
        self.logger = self.logger_manager.get_logger(self.__class__.__name__)
        self.spider_logger = self.logger_manager.get_spider_logger()
        
        self.browser: Optional[webdriver.Firefox] = None
        self.job_repository: Optional[JobRepository] = None
        
        # 初始化组件
        self._setup_database()
        self._setup_browser()
    
    def _setup_database(self) -> None:
        """设置数据库连接"""
        try:
            from dbutils import DBUtils
            db_config = self.config_manager.get_database_config()
            if db_config:
                db = DBUtils(**db_config)
                self.job_repository = JobRepository(db)
                self.logger.info("数据库连接成功")
            else:
                self.logger.error("数据库配置无效")
        except Exception as e:
            self.logger.error(f"数据库连接失败: {e}")
    
    def _setup_browser(self) -> None:
        """设置浏览器"""
        try:
            options = Options()
            
            # 根据环境设置浏览器选项
            if self.config_manager.get('debug_mode', False):
                options.add_argument('--headless')
            
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            
            # 查找Firefox路径
            firefox_path = self._find_firefox_path()
            if firefox_path:
                options.binary_location = firefox_path
            
            # 查找geckodriver路径
            geckodriver_path = self._find_geckodriver_path()
            if not geckodriver_path:
                raise Exception("未找到geckodriver")
            
            self.browser = webdriver.Firefox(options=options)
            self.logger.info("浏览器启动成功")
            
        except Exception as e:
            self.logger.error(f"浏览器启动失败: {e}")
            self.browser = None
    
    def _find_firefox_path(self) -> Optional[str]:
        """查找Firefox可执行文件路径"""
        firefox_paths = [
            "/usr/bin/firefox",
            "/usr/bin/firefox-esr",
            "/snap/bin/firefox",
            "/opt/firefox/firefox",
            "/usr/local/bin/firefox"
        ]
        
        for path in firefox_paths:
            if os.path.exists(path) and os.access(path, os.X_OK):
                self.logger.info(f"找到Firefox: {path}")
                return path
        
        self.logger.warning("未找到Firefox可执行文件")
        return None
    
    def _find_geckodriver_path(self) -> Optional[str]:
        """查找geckodriver路径"""
        geckodriver_paths = [
            "/usr/local/bin/geckodriver",
            "/usr/bin/geckodriver",
            "/snap/bin/geckodriver"
        ]
        
        for path in geckodriver_paths:
            if os.path.exists(path) and os.access(path, os.X_OK):
                self.logger.info(f"找到geckodriver: {path}")
                return path
        
        self.logger.error("未找到geckodriver")
        return None
    
    def wait_for_page_load(self, timeout: int = 10) -> bool:
        """等待页面加载完成"""
        try:
            WebDriverWait(self.browser, timeout).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            WebDriverWait(self.browser, timeout).until(
                lambda d: d.execute_script("return document.body != null")
            )
            return True
        except Exception as e:
            self.logger.warning(f"页面加载等待超时: {e}")
            return False
    
    def scroll_page(self, times: int = 2, delay: float = 2.0) -> None:
        """滚动页面"""
        for i in range(times):
            self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(delay)
    
    def get_province_from_location(self, location: str) -> str:
        """从工作地点获取省份"""
        if not location or '·' not in location:
            return ''
        
        city = location.split('·')[0]
        for province, cities in CITY_MAP.items():
            if city in cities:
                return province
        return ''
    
    def save_job_info(self, job_info: JobInfo) -> bool:
        """保存职位信息"""
        if not self.job_repository:
            self.logger.error("数据库连接未初始化")
            return False
        
        try:
            success = self.job_repository.save_job(job_info)
            if success:
                self.logger.info(f"成功保存职位: {job_info.job_title} - {job_info.job_company}")
                self.spider_logger.info(f"保存职位: {job_info.job_title}|{job_info.job_company}|{job_info.job_location}")
            else:
                self.logger.debug(f"职位已存在或保存失败: {job_info.job_title} - {job_info.job_company}")
            return success
        except Exception as e:
            self.logger.error(f"保存职位失败: {e}")
            return False
    
    def close(self) -> None:
        """关闭爬虫"""
        if self.browser:
            self.logger.info("正在关闭浏览器...")
            self.browser.quit()
            self.logger.info("浏览器已关闭")
        
        if self.job_repository and hasattr(self.job_repository.db, 'close'):
            self.job_repository.db.close()
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()

class BossSpider(BaseSpider):
    """Boss直聘爬虫"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.base_url = "https://www.zhipin.com/guangzhou/?ka=city-sites-101280100"
    
    def crawl_jobs(self, categories: List[str] = None) -> int:
        """爬取职位信息"""
        if not self.browser:
            self.logger.error("浏览器未初始化")
            return 0
        
        if not self.job_repository:
            self.logger.error("数据库未初始化")
            return 0
        
        try:
            self.logger.info("开始爬取Boss直聘职位信息")
            self.browser.get(self.base_url)
            
            # 点击互联网/AI分类
            self._click_category()
            
            # 获取职位分类
            job_categories = self._get_job_categories()
            if categories:
                job_categories = [cat for cat in job_categories if cat in categories]
            
            total_saved = 0
            for category in job_categories:
                saved_count = self._crawl_category_jobs(category)
                total_saved += saved_count
                self.logger.info(f"分类 {category} 爬取完成，保存 {saved_count} 个职位")
            
            self.logger.info(f"爬取完成，总共保存 {total_saved} 个职位")
            return total_saved
            
        except Exception as e:
            self.logger.error(f"爬取过程出错: {e}")
            return 0
    
    def _click_category(self) -> None:
        """点击职位分类"""
        try:
            category_element = self.browser.find_element(
                By.XPATH, 
                '//*[@id="main"]/div/div[1]/div/div[1]/dl[1]/dd/b'
            )
            category_element.click()
            self.logger.info("成功点击互联网/AI分类")
        except Exception as e:
            self.logger.error(f"点击分类失败: {e}")
            raise
    
    def _get_job_categories(self) -> List[str]:
        """获取职位分类列表"""
        try:
            category_elements = self.browser.find_elements(
                By.XPATH, 
                '//*[@id="main"]/div/div[1]/div/div[1]/dl[1]/div/ul/li/div/a'
            )
            categories = []
            for element in category_elements:
                try:
                    category_name = element.accessible_name
                    if category_name and ('java' in category_name.lower() or 'python' in category_name.lower()):
                        categories.append(category_name)
                except:
                    continue
            return categories
        except Exception as e:
            self.logger.error(f"获取分类列表失败: {e}")
            return []
    
    def _crawl_category_jobs(self, category: str) -> int:
        """爬取指定分类的职位"""
        try:
            # 点击分类
            category_elements = self.browser.find_elements(
                By.XPATH, 
                '//*[@id="main"]/div/div[1]/div/div[1]/dl[1]/div/ul/li/div/a'
            )
            
            for element in category_elements:
                if element.accessible_name == category:
                    element.click()
                    break
            
            # 等待页面加载
            self.wait_for_page_load()
            
            # 滚动页面加载更多内容
            self.scroll_page(times=2, delay=5)
            
            # 获取职位列表
            job_elements = self.browser.find_elements(
                By.XPATH, 
                '/html/body/div[1]/div[2]/div[3]/div/div/div[1]/ul/div'
            )
            
            saved_count = 0
            for job_element in job_elements:
                job_info = self._parse_job_element(job_element, category)
                if job_info and self.save_job_info(job_info):
                    saved_count += 1
            
            # 返回首页
            self.browser.back()
            self._click_category()
            
            return saved_count
            
        except Exception as e:
            self.logger.error(f"爬取分类 {category} 失败: {e}")
            return 0
    
    def _parse_job_element(self, element, category: str) -> Optional[JobInfo]:
        """解析职位元素"""
        try:
            # 提取职位信息
            job_title = self._safe_get_text(element, './div/li/div[1]/div/a')
            job_company = self._safe_get_text(element, './/span[@class="boss-name"]')
            job_location = self._safe_get_text(element, './/span[@class="company-location"]')
            job_salary_range = self._safe_get_text(element, './div/li/div[1]/div/span')
            job_experience = self._safe_get_text(element, './div/li/div[1]/ul/li[1]')
            job_education = self._safe_get_text(element, './div/li/div[1]/ul/li[2]')
            job_industry = self._safe_get_text(element, './div[1]/div/div[2]/ul/li[1]')
            job_finance = self._safe_get_text(element, './div[1]/div/div[2]/ul/li[2]')
            job_scale = self._safe_get_text(element, './div[1]/div/div[2]/ul/li[3]')
            job_welfare = self._safe_get_text(element, './div[2]/div')
            
            # 获取技能要求
            skill_elements = element.find_elements(By.XPATH, './div[2]/ul/li')
            job_skills = ','.join([skill.text.strip() for skill in skill_elements]) if skill_elements else '无'
            
            # 创建职位信息对象
            job_info = JobInfo(
                category='后端开发',
                sub_category=category,
                job_title=job_title,
                job_company=job_company,
                job_location=job_location,
                job_salary_range=job_salary_range,
                job_experience=job_experience,
                job_education=job_education,
                job_industry=job_industry,
                job_finance=job_finance,
                job_scale=job_scale,
                job_welfare=job_welfare,
                job_skills=job_skills
            )
            
            # 设置省份
            job_info.province = self.get_province_from_location(job_location)
            
            return job_info if job_info.is_valid() else None
            
        except Exception as e:
            self.logger.debug(f"解析职位元素失败: {e}")
            return None
    
    def _safe_get_text(self, element, xpath: str, default: str = '无') -> str:
        """安全获取元素文本"""
        try:
            sub_element = element.find_element(By.XPATH, xpath)
            return sub_element.text.strip() if sub_element.text else default
        except:
            return default

# 使用示例
if __name__ == '__main__':
    with BossSpider(env='production') as spider:
        saved_count = spider.crawl_jobs(['Java开发工程师', 'Python开发工程师'])
        print(f"爬取完成，保存了 {saved_count} 个职位")
