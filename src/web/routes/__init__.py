#!/usr/bin/python
# -*- coding:utf-8 -*-
# @author  : AI Assistant
# @time    : 2024/01/01
# @function: Web应用路由模块
# @version : V1

from flask import Blueprint, render_template, request, jsonify
from typing import Dict, Any, Optional

# 创建蓝图
dashboard_bp = Blueprint('dashboard', __name__)
api_bp = Blueprint('api', __name__, url_prefix='/api')

@dashboard_bp.route('/')
def index():
    """仪表盘首页"""
    return render_template('dashboard.html')

@dashboard_bp.route('/dashboard')
def dashboard():
    """仪表盘页面"""
    return render_template('dashboard.html')

@api_bp.route('/health')
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'healthy',
        'message': 'Boss直聘数据仪表盘运行正常'
    })

@api_bp.route('/version')
def get_version():
    """获取版本信息"""
    return jsonify({
        'version': '1.0.0',
        'name': 'Boss直聘数据仪表盘',
        'description': '基于Flask的数据可视化和SQL查询平台'
    })
