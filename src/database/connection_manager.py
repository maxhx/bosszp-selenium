#!/usr/bin/python
# -*- coding:utf-8 -*-
# @author  : AI Assistant
# @time    : 2024/01/01
# @function: 数据库连接管理器 - 支持连接池和自动重连
# @version : V1

import pymysql
import threading
import time
from typing import Dict, Any, Optional
from contextlib import contextmanager

class DatabaseConnectionManager:
    """数据库连接管理器 - 支持连接池和自动重连"""
    
    def __init__(self, host: str, user: str, password: str, db: str, 
                 port: int = 3306, charset: str = 'utf8', 
                 max_connections: int = 5, connection_timeout: int = 30):
        """
        初始化数据库连接管理器
        
        Args:
            host: 数据库主机
            user: 用户名
            password: 密码
            db: 数据库名
            port: 端口
            charset: 字符集
            max_connections: 最大连接数
            connection_timeout: 连接超时时间（秒）
        """
        self.host = host
        self.user = user
        self.password = password
        self.db = db
        self.port = port
        self.charset = charset
        self.max_connections = max_connections
        self.connection_timeout = connection_timeout
        
        # 连接池
        self._connections = []
        self._lock = threading.Lock()
        self._closed = False
        
        # 初始化连接池
        self._initialize_connections()
    
    def _initialize_connections(self):
        """初始化连接池"""
        for _ in range(min(2, self.max_connections)):  # 初始创建2个连接
            try:
                conn = self._create_connection()
                if conn:
                    self._connections.append(conn)
            except Exception as e:
                print(f"初始化连接失败: {e}")
    
    def _create_connection(self) -> Optional[pymysql.Connection]:
        """创建新的数据库连接"""
        try:
            conn = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                db=self.db,
                port=self.port,
                charset=self.charset,
                autocommit=True,
                connect_timeout=self.connection_timeout,
                read_timeout=self.connection_timeout,
                write_timeout=self.connection_timeout
            )
            return conn
        except Exception as e:
            print(f"创建数据库连接失败: {e}")
            return None
    
    def _get_connection(self) -> Optional[pymysql.Connection]:
        """从连接池获取连接"""
        with self._lock:
            if self._closed:
                return None
            
            # 尝试获取可用连接
            for i, conn in enumerate(self._connections):
                try:
                    # 测试连接是否有效
                    conn.ping(reconnect=True)
                    return conn
                except:
                    # 连接无效，移除并创建新连接
                    try:
                        conn.close()
                    except:
                        pass
                    self._connections.pop(i)
            
            # 如果没有可用连接，创建新连接
            if len(self._connections) < self.max_connections:
                conn = self._create_connection()
                if conn:
                    self._connections.append(conn)
                    return conn
            
            return None
    
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
        except Exception as e:
            if conn:
                try:
                    conn.rollback()
                except:
                    pass
            raise e
        finally:
            if cursor:
                try:
                    cursor.close()
                except:
                    pass
    
    def execute_query(self, sql: str, args=None) -> list:
        """执行查询并返回结果"""
        with self.get_cursor() as cursor:
            cursor.execute(sql, args)
            return cursor.fetchall()
    
    def execute_one(self, sql: str, args=None) -> Optional[Dict[str, Any]]:
        """执行查询并返回单条结果"""
        with self.get_cursor() as cursor:
            cursor.execute(sql, args)
            return cursor.fetchone()
    
    def execute_update(self, sql: str, args=None) -> int:
        """执行更新操作并返回影响行数"""
        with self.get_cursor() as cursor:
            cursor.execute(sql, args)
            return cursor.rowcount
    
    def close(self):
        """关闭所有连接"""
        with self._lock:
            self._closed = True
            for conn in self._connections:
                try:
                    conn.close()
                except:
                    pass
            self._connections.clear()

# 全局连接管理器实例
_connection_manager: Optional[DatabaseConnectionManager] = None
_manager_lock = threading.Lock()

def get_connection_manager(config: Dict[str, Any]) -> DatabaseConnectionManager:
    """获取全局数据库连接管理器实例"""
    global _connection_manager
    
    with _manager_lock:
        if _connection_manager is None or _connection_manager._closed:
            _connection_manager = DatabaseConnectionManager(
                host=config['host'],
                user=config['user'],
                password=config['password'],
                db=config['db'],
                port=config.get('port', 3306),
                charset=config.get('charset', 'utf8')
            )
        return _connection_manager

def close_connection_manager():
    """关闭全局连接管理器"""
    global _connection_manager
    with _manager_lock:
        if _connection_manager:
            _connection_manager.close()
            _connection_manager = None
