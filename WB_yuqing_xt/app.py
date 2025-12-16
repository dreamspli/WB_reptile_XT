from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
from analysis.data_analyzer import DataAnalyzer
from analysis.data_manager import DataManager
import threading
import time
from view.user import user
from view.page import page

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
socketio = SocketIO(app, cors_allowed_origins="*")

# 初始化数据管理器和分析器
data_manager = DataManager()
data_analyzer = DataAnalyzer()

app.register_blueprint(user.ub)
app.register_blueprint(page.pb)


# 主页路由
@app.route('/')
def index():
    return render_template('dashboard.html')


# 增强版仪表板
@app.route('/enhanced')
def enhanced_dashboard():
    return render_template('enhanced_dashboard.html')


# 系统状态页面
@app.route('/status')
def system_status():
    return render_template('system_status.html')


# API路由
@app.route('/api/stats')
def get_stats():
    """获取统计数据"""
    stats = data_analyzer.get_real_time_stats()
    return jsonify(stats)


@app.route('/api/sentiment')
def get_sentiment():
    """获取情感分析数据"""
    sentiment_data = data_analyzer.get_sentiment_analysis()
    return jsonify(sentiment_data)


@app.route('/api/keywords')
def get_keywords():
    """获取关键词数据"""
    keywords = data_analyzer.get_top_keywords()
    return jsonify(keywords)


@app.route('/api/trends')
def get_trends():
    """获取趋势数据"""
    trends = data_analyzer.get_trend_analysis()
    return jsonify(trends)


@app.route('/api/recent_articles')
def get_recent_articles():
    """获取最新文章"""
    limit = request.args.get('limit', 10, type=int)
    category = request.args.get('category', None)
    articles = data_manager.get_recent_articles(limit, category)
    return jsonify(articles)


@app.route('/api/categories')
def get_categories():
    """获取文章类别"""
    categories = data_manager.get_article_categories()
    return jsonify(categories)


@app.route('/api/regional_analysis')
def get_regional_analysis():
    """获取地域分析数据"""
    regional_data = data_analyzer.get_regional_analysis()
    return jsonify(regional_data)


@app.route('/api/author_analysis')
def get_author_analysis():
    """获取作者分析数据"""
    author_data = data_analyzer.get_author_analysis()
    return jsonify(author_data)


@app.route('/api/time_analysis')
def get_time_analysis():
    """获取时间分析数据"""
    time_data = data_analyzer.get_time_analysis()
    return jsonify(time_data)


@app.route('/api/article_detail/<article_id>')
def get_article_detail(article_id):
    """获取文章详情"""
    article_detail = data_manager.get_article_detail(article_id)
    return jsonify(article_detail)


@app.route('/api/system_status')
def get_system_status():
    """获取系统状态"""
    import psutil
    import os
    from datetime import datetime

    # 获取系统信息
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')

    # 获取进程信息
    current_process = psutil.Process(os.getpid())

    status = {
        'system': {
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'memory_used_gb': round(memory.used / (1024 ** 3), 2),
            'memory_total_gb': round(memory.total / (1024 ** 3), 2),
            'disk_percent': disk.percent,
            'disk_used_gb': round(disk.used / (1024 ** 3), 2),
            'disk_total_gb': round(disk.total / (1024 ** 3), 2)
        },
        'application': {
            'uptime': str(datetime.now() - datetime.fromtimestamp(current_process.create_time())),
            'memory_mb': round(current_process.memory_info().rss / (1024 ** 2), 2),
            'cpu_percent': current_process.cpu_percent(),
            'threads': current_process.num_threads()
        },
        'data': {
            'total_articles': data_manager.get_statistics()['total_articles'],
            'total_comments': data_manager.get_statistics()['total_comments'],
            'cache_status': 'Redis' if data_manager.use_redis else 'Memory'
        },
        'timestamp': datetime.now().isoformat()
    }

    return jsonify(status)


# WebSocket事件处理
@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('status', {'msg': 'Connected to real-time data stream'})


@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')


def background_data_update():
    """后台数据更新任务"""
    while True:
        try:
            # 获取最新统计数据
            stats = data_analyzer.get_real_time_stats()
            socketio.emit('stats_update', stats)

            # 获取最新情感分析
            sentiment = data_analyzer.get_sentiment_analysis()
            socketio.emit('sentiment_update', sentiment)

            # 获取最新关键词
            keywords = data_analyzer.get_top_keywords()
            socketio.emit('keywords_update', keywords)

            # 获取最新文章
            recent_articles = data_manager.get_recent_articles(10)
            socketio.emit('articles_update', recent_articles)

            print(f"数据更新推送完成: {time.strftime('%H:%M:%S')}")
            time.sleep(15)  # 每15秒更新一次（更频繁）
        except Exception as e:
            print(f"Background update error: {e}")
            time.sleep(30)


if __name__ == '__main__':
    # 启动后台数据更新线程
    update_thread = threading.Thread(target=background_data_update)
    update_thread.daemon = True
    update_thread.start()

    socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
