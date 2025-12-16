#!/usr/bin/env python3
"""
爬虫启动器 - 解决路径问题
"""
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.append(str(project_root))

def start_article_spider():
    """启动文章爬虫"""
    try:
        # 切换到爬虫目录
        spider_dir = project_root / 'spider' / 'article_data'
        os.chdir(str(spider_dir))
        
        # 导入并启动爬虫
        from spider.article_data.article_spider import start
        start()
    except Exception as e:
        print(f"启动文章爬虫失败: {e}")

def start_comment_spider():
    """启动评论爬虫"""
    try:
        # 切换到爬虫目录
        spider_dir = project_root / 'spider' / 'comment_spider'
        os.chdir(str(spider_dir))
        
        # 导入并启动爬虫
        from spider.comment_spider.comment_spider import main
        main()
    except Exception as e:
        print(f"启动评论爬虫失败: {e}")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='爬虫启动器')
    parser.add_argument('--type', choices=['article', 'comment'], required=True, help='爬虫类型')
    
    args = parser.parse_args()
    
    if args.type == 'article':
        start_article_spider()
    elif args.type == 'comment':
        start_comment_spider()
