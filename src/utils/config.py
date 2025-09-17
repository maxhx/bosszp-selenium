#!/usr/bin/python
# -*- coding:utf-8 -*-
# @author  : AI Assistant
# @time    : 2024/01/01
# @function: 项目重构示例 - 配置管理模块
# @version : V1

import json
import os
from typing import Dict, Any, Optional

class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_file: str = 'config.json', env: str = 'production'):
        self.config_file = config_file
        self.env = env
        self._config: Optional[Dict[str, Any]] = None
        self.load_config()
    
    def load_config(self) -> None:
        """加载配置文件"""
        try:
            if not os.path.exists(self.config_file):
                raise FileNotFoundError(f"配置文件 {self.config_file} 不存在")
            
            with open(self.config_file, 'r', encoding='utf-8') as f:
                all_configs = json.load(f)
            
            if self.env not in all_configs:
                raise ValueError(f"环境配置 {self.env} 不存在")
            
            self._config = all_configs[self.env]
            print(f"✓ 配置文件加载成功，当前环境: {self.env}")
            
        except Exception as e:
            print(f"✗ 配置文件加载失败: {e}")
            self._config = None
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        if self._config is None:
            return default
        return self._config.get(key, default)
    
    def get_database_config(self) -> Dict[str, Any]:
        """获取数据库配置"""
        if self._config is None:
            return {}
        
        return {
            'host': self.get('host', 'localhost'),
            'port': self.get('port', 3306),
            'user': self.get('user', 'root'),
            'password': self.get('password', ''),
            'db': self.get('db', 'spider_db'),
            'charset': 'utf8'
        }
    
    def is_valid(self) -> bool:
        """检查配置是否有效"""
        return self._config is not None

# 使用示例
if __name__ == '__main__':
    # 创建配置管理器
    config = ConfigManager(env='production')
    
    if config.is_valid():
        print("数据库配置:", config.get_database_config())
    else:
        print("配置无效")
