#!/usr/bin/python
# -*- coding:utf-8 -*-
# @author  : AI Assistant
# @time    : 2024/01/01
# @function: 启动Boss直聘数据仪表盘
# @version : V1

import os
import sys
import subprocess

def check_dependencies():
    """检查依赖是否安装"""
    try:
        import flask
        import flask_cors
        import pymysql
        print("✓ 所有依赖已安装")
        return True
    except ImportError as e:
        print(f"✗ 缺少依赖: {e}")
        print("请运行: pip install -r requirements.txt")
        return False

def check_database():
    """检查数据库连接"""
    try:
        from dbutils import DBUtils
        from src.utils.config import ConfigManager
        
        # 使用生产环境配置
        config = ConfigManager('src/utils/config.json', env='production')
        db_config = config.get_database_config()
        
        if not db_config:
            print("✗ 生产环境数据库配置无效")
            return False
            
        db = DBUtils(**db_config)
        db.close()
        print("✓ 生产环境数据库连接正常")
        return True
    except Exception as e:
        print(f"✗ 数据库连接失败: {e}")
        print("请确保MySQL服务已启动，并且生产环境数据库配置正确")
        return False

def main():
    """主函数"""
    print("=" * 50)
    print("Boss直聘数据仪表盘启动器")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        return
    
    # 检查数据库
    if not check_database():
        return
    
    print("\n正在启动仪表盘服务（生产环境）...")
    print("访问地址: http://localhost:5000")
    print("按 Ctrl+C 停止服务")
    print("-" * 50)
    
    # 启动Flask应用
    try:
        from src.web.app import create_app
        app = create_app(env='production')
        app.run(debug=False, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n服务已停止")
    except Exception as e:
        print(f"启动失败: {e}")

if __name__ == '__main__':
    main()
