#!/usr/bin/python
# -*- coding:utf-8 -*-
# @author  : AI Assistant
# @time    : 2024/01/01
# @function: Web应用模块 - Flask应用工厂
# @version : V1

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import json
import re
from typing import Dict, Any, Optional

from src.utils.config import ConfigManager
from src.utils.logger import LoggerManager
from src.database.models import JobRepository

def create_app(config_file: str = 'config.json', env: str = 'production') -> Flask:
    """Flask应用工厂函数"""
    
    # 创建Flask应用
    app = Flask(__name__)
    CORS(app)
    
    # 初始化配置和日志
    config_manager = ConfigManager(config_file, env)
    logger_manager = LoggerManager(debug_mode=(env == 'development'))
    logger = logger_manager.get_logger('web_app')
    
    # 初始化数据库连接
    job_repository = None
    try:
        from dbutils import DBUtils
        db_config = config_manager.get_database_config()
        if db_config:
            db = DBUtils(**db_config)
            job_repository = JobRepository(db)
            logger.info("数据库连接成功")
        else:
            logger.error("数据库配置无效")
    except Exception as e:
        logger.error(f"数据库连接失败: {e}")
    
    def validate_sql(sql: str) -> tuple[bool, str]:
        """验证SQL语句的安全性"""
        # 只允许SELECT语句
        sql = sql.strip().upper()
        if not sql.startswith('SELECT'):
            return False, "只允许执行SELECT查询语句"
        
        # 禁止危险操作
        dangerous_keywords = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE', 'TRUNCATE', 'EXEC', 'EXECUTE']
        for keyword in dangerous_keywords:
            if keyword in sql:
                return False, f"禁止使用 {keyword} 操作"
        
        return True, "SQL验证通过"
    
    @app.route('/')
    def index():
        """仪表盘首页"""
        return render_template('dashboard.html')
    
    @app.route('/api/dashboard/stats')
    def get_dashboard_stats():
        """获取仪表盘统计数据"""
        try:
            if not job_repository:
                return jsonify({'success': False, 'error': '数据库连接未初始化'})
            
            stats = job_repository.get_job_statistics()
            
            # 获取更多统计数据
            db = job_repository.db
            
            # 按薪资范围统计
            salary_stats = db.select_all("""
                SELECT job_salary_range, COUNT(*) as count 
                FROM job_info 
                WHERE job_salary_range IS NOT NULL AND job_salary_range != '' 
                GROUP BY job_salary_range 
                ORDER BY count DESC 
                LIMIT 10
            """)
            
            # 按学历要求统计
            education_stats = db.select_all("""
                SELECT job_education, COUNT(*) as count 
                FROM job_info 
                WHERE job_education IS NOT NULL AND job_education != '' 
                GROUP BY job_education 
                ORDER BY count DESC
            """)
            
            # 按工作经验统计
            experience_stats = db.select_all("""
                SELECT job_experience, COUNT(*) as count 
                FROM job_info 
                WHERE job_experience IS NOT NULL AND job_experience != '' 
                GROUP BY job_experience 
                ORDER BY count DESC
            """)
            
            # 按抓取时间统计（最近7天）
            time_stats = db.select_all("""
                SELECT create_time, COUNT(*) as count 
                FROM job_info 
                WHERE create_time >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
                GROUP BY create_time 
                ORDER BY create_time DESC
            """)
            
            stats.update({
                'salary_stats': salary_stats,
                'education_stats': education_stats,
                'experience_stats': experience_stats,
                'time_stats': time_stats
            })
            
            return jsonify({
                'success': True,
                'data': stats
            })
        except Exception as e:
            logger.error(f"获取统计数据失败: {e}")
            return jsonify({'success': False, 'error': str(e)})
    
    @app.route('/api/sql/query', methods=['POST'])
    def execute_sql_query():
        """执行自定义SQL查询"""
        try:
            data = request.get_json()
            sql = data.get('sql', '').strip()
            
            if not sql:
                return jsonify({'success': False, 'error': 'SQL语句不能为空'})
            
            # 验证SQL安全性
            is_valid, message = validate_sql(sql)
            if not is_valid:
                return jsonify({'success': False, 'error': message})
            
            if not job_repository:
                return jsonify({'success': False, 'error': '数据库连接未初始化'})
            
            results = job_repository.db.select_all(sql)
            
            return jsonify({
                'success': True,
                'data': results,
                'count': len(results)
            })
        except Exception as e:
            logger.error(f"SQL查询失败: {e}")
            return jsonify({'success': False, 'error': str(e)})
    
    @app.route('/api/sql/tables')
    def get_table_info():
        """获取数据库表信息"""
        try:
            if not job_repository:
                return jsonify({'success': False, 'error': '数据库连接未初始化'})
            
            db = job_repository.db
            
            # 获取表结构
            table_info = db.select_all("DESCRIBE job_info")
            
            # 获取表统计信息
            table_stats = db.select_one("""
                SELECT 
                    COUNT(*) as total_records,
                    COUNT(DISTINCT province) as unique_provinces,
                    COUNT(DISTINCT job_industry) as unique_industries,
                    COUNT(DISTINCT job_company) as unique_companies
                FROM job_info
            """)
            
            return jsonify({
                'success': True,
                'data': {
                    'table_structure': table_info,
                    'table_stats': table_stats
                }
            })
        except Exception as e:
            logger.error(f"获取表信息失败: {e}")
            return jsonify({'success': False, 'error': str(e)})
    
    @app.route('/api/sql/examples')
    def get_sql_examples():
        """获取SQL查询示例"""
        examples = [
            {
                'title': '查询各城市职位数量',
                'sql': 'SELECT job_location, COUNT(*) as count FROM job_info GROUP BY job_location ORDER BY count DESC LIMIT 20',
                'description': '统计各城市的职位数量，按数量降序排列'
            },
            {
                'title': '查询高薪职位（20K以上）',
                'sql': "SELECT job_title, job_company, job_salary_range, job_location FROM job_info WHERE job_salary_range LIKE '%20%' OR job_salary_range LIKE '%30%' OR job_salary_range LIKE '%40%' OR job_salary_range LIKE '%50%' LIMIT 20",
                'description': '查询薪资范围包含20K以上的职位信息'
            },
            {
                'title': '查询大厂职位',
                'sql': "SELECT job_title, job_company, job_salary_range, job_location FROM job_info WHERE job_company IN ('腾讯', '阿里巴巴', '百度', '字节跳动', '美团', '滴滴', '京东', '网易') LIMIT 20",
                'description': '查询知名互联网公司的职位信息'
            },
            {
                'title': '查询Python相关职位',
                'sql': "SELECT job_title, job_company, job_salary_range, job_location FROM job_info WHERE job_title LIKE '%Python%' OR job_skills LIKE '%Python%' LIMIT 20",
                'description': '查询Python相关的职位信息'
            },
            {
                'title': '查询最近抓取的职位',
                'sql': "SELECT job_title, job_company, job_salary_range, create_time FROM job_info ORDER BY create_time DESC LIMIT 20",
                'description': '查询最近抓取的职位信息'
            },
            {
                'title': '统计各学历要求的职位数量',
                'sql': 'SELECT job_education, COUNT(*) as count FROM job_info WHERE job_education IS NOT NULL GROUP BY job_education ORDER BY count DESC',
                'description': '统计不同学历要求的职位数量分布'
            }
        ]
        
        return jsonify({'success': True, 'data': examples})
    
    @app.route('/api/spider/status')
    def get_spider_status():
        """获取爬虫状态"""
        try:
            if not job_repository:
                return jsonify({'success': False, 'error': '数据库连接未初始化'})
            
            db = job_repository.db
            
            # 获取最近抓取的数据统计
            recent_stats = db.select_one("""
                SELECT 
                    COUNT(*) as total_jobs,
                    MAX(create_time) as last_crawl_time,
                    COUNT(DISTINCT create_time) as crawl_days
                FROM job_info
            """)
            
            # 获取今日抓取数量
            today_stats = db.select_one("""
                SELECT COUNT(*) as today_jobs
                FROM job_info 
                WHERE create_time = CURDATE()
            """)
            
            return jsonify({
                'success': True,
                'data': {
                    'total_jobs': recent_stats.get('total_jobs', 0),
                    'last_crawl_time': recent_stats.get('last_crawl_time'),
                    'crawl_days': recent_stats.get('crawl_days', 0),
                    'today_jobs': today_stats.get('today_jobs', 0) if today_stats else 0
                }
            })
        except Exception as e:
            logger.error(f"获取爬虫状态失败: {e}")
            return jsonify({'success': False, 'error': str(e)})
    
    return app

# 使用示例
if __name__ == '__main__':
    app = create_app(env='development')
    app.run(debug=True, host='0.0.0.0', port=5000)
