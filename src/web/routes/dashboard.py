#!/usr/bin/python
# -*- coding:utf-8 -*-
# @author  : AI Assistant
# @time    : 2024/01/01
# @function: 仪表盘路由模块
# @version : V1

from flask import Blueprint, render_template, request, jsonify
from typing import Dict, Any, Optional
import json
import re

dashboard_bp = Blueprint('dashboard', __name__)

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

@dashboard_bp.route('/')
def index():
    """仪表盘首页"""
    return render_template('dashboard.html')

@dashboard_bp.route('/dashboard')
def dashboard():
    """仪表盘页面"""
    return render_template('dashboard.html')

@dashboard_bp.route('/api/dashboard/stats')
def get_dashboard_stats():
    """获取仪表盘统计数据"""
    try:
        from src.database.models import JobRepository
        from src.utils.config import ConfigManager
        from dbutils import DBUtils
        
        # 初始化配置和数据库
        config_manager = ConfigManager()
        db_config = config_manager.get_database_config()
        
        if not db_config:
            return jsonify({'success': False, 'error': '数据库配置无效'})
        
        db = DBUtils(**db_config)
        job_repository = JobRepository(db)
        
        stats = job_repository.get_job_statistics()
        
        # 获取更多统计数据
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
        
        db.close()
        
        return jsonify({
            'success': True,
            'data': stats
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@dashboard_bp.route('/api/sql/query', methods=['POST'])
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
        
        from src.utils.config import ConfigManager
        from dbutils import DBUtils
        
        config_manager = ConfigManager()
        db_config = config_manager.get_database_config()
        
        if not db_config:
            return jsonify({'success': False, 'error': '数据库配置无效'})
        
        db = DBUtils(**db_config)
        results = db.select_all(sql)
        db.close()
        
        return jsonify({
            'success': True,
            'data': results,
            'count': len(results)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@dashboard_bp.route('/api/sql/tables')
def get_table_info():
    """获取数据库表信息"""
    try:
        from src.utils.config import ConfigManager
        from dbutils import DBUtils
        
        config_manager = ConfigManager()
        db_config = config_manager.get_database_config()
        
        if not db_config:
            return jsonify({'success': False, 'error': '数据库配置无效'})
        
        db = DBUtils(**db_config)
        
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
        
        db.close()
        
        return jsonify({
            'success': True,
            'data': {
                'table_structure': table_info,
                'table_stats': table_stats
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@dashboard_bp.route('/api/sql/examples')
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
