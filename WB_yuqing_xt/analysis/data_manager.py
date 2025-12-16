"""
数据管理器 - 负责数据的读取、存储和缓存
"""
import sqlite3
import csv
import json
import redis
from datetime import datetime, timedelta
import os
from typing import List, Dict, Any, Optional
import threading


class DataManager:
    def __init__(self, redis_host='localhost', redis_port=6379, redis_db=0):
        """初始化数据管理器"""
        self.db_path = 'data/analysis.db'
        self.article_csv_path = 'spider/article_data/article_data.csv'
        self.comment_csv_path = 'spider/comment_spider/comment_data.csv'
        
        # 初始化Redis连接（如果可用）
        try:
            self.redis_client = redis.Redis(host=redis_host, port=redis_port, db=redis_db, decode_responses=True)
            self.redis_client.ping()
            self.use_redis = True
            print("Redis连接成功")
        except:
            self.redis_client = None
            self.use_redis = False
            print("Redis不可用，使用内存缓存")
        
        # 内存缓存
        self.memory_cache = {}
        self.cache_lock = threading.Lock()
        
        # 初始化数据库
        self._init_database()
    
    def _init_database(self):
        """初始化SQLite数据库"""
        os.makedirs('data', exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建文章分析表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS article_analysis (
                id TEXT PRIMARY KEY,
                title TEXT,
                content TEXT,
                sentiment_score REAL,
                sentiment_label TEXT,
                keywords TEXT,
                created_at TEXT,
                analysis_time TEXT,
                reposts_count INTEGER,
                comments_count INTEGER,
                attitudes_count INTEGER,
                region_name TEXT,
                author_name TEXT
            )
        ''')
        
        # 创建关键词统计表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS keyword_stats (
                keyword TEXT PRIMARY KEY,
                count INTEGER,
                last_updated TEXT
            )
        ''')
        
        # 创建趋势数据表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trend_data (
                date TEXT,
                hour INTEGER,
                article_count INTEGER,
                positive_count INTEGER,
                negative_count INTEGER,
                neutral_count INTEGER,
                PRIMARY KEY (date, hour)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_recent_articles(self, limit: int = 10, category: str = None) -> List[Dict[str, Any]]:
        """获取最新文章数据"""
        cache_key = f"recent_articles_{limit}_{category or 'all'}"
        
        # 尝试从缓存获取
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            return cached_data
        
        articles = []
        try:
            if os.path.exists(self.article_csv_path):
                with open(self.article_csv_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    articles_list = list(reader)
                    
                    # 按创建时间排序，获取最新的文章
                    articles_list.sort(key=lambda x: x.get('created_at', ''), reverse=True)
                    
                    for article in articles_list:
                        # 如果指定了类别，进行过滤
                        if category and article.get('articleType', '') != category:
                            continue

                        articles.append({
                            'id': article.get('id', ''),
                            'title': article.get('title_raw', ''),
                            'reposts_count': int(article.get('reposts_count', 0)),
                            'comments_count': int(article.get('comments_count', 0)),
                            'attitudes_count': int(article.get('attitudes_count', 0)),
                            'region_name': article.get('region_name', ''),
                            'created_at': article.get('created_at', ''),
                            'author_name': article.get('authorName', ''),
                            'article_url': article.get('articleUrl', ''),
                            'article_type': article.get('articleType', '')
                        })

                        # 达到限制数量就停止
                        if len(articles) >= limit:
                            break
        except Exception as e:
            print(f"读取文章数据错误: {e}")
        
        # 缓存结果（缩短缓存时间）
        self._set_cache(cache_key, articles, expire_time=30)  # 30秒缓存
        return articles
    
    def get_all_articles(self) -> List[Dict[str, Any]]:
        """获取所有文章数据"""
        articles = []
        try:
            if os.path.exists(self.article_csv_path):
                with open(self.article_csv_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for article in reader:
                        articles.append({
                            'id': article.get('id', ''),
                            'title': article.get('title_raw', ''),
                            'reposts_count': int(article.get('reposts_count', 0)),
                            'comments_count': int(article.get('comments_count', 0)),
                            'attitudes_count': int(article.get('attitudes_count', 0)),
                            'region_name': article.get('region_name', ''),
                            'created_at': article.get('created_at', ''),
                            'author_name': article.get('authorName', ''),
                            'article_type': article.get('articleType', ''),
                            'article_url': article.get('articleUrl', '')
                        })
        except Exception as e:
            print(f"读取文章数据错误: {e}")
        
        return articles
    
    def get_comments_by_article_id(self, article_id: str) -> List[Dict[str, Any]]:
        """根据文章ID获取评论数据"""
        comments = []
        try:
            if os.path.exists(self.comment_csv_path):
                with open(self.comment_csv_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for comment in reader:
                        if comment.get('articleId') == article_id:
                            comments.append({
                                'id': comment.get('id', ''),
                                'text': comment.get('text_raw', ''),
                                'created_at': comment.get('created_at', ''),
                                'like_counts': int(comment.get('like_counts', 0)),
                                'user_name': comment.get('userName', ''),
                                'gender': comment.get('gender', ''),
                                'source': comment.get('source', '')
                            })
        except Exception as e:
            print(f"读取评论数据错误: {e}")
        
        return comments
    
    def save_analysis_result(self, article_id: str, analysis_data: Dict[str, Any]):
        """保存分析结果到数据库"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO article_analysis 
                (id, title, content, sentiment_score, sentiment_label, keywords, 
                 created_at, analysis_time, reposts_count, comments_count, 
                 attitudes_count, region_name, author_name)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                article_id,
                analysis_data.get('title', ''),
                analysis_data.get('content', ''),
                analysis_data.get('sentiment_score', 0.0),
                analysis_data.get('sentiment_label', ''),
                json.dumps(analysis_data.get('keywords', []), ensure_ascii=False),
                analysis_data.get('created_at', ''),
                datetime.now().isoformat(),
                analysis_data.get('reposts_count', 0),
                analysis_data.get('comments_count', 0),
                analysis_data.get('attitudes_count', 0),
                analysis_data.get('region_name', ''),
                analysis_data.get('author_name', '')
            ))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"保存分析结果错误: {e}")
    
    def _get_from_cache(self, key: str) -> Optional[Any]:
        """从缓存获取数据"""
        if self.use_redis:
            try:
                data = self.redis_client.get(key)
                if data:
                    return json.loads(data)
            except:
                pass
        
        # 使用内存缓存
        with self.cache_lock:
            cache_item = self.memory_cache.get(key)
            if cache_item:
                if datetime.now() < cache_item['expire_time']:
                    return cache_item['data']
                else:
                    del self.memory_cache[key]
        
        return None
    
    def _set_cache(self, key: str, data: Any, expire_time: int = 300):
        """设置缓存数据"""
        if self.use_redis:
            try:
                self.redis_client.setex(key, expire_time, json.dumps(data, ensure_ascii=False))
                return
            except:
                pass
        
        # 使用内存缓存
        with self.cache_lock:
            self.memory_cache[key] = {
                'data': data,
                'expire_time': datetime.now() + timedelta(seconds=expire_time)
            }
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取基本统计信息"""
        cache_key = "basic_statistics"
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            return cached_data
        
        stats = {
            'total_articles': 0,
            'total_comments': 0,
            'today_articles': 0,
            'today_comments': 0
        }
        
        try:
            # 统计文章数量
            if os.path.exists(self.article_csv_path):
                with open(self.article_csv_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    articles = list(reader)
                    stats['total_articles'] = len(articles)
                    
                    # 统计今日文章
                    today = datetime.now().strftime('%Y-%m-%d')
                    stats['today_articles'] = sum(1 for article in articles 
                                                if article.get('created_at', '').startswith(today))
            
            # 统计评论数量
            if os.path.exists(self.comment_csv_path):
                with open(self.comment_csv_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    comments = list(reader)
                    stats['total_comments'] = len(comments)
                    
                    # 统计今日评论
                    today = datetime.now().strftime('%Y-%m-%d')
                    stats['today_comments'] = sum(1 for comment in comments 
                                                if comment.get('created_at', '').startswith(today))
        
        except Exception as e:
            print(f"获取统计信息错误: {e}")
        
        # 缓存结果（缩短缓存时间）
        self._set_cache(cache_key, stats, expire_time=30)
        return stats

    def get_article_categories(self) -> List[Dict[str, Any]]:
        """获取文章类别统计"""
        cache_key = "article_categories"
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            return cached_data

        categories = {}
        try:
            if os.path.exists(self.article_csv_path):
                with open(self.article_csv_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for article in reader:
                        category = article.get('articleType', '未分类')
                        if category not in categories:
                            categories[category] = {'count': 0, 'name': category}
                        categories[category]['count'] += 1
        except Exception as e:
            print(f"获取文章类别错误: {e}")

        result = list(categories.values())
        result.sort(key=lambda x: x['count'], reverse=True)

        # 缓存结果
        self._set_cache(cache_key, result, expire_time=300)
        return result

    def get_article_detail(self, article_id: str) -> Dict[str, Any]:
        """获取文章详情"""
        try:
            # 获取文章基本信息
            article_info = None
            if os.path.exists(self.article_csv_path):
                with open(self.article_csv_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for article in reader:
                        if article.get('id') == article_id:
                            article_info = {
                                'id': article.get('id', ''),
                                'title': article.get('title_raw', ''),
                                'reposts_count': int(article.get('reposts_count', 0)),
                                'comments_count': int(article.get('comments_count', 0)),
                                'attitudes_count': int(article.get('attitudes_count', 0)),
                                'region_name': article.get('region_name', ''),
                                'created_at': article.get('created_at', ''),
                                'author_name': article.get('authorName', ''),
                                'author_id': article.get('authorId', ''),
                                'article_type': article.get('articleType', ''),
                                'article_url': article.get('articleUrl', ''),
                                'author_home_url': article.get('authorHomeUrl', '')
                            }
                            break

            if not article_info:
                return {'error': '文章不存在'}

            # 获取评论信息
            comments = self.get_comments_by_article_id(article_id)
            article_info['comments'] = comments
            article_info['comment_count'] = len(comments)

            return article_info

        except Exception as e:
            print(f"获取文章详情错误: {e}")
            return {'error': str(e)}
