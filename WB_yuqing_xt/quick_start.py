#!/usr/bin/env python3
"""
快速启动脚本 - 用于演示和测试
"""
import os
import sys
import time
import webbrowser
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.append(str(project_root))

def check_dependencies():
    """检查必要的依赖"""
    required_packages = ['flask', 'flask_socketio', 'jieba', 'requests']
    missing = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"❌ 缺少依赖包: {', '.join(missing)}")
        print("请运行: pip install -r requirements.txt")
        return False
    
    print("✅ 依赖检查通过")
    return True

def check_data_files():
    """检查数据文件"""
    article_csv = project_root / 'spider' / 'article_data' / 'article_data.csv'
    
    if not article_csv.exists():
        print("⚠️  未找到文章数据文件，将创建示例数据...")
        create_sample_data()
    else:
        print("✅ 数据文件存在")
    
    return True

def create_sample_data():
    """创建示例数据"""
    import csv
    from datetime import datetime, timedelta
    
    # 创建目录
    article_dir = project_root / 'spider' / 'article_data'
    comment_dir = project_root / 'spider' / 'comment_spider'
    article_dir.mkdir(parents=True, exist_ok=True)
    comment_dir.mkdir(parents=True, exist_ok=True)
    
    # 创建示例文章数据
    article_csv = article_dir / 'article_data.csv'
    with open(article_csv, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            "id", "title_raw", "reposts_count", "comments_count", 
            "attitudes_count", "region_name", "created_at", "articleType",
            "articleUrl", "authorId", "authorName", "authorHomeUrl"
        ])
        
        # 生成示例数据
        sample_data = [
            ["1", "今天天气真好，心情也很棒！", "15", "8", "32", "北京", 
             (datetime.now() - timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S'), "生活",
             "http://example.com/1", "user1", "小明", "http://example.com/user1"],
            ["2", "新的科技产品发布了，功能很强大", "25", "12", "45", "上海",
             (datetime.now() - timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S'), "科技",
             "http://example.com/2", "user2", "科技达人", "http://example.com/user2"],
            ["3", "这部电影真的很感人，推荐大家去看", "18", "6", "28", "广州",
             (datetime.now() - timedelta(hours=3)).strftime('%Y-%m-%d %H:%M:%S'), "娱乐",
             "http://example.com/3", "user3", "影评人", "http://example.com/user3"],
            ["4", "今天的股市表现不错，投资需谨慎", "8", "15", "12", "深圳",
             (datetime.now() - timedelta(hours=4)).strftime('%Y-%m-%d %H:%M:%S'), "财经",
             "http://example.com/4", "user4", "财经专家", "http://example.com/user4"],
            ["5", "健康饮食很重要，大家要注意营养搭配", "12", "9", "22", "杭州",
             (datetime.now() - timedelta(hours=5)).strftime('%Y-%m-%d %H:%M:%S'), "健康",
             "http://example.com/5", "user5", "营养师", "http://example.com/user5"]
        ]
        
        for data in sample_data:
            writer.writerow(data)
    
    # 创建示例评论数据
    comment_csv = comment_dir / 'comment_data.csv'
    with open(comment_csv, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'articleId', 'id', 'text_raw', 'created_at', 'source',
            'like_counts', 'userId', 'userName', 'gender', 'userHomeUrl'
        ])
        
        # 生成示例评论
        sample_comments = [
            ["1", "comment1", "确实是好天气！", 
             (datetime.now() - timedelta(minutes=30)).strftime('%Y-%m-%d %H:%M:%S'),
             "微博网页版", "5", "commenter1", "路人甲", "男", "http://example.com/commenter1"],
            ["1", "comment2", "心情好最重要", 
             (datetime.now() - timedelta(minutes=25)).strftime('%Y-%m-%d %H:%M:%S'),
             "微博手机版", "3", "commenter2", "路人乙", "女", "http://example.com/commenter2"],
            ["2", "comment3", "科技改变生活", 
             (datetime.now() - timedelta(minutes=20)).strftime('%Y-%m-%d %H:%M:%S'),
             "微博网页版", "8", "commenter3", "科技迷", "男", "http://example.com/commenter3"]
        ]
        
        for comment in sample_comments:
            writer.writerow(comment)
    
    print("✅ 示例数据创建完成")

def start_system():
    """启动系统"""
    print("\n🚀 启动微博舆情监测系统...")
    print("=" * 50)
    
    try:
        from integration.spider_integration import SpiderIntegration
        from app import app, socketio
        import threading
        
        # 启动数据集成服务
        print("📊 启动数据集成服务...")
        integration = SpiderIntegration()
        integration.manual_process_all()
        integration.start_monitoring()
        
        # 启动Web应用
        print("🌐 启动Web应用...")
        
        def run_app():
            socketio.run(app, debug=False, host='0.0.0.0', port=5000, use_reloader=False)
        
        app_thread = threading.Thread(target=run_app)
        app_thread.daemon = True
        app_thread.start()
        
        # 等待服务启动
        time.sleep(3)
        
        print("\n" + "=" * 50)
        print("🎉 系统启动成功！")
        print("=" * 50)
        print("📱 访问地址:")
        print("   基础版: http://localhost:5000")
        print("   增强版: http://localhost:5000/enhanced")
        print("   状态页: http://localhost:5000/status")
        print("\n💡 提示: 推荐使用增强版界面")
        print("⏹️  按 Ctrl+C 停止服务")
        print("=" * 50)
        
        # 自动打开浏览器
        try:
            webbrowser.open('http://localhost:5000/enhanced')
        except:
            pass
        
        # 保持运行
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n🛑 正在停止服务...")
            integration.stop_monitoring()
            print("✅ 服务已停止")
            
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        return False
    
    return True

def main():
    """主函数"""
    print("🔍 微博舆情监测系统 - 快速启动")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        return
    
    # 检查数据文件
    if not check_data_files():
        return
    
    # 启动系统
    start_system()

if __name__ == '__main__':
    main()
