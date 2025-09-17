#!/usr/bin/python
# -*- coding:utf-8 -*-
# @author  : AI Assistant
# @time    : 2024/01/01
# @function: 项目重构示例 - 数据模型
# @version : V1

from typing import Optional, Dict, Any
from datetime import datetime

class JobInfo:
    """职位信息数据模型"""
    
    def __init__(self, **kwargs):
        self.category: str = kwargs.get('category', '')
        self.sub_category: str = kwargs.get('sub_category', '')
        self.job_title: str = kwargs.get('job_title', '')
        self.province: str = kwargs.get('province', '')
        self.job_location: str = kwargs.get('job_location', '')
        self.job_company: str = kwargs.get('job_company', '')
        self.job_industry: str = kwargs.get('job_industry', '')
        self.job_finance: str = kwargs.get('job_finance', '')
        self.job_scale: str = kwargs.get('job_scale', '')
        self.job_welfare: str = kwargs.get('job_welfare', '')
        self.job_salary_range: str = kwargs.get('job_salary_range', '')
        self.job_experience: str = kwargs.get('job_experience', '')
        self.job_education: str = kwargs.get('job_education', '')
        self.job_skills: str = kwargs.get('job_skills', '')
        self.create_time: str = kwargs.get('create_time', datetime.now().strftime('%Y-%m-%d'))
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'category': self.category,
            'sub_category': self.sub_category,
            'job_title': self.job_title,
            'province': self.province,
            'job_location': self.job_location,
            'job_company': self.job_company,
            'job_industry': self.job_industry,
            'job_finance': self.job_finance,
            'job_scale': self.job_scale,
            'job_welfare': self.job_welfare,
            'job_salary_range': self.job_salary_range,
            'job_experience': self.job_experience,
            'job_education': self.job_education,
            'job_skills': self.job_skills,
            'create_time': self.create_time
        }
    
    def to_tuple(self) -> tuple:
        """转换为元组（用于数据库插入）"""
        return (
            self.category, self.sub_category, self.job_title, self.province,
            self.job_location, self.job_company, self.job_industry, self.job_finance,
            self.job_scale, self.job_welfare, self.job_salary_range, self.job_experience,
            self.job_education, self.job_skills, self.create_time
        )
    
    def is_valid(self) -> bool:
        """验证数据是否有效"""
        return bool(self.job_title and self.job_company and self.job_location)
    
    def get_unique_key(self) -> tuple:
        """获取唯一标识（用于去重）"""
        return (self.job_title, self.job_company, self.job_location)
    
    def __str__(self) -> str:
        return f"JobInfo(title={self.job_title}, company={self.job_company}, location={self.job_location})"
    
    def __repr__(self) -> str:
        return self.__str__()

class JobRepository:
    """职位数据仓库"""
    
    def __init__(self, db_utils):
        self.db = db_utils
    
    def save_job(self, job_info: JobInfo) -> bool:
        """保存职位信息"""
        try:
            if not job_info.is_valid():
                return False
            
            # 检查是否已存在
            if self.job_exists(job_info):
                return False
            
            # 插入数据
            sql = """
                INSERT INTO job_info(
                    category, sub_category, job_title, province, job_location,
                    job_company, job_industry, job_finance, job_scale, job_welfare,
                    job_salary_range, job_experience, job_education, job_skills, create_time
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            self.db.insert_data(sql, job_info.to_tuple())
            return True
            
        except Exception as e:
            print(f"保存职位失败: {e}")
            return False
    
    def job_exists(self, job_info: JobInfo) -> bool:
        """检查职位是否已存在"""
        try:
            sql = "SELECT 1 FROM job_info WHERE job_title=%s AND job_company=%s AND job_location=%s"
            result = self.db.select_one(sql, job_info.get_unique_key())
            return result is not None
        except Exception as e:
            print(f"检查职位存在性失败: {e}")
            return False
    
    def get_jobs_by_category(self, category: str, limit: int = 100) -> list:
        """根据分类获取职位"""
        try:
            sql = "SELECT * FROM job_info WHERE category=%s ORDER BY create_time DESC LIMIT %s"
            return self.db.select_all(sql, (category, limit))
        except Exception as e:
            print(f"获取职位失败: {e}")
            return []
    
    def get_job_statistics(self) -> Dict[str, Any]:
        """获取职位统计信息"""
        try:
            stats = {}
            
            # 总职位数
            total_jobs = self.db.select_one("SELECT COUNT(*) as count FROM job_info")
            stats['total_jobs'] = total_jobs['count'] if total_jobs else 0
            
            # 按省份统计
            province_stats = self.db.select_all("""
                SELECT province, COUNT(*) as count 
                FROM job_info 
                WHERE province IS NOT NULL AND province != '' 
                GROUP BY province 
                ORDER BY count DESC 
                LIMIT 10
            """)
            stats['province_stats'] = province_stats
            
            # 按行业统计
            industry_stats = self.db.select_all("""
                SELECT job_industry, COUNT(*) as count 
                FROM job_info 
                WHERE job_industry IS NOT NULL AND job_industry != '' 
                GROUP BY job_industry 
                ORDER BY count DESC 
                LIMIT 10
            """)
            stats['industry_stats'] = industry_stats
            
            return stats
            
        except Exception as e:
            print(f"获取统计信息失败: {e}")
            return {}

# 使用示例
if __name__ == '__main__':
    # 创建职位信息
    job = JobInfo(
        job_title="Python开发工程师",
        job_company="腾讯",
        job_location="深圳·南山区",
        job_salary_range="15-25K",
        job_experience="3-5年",
        job_education="本科"
    )
    
    print(f"职位信息: {job}")
    print(f"数据有效性: {job.is_valid()}")
    print(f"唯一标识: {job.get_unique_key()}")
    print(f"字典格式: {job.to_dict()}")
