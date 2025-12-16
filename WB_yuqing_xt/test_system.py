#!/usr/bin/env python3
"""
系统测试脚本 - 验证各个模块的功能
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
        
        dm = DataManager()
        
        # 测试获取统计信息
        stats = dm.get_statistics()
        print(f"统计信息: {stats}")
        
        # 测试获取最新文章
        articles = dm.get_recent_articles(5)
        print(f"获取到 {len(articles)} 篇最新文章")
        
        print("✓ 数据管理器测试通过")
        return True
        
    except Exception as e:
        print(f"✗ 数据管理器测试失败: {e}")
        return False

def test_data_analyzer():
    """测试数据分析器"""
    print("测试数据分析器...")
    try:
        from analysis.data_analyzer import DataAnalyzer
        
        analyzer = DataAnalyzer()
        
        # 测试情感分析
        test_text = "这个产品真的很好用，我很喜欢"
        sentiment_score, sentiment_label = analyzer.analyze_sentiment(test_text)
        print(f"情感分析结果: {sentiment_score}, {sentiment_label}")
        
        # 测试关键词提取
        keywords = analyzer.extract_keywords(test_text, 5)
        print(f"关键词: {keywords}")
        
        # 测试实时统计
        stats = analyzer.get_real_time_stats()
        print(f"实时统计: {stats}")
        
        print("✓ 数据分析器测试通过")
        return True
        
    except Exception as e:
        print(f"✗ 数据分析器测试失败: {e}")
        return False

def test_spider_integration():
    """测试爬虫集成"""
    print("测试爬虫集成...")
    try:
        from integration.spider_integration import SpiderIntegration
        
        integration = SpiderIntegration()
        
        # 测试获取处理状态
        status = integration.get_processing_status()
        print(f"处理状态: {status}")
        
        print("✓ 爬虫集成测试通过")
        return True
        
    except Exception as e:
        print(f"✗ 爬虫集成测试失败: {e}")
        return False

def test_web_app():
    """测试Web应用"""
    print("测试Web应用...")
    try:
        # 简单导入测试
        import app
        print("✓ Web应用导入成功")
        return True
        
    except Exception as e:
        print(f"✗ Web应用测试失败: {e}")
        return False

def check_dependencies():
    """检查依赖包"""
    print("检查依赖包...")
    
    required_packages = [
        ('flask', 'Flask'),
        ('flask_socketio', 'Flask-SocketIO'),
        ('jieba', 'jieba'),
        ('requests', 'requests'),
    ]
    
    optional_packages = [
        ('redis', 'redis'),
        ('pandas', 'pandas'),
        ('numpy', 'numpy'),
    ]
    
    missing_required = []
    missing_optional = []
    
    for package_name, display_name in required_packages:
        try:
            __import__(package_name)
            print(f"✓ {display_name}")
        except ImportError:
            print(f"✗ {display_name} (必需)")
            missing_required.append(display_name)
    
    for package_name, display_name in optional_packages:
        try:
            __import__(package_name)
            print(f"✓ {display_name}")
        except ImportError:
            print(f"- {display_name} (可选)")
            missing_optional.append(display_name)
    
    if missing_required:
        print(f"\n缺少必需的依赖包: {', '.join(missing_required)}")
        print("请运行: pip install -r requirements.txt")
        return False
    
    if missing_optional:
        print(f"\n缺少可选的依赖包: {', '.join(missing_optional)}")
        print("这些包不是必需的，但可以提供额外功能")
    
    return True

def check_file_structure():
    """检查文件结构"""
    print("检查文件结构...")
    
    required_files = [
        'app.py',
        'start_system.py',
        'requirements.txt',
        'analysis/__init__.py',
        'analysis/data_manager.py',
        'analysis/data_analyzer.py',
        'integration/__init__.py',
        'integration/spider_integration.py',
        'templates/dashboard.html',
        'static/css/dashboard.css',
        'static/js/dashboard.js',
        'spider/article_data/article_spider.py',
        'spider/comment_spider/comment_spider.py',
        'util/stringUtil.py'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path}")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n缺少文件: {', '.join(missing_files)}")
        return False
    
    return True

def create_sample_data():
    """创建示例数据"""
    print("创建示例数据...")
    
    try:
        # 创建数据目录
        data_dir = project_root / 'data'
        data_dir.mkdir(exist_ok=True)
        
        # 创建spider数据目录
        spider_article_dir = project_root / 'spider' / 'article_data'
        spider_comment_dir = project_root / 'spider' / 'comment_spider'
        
        spider_article_dir.mkdir(parents=True, exist_ok=True)
        spider_comment_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建示例CSV文件（如果不存在）
        article_csv = spider_article_dir / 'article_data.csv'
        if not article_csv.exists():
            import csv
            with open(article_csv, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    "id", "title_raw", "reposts_count", "comments_count", 
                    "attitudes_count", "region_name", "created_at", "articleType",
                    "articleUrl", "authorId", "authorName", "authorHomeUrl"
                ])
                # 添加一些示例数据
                writer.writerow([
                    "1", "这是一个测试微博内容", "10", "5", "20", "北京", 
                    "2024-01-01 12:00:00", "热门", "http://example.com", 
                    "user1", "测试用户", "http://example.com/user1"
                ])
        
        comment_csv = spider_comment_dir / 'comment_data.csv'
        if not comment_csv.exists():
            import csv
            with open(comment_csv, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'articleId', 'id', 'text_raw', 'created_at', 'source',
                    'like_counts', 'userId', 'userName', 'gender', 'userHomeUrl'
                ])
                # 添加一些示例数据
                writer.writerow([
                    "1", "comment1", "这是一个测试评论", "2024-01-01 12:05:00",
                    "微博网页版", "3", "user2", "评论用户", "男", "http://example.com/user2"
                ])
        
        print("✓ 示例数据创建完成")
        return True
        
    except Exception as e:
        print(f"✗ 创建示例数据失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 50)
    print("微博舆情监测系统 - 系统测试")
    print("=" * 50)
    
    tests = [
        ("文件结构检查", check_file_structure),
        ("依赖包检查", check_dependencies),
        ("示例数据创建", create_sample_data),
        ("数据管理器", test_data_manager),
        ("数据分析器", test_data_analyzer),
        ("爬虫集成", test_spider_integration),
        ("Web应用", test_web_app),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 30)
        if test_func():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"测试结果: {passed}/{total} 通过")
    print("=" * 50)
    
    if passed == total:
        print("✓ 所有测试通过！系统可以正常运行。")
        print("\n启动系统:")
        print("python start_system.py")
    else:
        print("✗ 部分测试失败，请检查上述错误信息。")
        return False
    
    return True

if __name__ == '__main__':
    main()
