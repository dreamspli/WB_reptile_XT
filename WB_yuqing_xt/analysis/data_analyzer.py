"""
数据分析器 - 负责数据的分析处理
"""
import jieba
import jieba.analyse
from collections import Counter, defaultdict
from datetime import datetime, timedelta
import re
import math
from typing import List, Dict, Any, Tuple
from .data_manager import DataManager


class DataAnalyzer:
    def __init__(self):
        """初始化数据分析器"""
        self.data_manager = DataManager()
        
        # 初始化jieba分词
        jieba.initialize()
        
        # 情感词典（简化版本）
        self.positive_words = {
            '好', '棒', '赞', '优秀', '完美', '喜欢', '爱', '支持', '满意', '开心',
            '高兴', '快乐', '幸福', '美好', '精彩', '优质', '不错', '给力', '厉害', '牛'
        }
        
        self.negative_words = {
            '差', '烂', '垃圾', '讨厌', '恨', '反对', '不满', '愤怒', '生气', '失望',
            '糟糕', '恶心', '无聊', '浪费', '骗子', '假', '黑', '坑', '坏', '臭'
        }
        
        # 停用词
        self.stop_words = {
            '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一',
            '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有',
            '看', '好', '自己', '这', '那', '里', '就是', '还是', '为了', '还有', '可以',
            '这个', '那个', '什么', '怎么', '现在', '知道', '应该', '可能', '已经', '如果'
        }
    
    def analyze_sentiment(self, text: str) -> Tuple[float, str]:
        """
        分析文本情感
        返回: (情感分数, 情感标签)
        情感分数: -1到1之间，负数表示负面，正数表示正面
        """
        if not text:
            return 0.0, 'neutral'
        
        # 分词
        words = jieba.lcut(text)
        
        positive_count = 0
        negative_count = 0
        total_words = len(words)
        
        for word in words:
            if word in self.positive_words:
                positive_count += 1
            elif word in self.negative_words:
                negative_count += 1
        
        if total_words == 0:
            return 0.0, 'neutral'
        
        # 计算情感分数
        sentiment_score = (positive_count - negative_count) / total_words
        
        # 确定情感标签
        if sentiment_score > 0.1:
            sentiment_label = 'positive'
        elif sentiment_score < -0.1:
            sentiment_label = 'negative'
        else:
            sentiment_label = 'neutral'
        
        return sentiment_score, sentiment_label
    
    def extract_keywords(self, text: str, top_k: int = 10) -> List[str]:
        """提取关键词"""
        if not text:
            return []
        
        # 使用TF-IDF提取关键词
        keywords = jieba.analyse.extract_tags(text, topK=top_k, withWeight=False)
        
        # 过滤停用词
        filtered_keywords = [kw for kw in keywords if kw not in self.stop_words and len(kw) > 1]
        
        return filtered_keywords[:top_k]
    
    def get_real_time_stats(self) -> Dict[str, Any]:
        """获取实时统计数据"""
        stats = self.data_manager.get_statistics()
        
        # 获取最新文章进行情感分析
        recent_articles = self.data_manager.get_recent_articles(100)
        
        sentiment_stats = {
            'positive': 0,
            'negative': 0,
            'neutral': 0
        }
        
        total_engagement = 0
        
        for article in recent_articles:
            # 分析情感
            sentiment_score, sentiment_label = self.analyze_sentiment(article.get('title', ''))
            sentiment_stats[sentiment_label] += 1
            
            # 计算参与度
            engagement = (article.get('reposts_count', 0) + 
                         article.get('comments_count', 0) + 
                         article.get('attitudes_count', 0))
            total_engagement += engagement
        
        stats.update({
            'sentiment_distribution': sentiment_stats,
            'average_engagement': total_engagement / len(recent_articles) if recent_articles else 0,
            'last_updated': datetime.now().isoformat()
        })
        
        return stats
    
    def get_sentiment_analysis(self) -> Dict[str, Any]:
        """获取情感分析数据"""
        articles = self.data_manager.get_recent_articles(200)
        
        sentiment_data = {
            'hourly_sentiment': defaultdict(lambda: {'positive': 0, 'negative': 0, 'neutral': 0}),
            'daily_sentiment': defaultdict(lambda: {'positive': 0, 'negative': 0, 'neutral': 0}),
            'overall_sentiment': {'positive': 0, 'negative': 0, 'neutral': 0},
            'sentiment_trend': []
        }
        
        for article in articles:
            # 分析情感
            sentiment_score, sentiment_label = self.analyze_sentiment(article.get('title', ''))
            
            # 解析时间
            created_at = article.get('created_at', '')
            if created_at:
                try:
                    dt = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
                    hour_key = dt.strftime('%Y-%m-%d %H')
                    day_key = dt.strftime('%Y-%m-%d')
                    
                    # 按小时统计
                    sentiment_data['hourly_sentiment'][hour_key][sentiment_label] += 1
                    
                    # 按天统计
                    sentiment_data['daily_sentiment'][day_key][sentiment_label] += 1
                    
                except:
                    pass
            
            # 总体统计
            sentiment_data['overall_sentiment'][sentiment_label] += 1
        
        # 转换为列表格式便于前端使用
        sentiment_data['hourly_sentiment'] = dict(sentiment_data['hourly_sentiment'])
        sentiment_data['daily_sentiment'] = dict(sentiment_data['daily_sentiment'])
        
        # 生成趋势数据（最近24小时）
        now = datetime.now()
        for i in range(24):
            hour_time = now - timedelta(hours=i)
            hour_key = hour_time.strftime('%Y-%m-%d %H')
            hour_data = sentiment_data['hourly_sentiment'].get(hour_key, {'positive': 0, 'negative': 0, 'neutral': 0})
            
            sentiment_data['sentiment_trend'].append({
                'time': hour_key,
                'positive': hour_data['positive'],
                'negative': hour_data['negative'],
                'neutral': hour_data['neutral']
            })
        
        sentiment_data['sentiment_trend'].reverse()
        
        return sentiment_data
    
    def get_top_keywords(self, limit: int = 20) -> List[Dict[str, Any]]:
        """获取热门关键词"""
        articles = self.data_manager.get_recent_articles(500)
        
        keyword_counter = Counter()
        keyword_sentiment = defaultdict(list)
        
        for article in articles:
            title = article.get('title', '')
            if title:
                # 提取关键词
                keywords = self.extract_keywords(title, 5)
                
                # 分析情感
                sentiment_score, sentiment_label = self.analyze_sentiment(title)
                
                for keyword in keywords:
                    keyword_counter[keyword] += 1
                    keyword_sentiment[keyword].append(sentiment_score)
        
        # 构建结果
        top_keywords = []
        for keyword, count in keyword_counter.most_common(limit):
            sentiment_scores = keyword_sentiment[keyword]
            avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
            
            # 确定主要情感倾向
            if avg_sentiment > 0.1:
                main_sentiment = 'positive'
            elif avg_sentiment < -0.1:
                main_sentiment = 'negative'
            else:
                main_sentiment = 'neutral'
            
            top_keywords.append({
                'keyword': keyword,
                'count': count,
                'sentiment_score': round(avg_sentiment, 3),
                'sentiment_label': main_sentiment
            })
        
        return top_keywords
    
    def get_trend_analysis(self) -> Dict[str, Any]:
        """获取趋势分析数据"""
        articles = self.data_manager.get_recent_articles(1000)
        
        # 按小时统计文章数量和参与度
        hourly_stats = defaultdict(lambda: {
            'article_count': 0,
            'total_reposts': 0,
            'total_comments': 0,
            'total_attitudes': 0,
            'avg_engagement': 0
        })
        
        # 按天统计
        daily_stats = defaultdict(lambda: {
            'article_count': 0,
            'total_reposts': 0,
            'total_comments': 0,
            'total_attitudes': 0,
            'avg_engagement': 0
        })
        
        for article in articles:
            created_at = article.get('created_at', '')
            if created_at:
                try:
                    dt = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
                    hour_key = dt.strftime('%Y-%m-%d %H')
                    day_key = dt.strftime('%Y-%m-%d')
                    
                    reposts = article.get('reposts_count', 0)
                    comments = article.get('comments_count', 0)
                    attitudes = article.get('attitudes_count', 0)
                    
                    # 小时统计
                    hourly_stats[hour_key]['article_count'] += 1
                    hourly_stats[hour_key]['total_reposts'] += reposts
                    hourly_stats[hour_key]['total_comments'] += comments
                    hourly_stats[hour_key]['total_attitudes'] += attitudes
                    
                    # 日统计
                    daily_stats[day_key]['article_count'] += 1
                    daily_stats[day_key]['total_reposts'] += reposts
                    daily_stats[day_key]['total_comments'] += comments
                    daily_stats[day_key]['total_attitudes'] += attitudes
                    
                except:
                    pass
        
        # 计算平均参与度
        for stats in hourly_stats.values():
            if stats['article_count'] > 0:
                total_engagement = stats['total_reposts'] + stats['total_comments'] + stats['total_attitudes']
                stats['avg_engagement'] = total_engagement / stats['article_count']
        
        for stats in daily_stats.values():
            if stats['article_count'] > 0:
                total_engagement = stats['total_reposts'] + stats['total_comments'] + stats['total_attitudes']
                stats['avg_engagement'] = total_engagement / stats['article_count']
        
        # 生成最近24小时的趋势数据
        hourly_trend = []
        now = datetime.now()
        for i in range(24):
            hour_time = now - timedelta(hours=i)
            hour_key = hour_time.strftime('%Y-%m-%d %H')
            hour_data = hourly_stats.get(hour_key, {
                'article_count': 0, 'total_reposts': 0, 'total_comments': 0, 
                'total_attitudes': 0, 'avg_engagement': 0
            })
            
            hourly_trend.append({
                'time': hour_key,
                'article_count': hour_data['article_count'],
                'avg_engagement': round(hour_data['avg_engagement'], 2)
            })
        
        hourly_trend.reverse()
        
        # 生成最近7天的趋势数据
        daily_trend = []
        for i in range(7):
            day_time = now - timedelta(days=i)
            day_key = day_time.strftime('%Y-%m-%d')
            day_data = daily_stats.get(day_key, {
                'article_count': 0, 'total_reposts': 0, 'total_comments': 0, 
                'total_attitudes': 0, 'avg_engagement': 0
            })
            
            daily_trend.append({
                'date': day_key,
                'article_count': day_data['article_count'],
                'avg_engagement': round(day_data['avg_engagement'], 2)
            })
        
        daily_trend.reverse()
        
        return {
            'hourly_trend': hourly_trend,
            'daily_trend': daily_trend,
            'peak_hours': self._find_peak_hours(hourly_stats),
            'growth_rate': self._calculate_growth_rate(daily_trend)
        }
    
    def _find_peak_hours(self, hourly_stats: Dict) -> List[str]:
        """找出活跃度最高的时间段"""
        if not hourly_stats:
            return []
        
        # 按参与度排序
        sorted_hours = sorted(hourly_stats.items(), 
                            key=lambda x: x[1]['avg_engagement'], 
                            reverse=True)
        
        return [hour for hour, _ in sorted_hours[:3]]
    
    def _calculate_growth_rate(self, daily_trend: List[Dict]) -> float:
        """计算增长率"""
        if len(daily_trend) < 2:
            return 0.0
        
        recent_avg = sum(day['article_count'] for day in daily_trend[-3:]) / 3
        previous_avg = sum(day['article_count'] for day in daily_trend[:3]) / 3
        
        if previous_avg == 0:
            return 0.0
        
        growth_rate = ((recent_avg - previous_avg) / previous_avg) * 100
        return round(growth_rate, 2)

    def get_regional_analysis(self) -> Dict[str, Any]:
        """获取地域分析数据"""
        articles = self.data_manager.get_all_articles()

        regional_stats = defaultdict(lambda: {
            'count': 0,
            'total_engagement': 0,
            'avg_engagement': 0,
            'sentiment_positive': 0,
            'sentiment_negative': 0,
            'sentiment_neutral': 0
        })

        for article in articles:
            region = article.get('region_name', '未知地区').strip()
            if not region or region == '发布于':
                region = '未知地区'

            # 统计数量
            regional_stats[region]['count'] += 1

            # 统计参与度
            engagement = (article.get('reposts_count', 0) +
                         article.get('comments_count', 0) +
                         article.get('attitudes_count', 0))
            regional_stats[region]['total_engagement'] += engagement

            # 情感分析
            title = article.get('title', '')
            if title:
                sentiment_score, sentiment_label = self.analyze_sentiment(title)
                regional_stats[region][f'sentiment_{sentiment_label}'] += 1

        # 计算平均参与度
        for region_data in regional_stats.values():
            if region_data['count'] > 0:
                region_data['avg_engagement'] = round(
                    region_data['total_engagement'] / region_data['count'], 2
                )

        # 转换为列表并排序
        result = []
        for region, data in regional_stats.items():
            result.append({
                'region': region,
                'count': data['count'],
                'avg_engagement': data['avg_engagement'],
                'sentiment_distribution': {
                    'positive': data['sentiment_positive'],
                    'negative': data['sentiment_negative'],
                    'neutral': data['sentiment_neutral']
                }
            })

        result.sort(key=lambda x: x['count'], reverse=True)
        return {'regional_data': result[:20]}  # 返回前20个地区

    def get_author_analysis(self) -> Dict[str, Any]:
        """获取作者分析数据"""
        articles = self.data_manager.get_all_articles()

        author_stats = defaultdict(lambda: {
            'name': '',
            'count': 0,
            'total_engagement': 0,
            'avg_engagement': 0,
            'articles': []
        })

        for article in articles:
            author_id = article.get('author_id', '')
            author_name = article.get('author_name', '未知作者')

            if not author_id:
                continue

            # 统计作者数据
            author_stats[author_id]['name'] = author_name
            author_stats[author_id]['count'] += 1

            engagement = (article.get('reposts_count', 0) +
                         article.get('comments_count', 0) +
                         article.get('attitudes_count', 0))
            author_stats[author_id]['total_engagement'] += engagement

            # 保存文章信息
            author_stats[author_id]['articles'].append({
                'title': article.get('title', ''),
                'engagement': engagement,
                'created_at': article.get('created_at', '')
            })

        # 计算平均参与度并筛选活跃作者
        active_authors = []
        for author_id, data in author_stats.items():
            if data['count'] >= 2:  # 至少发布2篇文章
                data['avg_engagement'] = round(
                    data['total_engagement'] / data['count'], 2
                )
                active_authors.append({
                    'author_id': author_id,
                    'name': data['name'],
                    'article_count': data['count'],
                    'avg_engagement': data['avg_engagement'],
                    'total_engagement': data['total_engagement']
                })

        active_authors.sort(key=lambda x: x['avg_engagement'], reverse=True)
        return {'top_authors': active_authors[:20]}

    def get_time_analysis(self) -> Dict[str, Any]:
        """获取时间分析数据"""
        articles = self.data_manager.get_all_articles()

        # 按小时统计
        hourly_stats = defaultdict(lambda: {'count': 0, 'engagement': 0})
        # 按星期统计
        weekly_stats = defaultdict(lambda: {'count': 0, 'engagement': 0})

        for article in articles:
            created_at = article.get('created_at', '')
            if created_at:
                try:
                    dt = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
                    hour = dt.hour
                    weekday = dt.weekday()  # 0=Monday, 6=Sunday

                    engagement = (article.get('reposts_count', 0) +
                                 article.get('comments_count', 0) +
                                 article.get('attitudes_count', 0))

                    # 小时统计
                    hourly_stats[hour]['count'] += 1
                    hourly_stats[hour]['engagement'] += engagement

                    # 星期统计
                    weekly_stats[weekday]['count'] += 1
                    weekly_stats[weekday]['engagement'] += engagement

                except:
                    pass

        # 格式化结果
        hourly_data = []
        for hour in range(24):
            data = hourly_stats[hour]
            avg_engagement = data['engagement'] / data['count'] if data['count'] > 0 else 0
            hourly_data.append({
                'hour': hour,
                'count': data['count'],
                'avg_engagement': round(avg_engagement, 2)
            })

        weekday_names = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        weekly_data = []
        for weekday in range(7):
            data = weekly_stats[weekday]
            avg_engagement = data['engagement'] / data['count'] if data['count'] > 0 else 0
            weekly_data.append({
                'weekday': weekday,
                'weekday_name': weekday_names[weekday],
                'count': data['count'],
                'avg_engagement': round(avg_engagement, 2)
            })

        return {
            'hourly_analysis': hourly_data,
            'weekly_analysis': weekly_data
        }
