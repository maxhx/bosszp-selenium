#!/usr/bin/python
# -*- coding:utf-8 -*-
# @author  : AI Assistant
# @time    : 2024/01/01
# @function: 项目重构示例 - 日志管理模块
# @version : V1

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from typing import Optional

class LoggerManager:
    """日志管理器"""
    
    def __init__(self, log_dir: str = 'logs', debug_mode: bool = False):
        self.log_dir = log_dir
        self.debug_mode = debug_mode
        self._setup_logging()
    
    def _setup_logging(self) -> None:
        """设置日志系统"""
        # 创建日志目录
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir, mode=0o755)
        
        # 设置日志格式
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        date_format = '%Y-%m-%d %H:%M:%S'
        
        # 配置根日志器
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG if self.debug_mode else logging.INFO)
        logger.handlers.clear()
        
        # 控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(log_format, date_format)
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        # 文件处理器
        file_handler = RotatingFileHandler(
            os.path.join(self.log_dir, 'boss_spider.log'),
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
            os.path.join(self.log_dir, 'boss_spider_error.log'),
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)
        logger.addHandler(error_handler)
        
        # 爬虫专用日志文件
        spider_handler = RotatingFileHandler(
            os.path.join(self.log_dir, 'spider_data.log'),
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
        spider_logger.propagate = False
    
    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """获取日志器"""
        return logging.getLogger(name)
    
    @staticmethod
    def get_spider_logger() -> logging.Logger:
        """获取爬虫专用日志器"""
        return logging.getLogger('spider')

# 使用示例
if __name__ == '__main__':
    # 创建日志管理器
    logger_manager = LoggerManager(debug_mode=True)
    
    # 获取日志器
    logger = logger_manager.get_logger(__name__)
    spider_logger = logger_manager.get_spider_logger()
    
    # 测试日志
    logger.info("这是一条信息日志")
    logger.error("这是一条错误日志")
    spider_logger.info("这是一条爬虫日志")
