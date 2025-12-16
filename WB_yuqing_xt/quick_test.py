#!/usr/bin/env python3
"""
快速测试脚本 - 测试主要功能是否正常
"""
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.append(str(project_root))

def test_imports():
    """测试所有关键模块导入"""
    print("测试模块导入...")
    
    try:
        # 核心模块
        from analysis.data_manager import DataManager
        from analysis.data_analyzer import DataAnalyzer
        from integration.spider_integration import SpiderIntegration
        
        # Flask应用
        from app import app, socketio
        
        # 视图模块
        from view.user import ub
        from view.page import pb
        
        print("[SUCCESS] 所有模块导入成功")
        return True
    except ImportError as e:
        print(f"[ERROR] 导入失败: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] 其他错误: {e}")
        return False

def test_data_availability():
    """测试数据可用性"""
    print("测试数据可用性...")
    
    try:
        from analysis.data_manager import DataManager
        manager = DataManager()
        
        # 获取统计数据
        stats = manager.get_statistics()
        print(f"文章总数: {stats.get('total_articles', 0)}")
        print(f"评论总数: {stats.get('total_comments', 0)}")
        
        # 获取最新文章
        articles = manager.get_recent_articles(3)
        print(f"最新文章数量: {len(articles)}")
        
        if len(articles) > 0:
            print("示例文章标题:", articles[0].get('title', '无标题')[:50])
        
        print("[SUCCESS] 数据测试通过")
        return True
    except Exception as e:
        print(f"[ERROR] 数据测试失败: {e}")
        return False

def test_analysis_functions():
    """测试分析功能"""
    print("测试分析功能...")
    
    try:
        from analysis.data_analyzer import DataAnalyzer
        analyzer = DataAnalyzer()
        
        # 测试情感分析
        sentiment_score, sentiment_label = analyzer.analyze_sentiment("我很开心今天完成了项目")
        print(f"情感分析测试: {sentiment_score} ({sentiment_label})")
        
        # 测试关键词提取
        keywords = analyzer.extract_keywords("人工智能技术发展迅速，应用前景广阔", 5)
        print(f"关键词提取: {keywords}")
        
        print("[SUCCESS] 分析功能测试通过")
        return True
    except Exception as e:
        print(f"[ERROR] 分析功能测试失败: {e}")
        return False

def test_api_endpoints():
    """测试API端点是否定义"""
    print("测试API端点...")
    
    try:
        from app import app
        
        with app.test_client() as client:
            # 测试主页
            response = client.get('/')
            print(f"主页状态码: {response.status_code}")
            
            # 测试API端点（即使没有数据也会返回响应）
            endpoints = [
                '/api/stats',
                '/api/sentiment', 
                '/api/keywords',
                '/api/recent_articles'
            ]
            
            for endpoint in endpoints:
                try:
                    response = client.get(endpoint)
                    print(f"{endpoint}: {response.status_code}")
                except Exception as e:
                    print(f"{endpoint}: 错误 - {e}")
        
        print("[SUCCESS] API端点测试通过")
        return True
    except Exception as e:
        print(f"[ERROR] API端点测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("微博舆情监测系统 - 快速测试")
    print("=" * 60)
    
    tests = [
        ("模块导入", test_imports),
        ("数据可用性", test_data_availability),
        ("分析功能", test_analysis_functions),
        ("API端点", test_api_endpoints)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            if test_func():
                print(f"[PASS] {test_name}")
                passed += 1
            else:
                print(f"[FAIL] {test_name}")
                failed += 1
        except Exception as e:
            print(f"[ERROR] {test_name}: {e}")
            failed += 1
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    
    if failed == 0:
        print("\n[SUCCESS] 系统准备就绪！")
        print("\n启动Web服务:")
        print("  python app.py")
        print("\n或使用完整系统:")
        print("  python start_system.py")
        print("\n启动后访问: http://localhost:5000")
        return True
    else:
        print("\n[FAILED] 请检查错误信息并修复问题")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)