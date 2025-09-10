#!/usr/bin/python
# -*- coding:utf-8 -*-
"""
Python版本兼容性检查脚本
"""
import sys

def check_python_version():
    """检查Python版本"""
    version = sys.version_info
    print("当前Python版本: {}.{}.{}".format(version.major, version.minor, version.micro))
    
    if version.major < 3:
        print("❌ 错误: 需要Python 3.0或更高版本")
        return False
    elif version.major == 3 and version.minor < 6:
        print("⚠️  警告: Python版本较低，不支持f-string语法")
        print("   建议升级到Python 3.6+以获得更好的性能")
        return True
    else:
        print("✅ Python版本兼容")
        return True

def check_dependencies():
    """检查依赖包"""
    required_packages = ['selenium', 'mysql-connector-python']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print("✅ {} 已安装".format(package))
        except ImportError:
            print("❌ {} 未安装".format(package))
            missing_packages.append(package)
    
    if missing_packages:
        print("\n请安装缺失的包:")
        print("pip install {}".format(' '.join(missing_packages)))
        return False
    return True

def main():
    print("=== Boss直聘爬虫环境检查 ===\n")
    
    # 检查Python版本
    print("1. 检查Python版本:")
    version_ok = check_python_version()
    print()
    
    # 检查依赖包
    print("2. 检查依赖包:")
    deps_ok = check_dependencies()
    print()
    
    # 总结
    if version_ok and deps_ok:
        print("🎉 环境检查通过！可以运行爬虫程序")
        print("运行命令: python boss_selenium_copy.py")
    else:
        print("❌ 环境检查失败，请解决上述问题后重试")

if __name__ == "__main__":
    main()
