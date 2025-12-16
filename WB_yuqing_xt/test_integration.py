#!/usr/bin/env python3
"""
测试系统集成脚本
"""
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.append(str(project_root))

def test_data_manager():
    """测试数据管理器"""
    print("测试数据管理器...")
    try:
        from analysis.data_manager import DataManager
        manager = DataManager()
        stats = manager.get_statistics()
        print(f"统计数据: {stats}")
        
        articles = manager.get_recent_articles(5)
        print(f"最新文章数量: {len(articles)}")
        
        return True
    except Exception as e:
        print(f"数据管理器测试失败: {e}")
        return False

def test_data_analyzer():
    """测试数据分析器"""
    print("测试数据分析器...")
    try:
        from analysis.data_analyzer import DataAnalyzer
        analyzer = DataAnalyzer()
        
        # 测试情感分析
        sentiment_score, sentiment_label = analyzer.analyze_sentiment("今天天气很好，心情愉快")
        print(f"情感分析测试: {sentiment_score}, {sentiment_label}")
        
        # 测试关键词提取
        keywords = analyzer.extract_keywords("这是一个关于科技创新和发展的重要话题", 5)
        print(f"关键词提取测试: {keywords}")
        
        return True
    except Exception as e:
        print(f"数据分析器测试失败: {e}")
        return False

def test_spider_integration():
    """测试爬虫集成"""
    print("测试爬虫集成...")
    try:
        from integration.spider_integration import SpiderIntegration
        integration = SpiderIntegration()
        print("爬虫集成器初始化成功")
        return True
    except Exception as e:
        print(f"爬虫集成测试失败: {e}")
        return False

def test_imports():
    """测试所有导入"""
    print("测试核心模块导入...")
    try:
        import jieba
        import pandas
        import numpy
        import flask
        import redis
        print("所有依赖模块导入成功")
        return True
    except ImportError as e:
        print(f"导入失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 50)
    print("微博舆情监测系统 - 集成测试")
    print("=" * 50)
    
    tests = [
        ("依赖导入", test_imports),
        ("数据管理器", test_data_manager),
        ("数据分析器", test_data_analyzer),
        ("爬虫集成", test_spider_integration)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            if test_func():
                print(f"[PASS] {test_name} 通过")
                passed += 1
            else:
                print(f"[FAIL] {test_name} 失败")
                failed += 1
        except Exception as e:
            print(f"[ERROR] {test_name} 异常: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    print("=" * 50)
    
    if failed == 0:
        print("[SUCCESS] 所有测试通过，系统准备就绪！")
        print("\n启动命令:")
        print("  python start_system.py      # 启动完整系统")
        print("  python start_web.py         # 仅启动Web服务")
        print("  python app.py               # 直接启动Flask应用")
        return True
    else:
        print("[FAILED] 部分测试失败，请检查错误信息")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)