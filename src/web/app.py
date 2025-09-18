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

import sys
import os
# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.utils.config import ConfigManager
from src.utils.logger import LoggerManager
from src.database.models import JobRepository
from src.database.connection_manager import get_connection_manager, close_connection_manager
from src.web.routes.dashboard import dashboard_bp

def create_app(config_file: str = 'src/utils/config.json', env: str = 'production') -> Flask:
    """Flask应用工厂函数"""
    
    # 创建Flask应用
    app = Flask(__name__, template_folder='templates', root_path=os.path.dirname(os.path.abspath(__file__)))
    CORS(app)
    
    # 注册蓝图
    app.register_blueprint(dashboard_bp)
    
    # 初始化配置和日志
    config_manager = ConfigManager(config_file, env)
    logger_manager = LoggerManager(debug_mode=(env == 'production'))
    logger = logger_manager.get_logger('web_app')
    
    # 初始化数据库连接管理器
    connection_manager = None
    job_repository = None
    try:
        db_config = config_manager.get_database_config()
        if db_config:
            connection_manager = get_connection_manager(db_config)
            # 测试连接
            connection_manager.execute_one("SELECT 1 as test")
            logger.info("数据库连接管理器初始化成功")
        else:
            logger.error("数据库配置无效")
    except Exception as e:
        logger.error(f"数据库连接管理器初始化失败: {e}")
    
    
    
    
    # 添加应用关闭时的清理逻辑
    @app.teardown_appcontext
    def close_db(error):
        """应用上下文关闭时清理资源"""
        pass  # 连接管理器会在应用关闭时自动清理
    
    return app

# 使用示例
if __name__ == '__main__':
    app = create_app(env='production')
    try:
        app.run(debug=False, host='0.0.0.0', port=5000)
    finally:
        # 确保连接管理器被正确关闭
        close_connection_manager()
