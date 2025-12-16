// 全局变量
let socket;
let charts = {};

// 初始化函数
document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
    initializeWebSocket();
    loadInitialData();
    
    // 定期刷新数据（如果WebSocket连接失败）
    setInterval(loadInitialData, 30000);
});

// 初始化仪表板
function initializeDashboard() {
    console.log('初始化仪表板...');
    
    // 初始化图表
    initializeCharts();
    
    // 绑定事件
    bindEvents();
}

// 初始化WebSocket连接
function initializeWebSocket() {
    try {
        socket = io();
        
        socket.on('connect', function() {
            console.log('WebSocket连接成功');
            showConnectionStatus(true);
        });
        
        socket.on('disconnect', function() {
            console.log('WebSocket连接断开');
            showConnectionStatus(false);
        });
        
        socket.on('stats_update', function(data) {
            updateStatsCards(data);
        });
        
        socket.on('sentiment_update', function(data) {
            updateSentimentCharts(data);
        });
        
        socket.on('keywords_update', function(data) {
            updateKeywords(data);
        });
        
        socket.on('articles_update', function(data) {
            updateRecentArticles(data);
        });
        
    } catch (error) {
        console.error('WebSocket初始化失败:', error);
        showConnectionStatus(false);
    }
}

// 加载初始数据
async function loadInitialData() {
    try {
        // 并行加载所有数据
        const [stats, sentiment, keywords, trends, articles] = await Promise.all([
            fetch('/api/stats').then(r => r.json()),
            fetch('/api/sentiment').then(r => r.json()),
            fetch('/api/keywords').then(r => r.json()),
            fetch('/api/trends').then(r => r.json()),
            fetch('/api/recent_articles').then(r => r.json())
        ]);
        
        updateStatsCards(stats);
        updateSentimentCharts(sentiment);
        updateKeywords(keywords);
        updateRecentArticles(articles);
        updateTrendChart(trends);
        
        updateLastUpdateTime();
        
    } catch (error) {
        console.error('加载初始数据失败:', error);
        showError('加载数据失败，请检查网络连接');
    }
}

// 初始化图表
function initializeCharts() {
    // 情感趋势图
    const sentimentCtx = document.getElementById('sentimentChart').getContext('2d');
    charts.sentimentChart = new Chart(sentimentCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: '正面',
                data: [],
                borderColor: '#28a745',
                backgroundColor: 'rgba(40, 167, 69, 0.1)',
                tension: 0.4
            }, {
                label: '负面',
                data: [],
                borderColor: '#dc3545',
                backgroundColor: 'rgba(220, 53, 69, 0.1)',
                tension: 0.4
            }, {
                label: '中性',
                data: [],
                borderColor: '#6c757d',
                backgroundColor: 'rgba(108, 117, 125, 0.1)',
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top'
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
    
    // 情感分布饼图
    const sentimentPieCtx = document.getElementById('sentimentPieChart').getContext('2d');
    charts.sentimentPieChart = new Chart(sentimentPieCtx, {
        type: 'doughnut',
        data: {
            labels: ['正面', '负面', '中性'],
            datasets: [{
                data: [0, 0, 0],
                backgroundColor: ['#28a745', '#dc3545', '#6c757d']
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
    
    // 趋势图
    const trendCtx = document.getElementById('trendChart').getContext('2d');
    charts.trendChart = new Chart(trendCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: '文章数量',
                data: [],
                borderColor: '#007bff',
                backgroundColor: 'rgba(0, 123, 255, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// 更新统计卡片
function updateStatsCards(data) {
    const cards = {
        'total-articles': data.total_articles || 0,
        'total-comments': data.total_comments || 0,
        'today-articles': data.today_articles || 0,
        'avg-engagement': (data.average_engagement || 0).toFixed(1)
    };
    
    Object.keys(cards).forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            const oldValue = element.textContent;
            const newValue = String(cards[id]);
            
            if (oldValue !== newValue) {
                element.textContent = newValue;
                element.classList.add('pulse');
                setTimeout(() => element.classList.remove('pulse'), 300);
            }
        }
    });
}

// 更新情感图表
function updateSentimentCharts(data) {
    if (data.sentiment_trend && charts.sentimentChart) {
        const labels = data.sentiment_trend.map(item => 
            new Date(item.time).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
        );
        const positiveData = data.sentiment_trend.map(item => item.positive);
        const negativeData = data.sentiment_trend.map(item => item.negative);
        const neutralData = data.sentiment_trend.map(item => item.neutral);
        
        charts.sentimentChart.data.labels = labels;
        charts.sentimentChart.data.datasets[0].data = positiveData;
        charts.sentimentChart.data.datasets[1].data = negativeData;
        charts.sentimentChart.data.datasets[2].data = neutralData;
        charts.sentimentChart.update();
    }
    
    if (data.overall_sentiment && charts.sentimentPieChart) {
        charts.sentimentPieChart.data.datasets[0].data = [
            data.overall_sentiment.positive || 0,
            data.overall_sentiment.negative || 0,
            data.overall_sentiment.neutral || 0
        ];
        charts.sentimentPieChart.update();
    }
}

// 更新关键词
function updateKeywords(keywords) {
    const container = document.getElementById('keywords-container');
    if (!container) return;
    
    container.innerHTML = '';
    
    if (!Array.isArray(keywords) || keywords.length === 0) {
        container.innerHTML = '<p class="text-muted">暂无关键词数据</p>';
        return;
    }
    
    keywords.forEach((keyword, index) => {
        const tag = document.createElement('span');
        tag.className = `keyword-tag ${keyword.sentiment_label || 'neutral'}`;
        tag.textContent = `${keyword.keyword} (${keyword.count})`;
        tag.title = `情感分数: ${keyword.sentiment_score}`;
        
        // 添加淡入动画
        tag.style.opacity = '0';
        tag.style.animation = `fadeIn 0.3s ease-out ${index * 0.05}s forwards`;
        
        container.appendChild(tag);
    });
}

// 更新最新文章
function updateRecentArticles(articles) {
    const container = document.getElementById('recent-articles');
    if (!container) return;
    
    container.innerHTML = '';
    
    if (!Array.isArray(articles) || articles.length === 0) {
        container.innerHTML = '<p class="text-muted">暂无文章数据</p>';
        return;
    }
    
    articles.forEach((article, index) => {
        const articleDiv = document.createElement('div');
        articleDiv.className = 'article-item';
        
        const title = article.title || '无标题';
        const truncatedTitle = title.length > 50 ? title.substring(0, 50) + '...' : title;
        
        articleDiv.innerHTML = `
            <div class="article-title">${truncatedTitle}</div>
            <div class="article-meta">
                <span><i class="fas fa-user"></i> ${article.author_name || '未知'}</span>
                <span><i class="fas fa-clock"></i> ${formatDateTime(article.created_at)}</span>
            </div>
            <div class="article-stats">
                <span><i class="fas fa-retweet"></i> ${article.reposts_count || 0}</span>
                <span><i class="fas fa-comment"></i> ${article.comments_count || 0}</span>
                <span><i class="fas fa-heart"></i> ${article.attitudes_count || 0}</span>
            </div>
        `;
        
        // 添加淡入动画
        articleDiv.style.opacity = '0';
        articleDiv.style.animation = `fadeIn 0.3s ease-out ${index * 0.05}s forwards`;
        
        container.appendChild(articleDiv);
    });
}

// 更新趋势图
function updateTrendChart(data) {
    if (data.hourly_trend && charts.trendChart) {
        const labels = data.hourly_trend.map(item => 
            new Date(item.time).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
        );
        const articleCount = data.hourly_trend.map(item => item.article_count);
        
        charts.trendChart.data.labels = labels;
        charts.trendChart.data.datasets[0].data = articleCount;
        charts.trendChart.update();
    }
}

// 更新最后更新时间
function updateLastUpdateTime() {
    const element = document.getElementById('update-time');
    if (element) {
        element.textContent = new Date().toLocaleString('zh-CN');
    }
}

// 显示连接状态
function showConnectionStatus(connected) {
    const statusElement = document.getElementById('connection-status');
    if (statusElement) {
        if (connected) {
            statusElement.className = 'alert alert-success';
            statusElement.innerHTML = '<i class="fas fa-wifi me-2"></i>实时连接已建立';
            statusElement.style.display = 'block';
        } else {
            statusElement.className = 'alert alert-warning';
            statusElement.innerHTML = '<i class="fas fa-wifi-slash me-2"></i>实时连接断开，使用定期更新';
            statusElement.style.display = 'block';
        }
        
        // 3秒后自动隐藏
        setTimeout(() => {
            statusElement.style.display = 'none';
        }, 3000);
    }
}

// 绑定事件
function bindEvents() {
    // 可以在这里添加更多的事件绑定
}

// 格式化日期时间
function formatDateTime(dateString) {
    if (!dateString) return '--';
    
    try {
        const date = new Date(dateString);
        return date.toLocaleString('zh-CN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });
    } catch (error) {
        return '--';
    }
}

// 显示错误信息
function showError(message) {
    console.error(message);
    // 可以在这里添加用户友好的错误提示
}

// 工具函数
const utils = {
    // 数字格式化
    formatNumber: function(num) {
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        } else if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        return num.toString();
    },
    
    // 防抖函数
    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
};