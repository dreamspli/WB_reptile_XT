#!/usr/bin/env python3
"""
测试数据更新脚本
"""
import sys
import time
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from analysis.data_manager import DataManager
from analysis.data_analyzer import DataAnalyzer

def test_data_updates():
    """测试数据更新"""
    print("测试数据更新...")
    
    dm = DataManager()
    da = DataAnalyzer()
    
    print("=" * 50)
    
    # 测试多次获取数据，观察变化
    for i in range(5):
        print(f"\n第 {i+1} 次测试:")
        print("-" * 30)
        
        # 获取统计数据
        stats = dm.get_statistics()
        print(f"总文章数: {stats['total_articles']}")
        print(f"今日文章: {stats['today_articles']}")
        
        # 获取最新文章
        articles = dm.get_recent_articles(3)
        print(f"最新文章数: {len(articles)}")
        if articles:
            print(f"最新文章标题: {articles[0]['title'][:30]}...")
        
        # 获取关键词
        keywords = da.get_top_keywords(5)
        print(f"热门关键词: {[kw['keyword'] for kw in keywords[:3]]}")
        
        if i < 4:  # 最后一次不等待
            print("等待10秒...")
            time.sleep(10)
    
    print("\n" + "=" * 50)
    print("测试完成")

if __name__ == '__main__':
    test_data_updates()
