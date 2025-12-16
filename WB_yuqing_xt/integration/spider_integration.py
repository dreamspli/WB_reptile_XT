"""
爬虫集成模块 - 将爬虫数据与分析系统集成
"""
import sys
import os
import threading
import time
import csv
from datetime import datetime
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from analysis.data_analyzer import DataAnalyzer
from analysis.data_manager import DataManager


class SpiderIntegration:
    def __init__(self):
        """初始化爬虫集成器"""
        self.data_manager = DataManager()
        self.data_analyzer = DataAnalyzer()
        
        # 文件路径
        self.article_csv_path = project_root / 'spider' / 'article_data' / 'article_data.csv'
        self.comment_csv_path = project_root / 'spider' / 'comment_spider' / 'comment_data.csv'
        
        # 记录上次处理的文件修改时间
        self.last_article_mtime = 0
        self.last_comment_mtime = 0
        
        # 处理状态
        self.is_running = False
        self.processing_thread = None
        
        print("爬虫集成器初始化完成")
    
    def start_monitoring(self):
        """开始监控文件变化"""
        if self.is_running:
            print("监控已在运行中")
            return
        
        self.is_running = True
        self.processing_thread = threading.Thread(target=self._monitor_files)
        self.processing_thread.daemon = True
        self.processing_thread.start()
        
        print("开始监控爬虫数据文件变化...")
    
    def stop_monitoring(self):
        """停止监控"""
        self.is_running = False
        if self.processing_thread:
            self.processing_thread.join()
        print("停止监控")
    
    def _monitor_files(self):
        """监控文件变化的主循环"""
        # 初始化文件修改时间
        if self.article_csv_path.exists():
            self.last_article_mtime = self.article_csv_path.stat().st_mtime
        if self.comment_csv_path.exists():
            self.last_comment_mtime = self.comment_csv_path.stat().st_mtime

        while self.is_running:
            try:
                # 检查文章文件是否有更新
                if self.article_csv_path.exists():
                    current_mtime = self.article_csv_path.stat().st_mtime
                    if current_mtime > self.last_article_mtime:
                        print(f"检测到文章数据更新: {datetime.now()}")
                        self._process_new_articles()
                        self.last_article_mtime = current_mtime

                        # 清除相关缓存
                        self._clear_cache()

                # 检查评论文件是否有更新
                if self.comment_csv_path.exists():
                    current_mtime = self.comment_csv_path.stat().st_mtime
                    if current_mtime > self.last_comment_mtime:
                        print(f"检测到评论数据更新: {datetime.now()}")
                        self._process_new_comments()
                        self.last_comment_mtime = current_mtime

                        # 清除相关缓存
                        self._clear_cache()

                # 每10秒检查一次（更频繁）
                time.sleep(10)

            except Exception as e:
                print(f"监控过程中出错: {e}")
                time.sleep(30)  # 出错后等待更长时间
    
    def _process_new_articles(self):
        """处理新的文章数据"""
        try:
            # 获取最新的文章数据
            recent_articles = self.data_manager.get_recent_articles(50)
            
            processed_count = 0
            for article in recent_articles:
                # 分析文章情感和关键词
                title = article.get('title', '')
                if title:
                    # 情感分析
                    sentiment_score, sentiment_label = self.data_analyzer.analyze_sentiment(title)
                    
                    # 关键词提取
                    keywords = self.data_analyzer.extract_keywords(title, 5)
                    
                    # 准备分析数据
                    analysis_data = {
                        'title': title,
                        'content': title,  # 目前使用标题作为内容
                        'sentiment_score': sentiment_score,
                        'sentiment_label': sentiment_label,
                        'keywords': keywords,
                        'created_at': article.get('created_at', ''),
                        'reposts_count': article.get('reposts_count', 0),
                        'comments_count': article.get('comments_count', 0),
                        'attitudes_count': article.get('attitudes_count', 0),
                        'region_name': article.get('region_name', ''),
                        'author_name': article.get('author_name', '')
                    }
                    
                    # 保存分析结果
                    self.data_manager.save_analysis_result(article['id'], analysis_data)
                    processed_count += 1
            
            if processed_count > 0:
                print(f"处理了 {processed_count} 篇新文章")
                
        except Exception as e:
            print(f"处理文章数据时出错: {e}")
    
    def _process_new_comments(self):
        """处理新的评论数据"""
        try:
            # 这里可以添加评论数据的处理逻辑
            # 例如：评论情感分析、热门评论识别等
            print("评论数据已更新，可在此添加评论分析逻辑")
            
        except Exception as e:
            print(f"处理评论数据时出错: {e}")

    def _clear_cache(self):
        """清除数据管理器的缓存"""
        try:
            # 清除内存缓存
            with self.data_manager.cache_lock:
                self.data_manager.memory_cache.clear()

            # 如果使用Redis，也清除Redis缓存
            if self.data_manager.use_redis:
                try:
                    # 清除特定的缓存键
                    cache_keys = [
                        "recent_articles_*",
                        "basic_statistics",
                        "sentiment_*",
                        "keywords_*"
                    ]
                    for pattern in cache_keys:
                        keys = self.data_manager.redis_client.keys(pattern)
                        if keys:
                            self.data_manager.redis_client.delete(*keys)
                except:
                    pass

            print("缓存已清除")
        except Exception as e:
            print(f"清除缓存时出错: {e}")

    def manual_process_all(self):
        """手动处理所有现有数据"""
        print("开始手动处理所有数据...")
        
        try:
            # 处理所有文章
            all_articles = self.data_manager.get_all_articles()
            print(f"找到 {len(all_articles)} 篇文章需要处理")
            
            processed_count = 0
            for i, article in enumerate(all_articles):
                if i % 100 == 0:
                    print(f"处理进度: {i}/{len(all_articles)}")
                
                title = article.get('title', '')
                if title:
                    # 情感分析
                    sentiment_score, sentiment_label = self.data_analyzer.analyze_sentiment(title)
                    
                    # 关键词提取
                    keywords = self.data_analyzer.extract_keywords(title, 5)
                    
                    # 准备分析数据
                    analysis_data = {
                        'title': title,
                        'content': title,
                        'sentiment_score': sentiment_score,
                        'sentiment_label': sentiment_label,
                        'keywords': keywords,
                        'created_at': article.get('created_at', ''),
                        'reposts_count': article.get('reposts_count', 0),
                        'comments_count': article.get('comments_count', 0),
                        'attitudes_count': article.get('attitudes_count', 0),
                        'region_name': article.get('region_name', ''),
                        'author_name': article.get('author_name', '')
                    }
                    
                    # 保存分析结果
                    self.data_manager.save_analysis_result(article['id'], analysis_data)
                    processed_count += 1
            
            print(f"手动处理完成，共处理 {processed_count} 篇文章")
            
        except Exception as e:
            print(f"手动处理数据时出错: {e}")
    
    def get_processing_status(self):
        """获取处理状态"""
        return {
            'is_running': self.is_running,
            'last_article_check': datetime.fromtimestamp(self.last_article_mtime).isoformat() if self.last_article_mtime > 0 else None,
            'last_comment_check': datetime.fromtimestamp(self.last_comment_mtime).isoformat() if self.last_comment_mtime > 0 else None,
            'article_file_exists': self.article_csv_path.exists(),
            'comment_file_exists': self.comment_csv_path.exists()
        }


def main():
    """主函数 - 可以作为独立脚本运行"""
    integration = SpiderIntegration()
    
    # 首先手动处理所有现有数据
    integration.manual_process_all()
    
    # 开始监控新数据
    integration.start_monitoring()
    
    try:
        # 保持程序运行
        while True:
            status = integration.get_processing_status()
            print(f"监控状态: {status}")
            time.sleep(300)  # 每5分钟打印一次状态
            
    except KeyboardInterrupt:
        print("收到中断信号，正在停止...")
        integration.stop_monitoring()


if __name__ == '__main__':
    main()
