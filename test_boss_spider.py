#!/usr/bin/python
# -*- coding:utf-8 -*-
"""
Boss直聘爬虫测试文件
"""
import json
import pytest
from boss_selenium_copy import create_browser, city_map, ENVIRONMENT

def test_config_loading():
    """测试配置文件加载"""
    try:
        with open('config.json', 'r') as f:
            configs = json.load(f)
        assert 'production' in configs
        assert 'testing' in configs
        assert 'development' in configs
        print("✓ 配置文件加载测试通过")
    except Exception as e:
        pytest.fail(f"配置文件加载失败: {e}")

def test_database_config():
    """测试数据库配置"""
    try:
        with open('config.json', 'r') as f:
            configs = json.load(f)
        
        db_config = configs.get(ENVIRONMENT)
        assert db_config is not None, "未找到环境 '{}' 的配置".format(ENVIRONMENT)
        assert 'host' in db_config
        assert 'user' in db_config
        assert 'password' in db_config
        assert 'db' in db_config
        print("✓ 数据库配置测试通过 (环境: {})".format(ENVIRONMENT))
    except Exception as e:
        pytest.fail(f"数据库配置测试失败: {e}")

def test_city_mapping():
    """测试城市映射"""
    assert len(city_map) > 0, "城市映射不能为空"
    assert "北京" in city_map, "应该包含北京"
    assert "广东" in city_map, "应该包含广东"
    assert "广州" in city_map["广东"], "广东应该包含广州"
    print("✓ 城市映射测试通过")

def test_browser_creation_function():
    """测试浏览器创建函数存在"""
    assert callable(create_browser), "create_browser函数应该存在"
    print("✓ 浏览器创建函数测试通过")

def test_environment_variable():
    """测试环境变量"""
    assert ENVIRONMENT in ['production', 'testing', 'development'], "环境变量值无效: {}".format(ENVIRONMENT)
    print("✓ 环境变量测试通过: {}".format(ENVIRONMENT))

def test_city_province_mapping():
    """测试城市到省份的映射逻辑"""
    # 测试几个主要城市
    test_cases = [
        ("北京", "北京"),
        ("广州", "广东"),
        ("上海", "上海"),
        ("深圳", "广东"),
        ("杭州", "浙江")
    ]
    
    for city, expected_province in test_cases:
        found_province = ''
        for province, cities in city_map.items():
            if city in cities:
                found_province = province
                break
        assert found_province == expected_province, "城市 {} 应该映射到 {}，但映射到了 {}".format(city, expected_province, found_province)
    
    print("✓ 城市省份映射测试通过")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
