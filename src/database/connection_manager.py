#!/usr/bin/python
# -*- coding:utf-8 -*-
# @author  : AI Assistant
# @time    : 2024/01/01
# @function: 数据库连接管理器 - 处理连接池和重连逻辑
# @version : V1

import pymysql
import threading
import time
from typing import Dict, Any, Optional
from contextlib import contextmanager
from typing import Dict, Any, List, Optional
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConnectionManager:
    """数据库连接管理器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.connections = []
        self.max_connections = 10
        self.current_connections = 0
        self._lock = threading.Lock()
        self._closed = False
        
        # 连接参数
        self.connect_params = {
            'host': config.get('host', 'localhost'),
            'port': config.get('port', 3306),
            'user': config.get('user', 'root'),
            'password': config.get('password', ''),
            'db': config.get('db', 'spider_db'),
            'charset': config.get('charset', 'utf8'),
            'autocommit': True,
            'connect_timeout': 10,
            'read_timeout': 30,
            'write_timeout': 30,
            'max_allowed_packet': 16777216,
            'sql_mode': "STRICT_TRANS_TABLES,NO_ZERO_DATE,NO_ZERO_IN_DATE,ERROR_FOR_DIVISION_BY_ZERO"
        }
        
        logger.info(f"连接管理器初始化: {self.connect_params['host']}:{self.connect_params['port']}/{self.connect_params['db']}")
    
    def _create_connection(self):
        """创建新的数据库连接"""
        try:
            conn = pymysql.connect(**self.connect_params)
            logger.info("新数据库连接创建成功")
            return conn
        except Exception as e:
            logger.error(f"创建数据库连接失败: {e}")
            raise
    
    def _get_connection(self):
        """获取可用的数据库连接"""
        with self._lock:
            if self._closed:
                raise RuntimeError("连接管理器已关闭")
            
            # 尝试从连接池获取可用连接
            for conn in self.connections:
                try:
                    # 测试连接是否有效
                    conn.ping(reconnect=False)
                    return conn
                except:
                    # 连接无效，从池中移除
                    try:
                        conn.close()
                    except:
                        pass
                    self.connections.remove(conn)
                    self.current_connections -= 1
            
            # 如果没有可用连接且未达到最大连接数，创建新连接
            if self.current_connections < self.max_connections:
                conn = self._create_connection()
                self.connections.append(conn)
                self.current_connections += 1
                return conn
            else:
                # 达到最大连接数，等待或创建临时连接
                logger.warning("连接池已满，创建临时连接")
                return self._create_connection()
    
    @contextmanager
    def get_cursor(self):
        """获取数据库游标的上下文管理器"""
        conn = None
        cursor = None
        try:
            conn = self._get_connection()
            if not conn:
                raise Exception("无法获取数据库连接")
            
            # 确保连接有效
            conn.ping(reconnect=True)
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            yield cursor
        except (pymysql.OperationalError, pymysql.InterfaceError) as e:
            logger.warning(f"数据库操作失败，尝试重新连接: {e}")
            # 如果是连接问题，尝试重新获取连接
            try:
                if conn:
                    conn.close()
            except:
                pass
            
            # 重新获取连接
            conn = self._create_connection()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            yield cursor
        finally:
            if cursor:
                try:
                    cursor.close()
                except:
                    pass
    
    def execute_query(self, sql: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """执行查询并返回所有结果"""
        with self.get_cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchall()
    
    def execute_one(self, sql: str, params: Optional[tuple] = None) -> Optional[Dict[str, Any]]:
        """执行查询并返回单条结果"""
        with self.get_cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchone()
    
    def execute_update(self, sql: str, params: Optional[tuple] = None) -> int:
        """执行更新操作并返回影响的行数"""
        with self.get_cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.rowcount
    
    def execute_insert(self, sql: str, params: Optional[tuple] = None) -> int:
        """执行插入操作并返回影响的行数"""
        with self.get_cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.rowcount
    
    def test_connection(self) -> bool:
        """测试数据库连接"""
        try:
            result = self.execute_one("SELECT 1 as test")
            return result is not None and result.get('test') == 1
        except Exception as e:
            logger.error(f"数据库连接测试失败: {e}")
            return False
    
    def close(self):
        """关闭所有连接"""
        with self._lock:
            self._closed = True
            for conn in self.connections:
                try:
                    conn.close()
                except:
                    pass
            self.connections.clear()
            self.current_connections = 0
            logger.info("连接管理器已关闭")

# 全局连接管理器实例
_connection_manager: Optional[ConnectionManager] = None
_manager_lock = threading.Lock()

def get_connection_manager(config: Dict[str, Any]) -> ConnectionManager:
    """获取全局连接管理器实例"""
    global _connection_manager
    
    with _manager_lock:
        if _connection_manager is None or _connection_manager._closed:
            _connection_manager = ConnectionManager(config)
        return _connection_manager

def close_connection_manager():
    """关闭全局连接管理器"""
    global _connection_manager
    
    with _manager_lock:
        if _connection_manager:
            _connection_manager.close()
            _connection_manager = None

# 使用示例
if __name__ == '__main__':
    # 测试连接管理器
    config = {
        'host': 'localhost',
        'port': 3306,
        'user': 'root',
        'password': '123456',
        'db': 'spider_db'
    }
    
    manager = get_connection_manager(config)
    
    try:
        # 测试连接
        if manager.test_connection():
            print("✓ 数据库连接测试成功")
        else:
            print("✗ 数据库连接测试失败")
        
        # 测试查询
        result = manager.execute_one("SELECT COUNT(*) as count FROM job_info")
        print(f"职位总数: {result.get('count', 0) if result else 0}")
        
    except Exception as e:
        print(f"测试失败: {e}")
    finally:
        close_connection_manager()