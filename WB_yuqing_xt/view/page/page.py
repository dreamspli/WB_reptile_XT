from flask import Blueprint, render_template, request, jsonify
from analysis.data_manager import DataManager
from analysis.data_analyzer import DataAnalyzer

# 创建页面蓝图
pb = Blueprint('page', __name__)

# 初始化数据管理器
data_manager = DataManager()
data_analyzer = DataAnalyzer()

@pb.route('/dashboard')
def dashboard():
    """仪表板页面"""
    return render_template('dashboard.html')

@pb.route('/analytics')
def analytics():
    """分析页面"""
    return render_template('analytics.html')

@pb.route('/articles')
def articles():
    """文章列表页面"""
    return render_template('articles.html')

@pb.route('/article/<article_id>')
def article_detail(article_id):
    """文章详情页面"""
    return render_template('article_detail.html', article_id=article_id)

@pb.route('/reports')
def reports():
    """报告页面"""
    return render_template('reports.html')

@pb.route('/settings')
def settings():
    """设置页面"""
    return render_template('settings.html')