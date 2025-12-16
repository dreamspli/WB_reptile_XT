// 全局变量
let socket;
let sentimentChart;
let sentimentPieChart;
let trendChart;

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeSocket();
    initializeCharts();
    loadInitialData();
    
    // 设置定时刷新（更频繁）
    setInterval(loadInitialData, 30000); // 每30秒刷新一次
});

// 初始化Socket连接
function initializeSocket() {
    socket = io();
    
    socket.on('connect', function() {
        console.log('Connected to server');
        showConnectionStatus('已连接到实时数据流', 'success');
    });
    
    socket.on('disconnect', function() {
        console.log('Disconnected from server');
        showConnectionStatus('连接已断开', 'danger');
    });
    
    socket.on('stats_update', function(data) {
        updateStats(data);
    });
    
    socket.on('sentiment_update', function(data) {
        updateSentimentChart(data);
    });
    
    socket.on('keywords_update', function(data) {
        updateKeywords(data);
    });

    socket.on('articles_update', function(data) {
        updateRecentArticles(data);
    });
}

// 显示连接状态
function showConnectionStatus(message, type) {
    const statusDiv = document.getElementById('connection-status');
    statusDiv.className = `alert alert-${type}`;
    statusDiv.innerHTML = `<i class="fas fa-wifi me-2"></i>${message}`;
    statusDiv.style.display = 'block';
    
    setTimeout(() => {
        statusDiv.style.display = 'none';
    }, 3000);
}

// 初始化图表
function initializeCharts() {
    // 情感趋势图
    const sentimentCtx = document.getElementById('sentimentChart').getContext('2d');
    sentimentChart = new Chart(sentimentCtx, {
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
            scales: {
                y: {
                    beginAtZero: true
                }
            },
            plugins: {
                legend: {
                    position: 'top'
                }
            }
        }
    });
    
    // 情感分布饼图
    const pieCtx = document.getElementById('sentimentPieChart').getContext('2d');
    sentimentPieChart = new Chart(pieCtx, {
        type: 'doughnut',
        data: {
            labels: ['正面', '负面', '中性'],
            datasets: [{
                data: [0, 0, 0],
                backgroundColor: ['#28a745', '#dc3545', '#6c757d'],
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
    
    // 趋势分析图
    const trendCtx = document.getElementById('trendChart').getContext('2d');
    trendChart = new Chart(trendCtx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: '文章数量',
                data: [],
                backgroundColor: 'rgba(54, 162, 235, 0.6)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1,
                yAxisID: 'y'
            }, {
                label: '平均参与度',
                data: [],
                type: 'line',
                backgroundColor: 'rgba(255, 99, 132, 0.2)',
                borderColor: 'rgba(255, 99, 132, 1)',
                borderWidth: 2,
                tension: 0.4,
                yAxisID: 'y1'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: '文章数量'
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: '平均参与度'
                    },
                    grid: {
                        drawOnChartArea: false,
                    },
                }
            },
            plugins: {
                legend: {
                    position: 'top'
                }
            }
        }
    });
}

// 加载初始数据
function loadInitialData() {
    Promise.all([
        fetch('/api/stats').then(r => r.json()),
        fetch('/api/sentiment').then(r => r.json()),
        fetch('/api/keywords').then(r => r.json()),
        fetch('/api/trends').then(r => r.json()),
        fetch('/api/recent_articles?limit=10').then(r => r.json())
    ]).then(([stats, sentiment, keywords, trends, articles]) => {
        updateStats(stats);
        updateSentimentChart(sentiment);
        updateKeywords(keywords);
        updateTrendChart(trends);
        updateRecentArticles(articles);
        updateLastUpdateTime();
    }).catch(error => {
        console.error('Error loading data:', error);
    });
}

// 更新统计数据
function updateStats(data) {
    document.getElementById('total-articles').textContent = data.total_articles || 0;
    document.getElementById('total-comments').textContent = data.total_comments || 0;
    document.getElementById('today-articles').textContent = data.today_articles || 0;
    document.getElementById('avg-engagement').textContent = Math.round(data.average_engagement || 0);
    
    // 添加更新动画
    ['total-articles', 'total-comments', 'today-articles', 'avg-engagement'].forEach(id => {
        document.getElementById(id).parentElement.parentElement.classList.add('data-updated');
        setTimeout(() => {
            document.getElementById(id).parentElement.parentElement.classList.remove('data-updated');
        }, 500);
    });
}

// 更新情感图表
function updateSentimentChart(data) {
    if (data.sentiment_trend && data.sentiment_trend.length > 0) {
        const labels = data.sentiment_trend.map(item => {
            const date = new Date(item.time + ':00');
            return date.getHours() + ':00';
        });
        
        sentimentChart.data.labels = labels;
        sentimentChart.data.datasets[0].data = data.sentiment_trend.map(item => item.positive);
        sentimentChart.data.datasets[1].data = data.sentiment_trend.map(item => item.negative);
        sentimentChart.data.datasets[2].data = data.sentiment_trend.map(item => item.neutral);
        sentimentChart.update();
    }
    
    // 更新饼图
    if (data.overall_sentiment) {
        const total = data.overall_sentiment.positive + data.overall_sentiment.negative + data.overall_sentiment.neutral;
        if (total > 0) {
            sentimentPieChart.data.datasets[0].data = [
                data.overall_sentiment.positive,
                data.overall_sentiment.negative,
                data.overall_sentiment.neutral
            ];
            sentimentPieChart.update();
        }
    }
}

// 更新关键词
function updateKeywords(data) {
    const container = document.getElementById('keywords-container');
    container.innerHTML = '';
    
    if (data && data.length > 0) {
        data.forEach(keyword => {
            const tag = document.createElement('span');
            tag.className = `keyword-tag keyword-${keyword.sentiment_label}`;
            tag.textContent = `${keyword.keyword} (${keyword.count})`;
            tag.title = `情感分数: ${keyword.sentiment_score}`;
            container.appendChild(tag);
        });
    } else {
        container.innerHTML = '<p class="text-muted">暂无关键词数据</p>';
    }
}

// 更新趋势图表
function updateTrendChart(data) {
    if (data.hourly_trend && data.hourly_trend.length > 0) {
        const labels = data.hourly_trend.map(item => {
            const date = new Date(item.time + ':00');
            return date.getHours() + ':00';
        });
        
        trendChart.data.labels = labels;
        trendChart.data.datasets[0].data = data.hourly_trend.map(item => item.article_count);
        trendChart.data.datasets[1].data = data.hourly_trend.map(item => item.avg_engagement);
        trendChart.update();
    }
}

// 更新最新文章
function updateRecentArticles(data) {
    const container = document.getElementById('recent-articles');
    container.innerHTML = '';
    
    if (data && data.length > 0) {
        data.forEach(article => {
            const articleDiv = document.createElement('div');
            articleDiv.className = 'article-item';
            
            const title = article.title.length > 50 ? 
                article.title.substring(0, 50) + '...' : article.title;
            
            articleDiv.innerHTML = `
                <a href="${article.article_url}" target="_blank" class="article-title">
                    ${title}
                </a>
                <div class="article-meta">
                    <small>
                        <i class="fas fa-user"></i> ${article.author_name} | 
                        <i class="fas fa-clock"></i> ${formatTime(article.created_at)} |
                        <i class="fas fa-map-marker-alt"></i> ${article.region_name || '未知'}
                    </small>
                </div>
                <div class="article-stats mt-1">
                    <span><i class="fas fa-retweet"></i> ${article.reposts_count}</span>
                    <span><i class="fas fa-comment"></i> ${article.comments_count}</span>
                    <span><i class="fas fa-heart"></i> ${article.attitudes_count}</span>
                </div>
            `;
            
            container.appendChild(articleDiv);
        });
    } else {
        container.innerHTML = '<p class="text-muted">暂无文章数据</p>';
    }
}

// 更新最后更新时间
function updateLastUpdateTime() {
    const now = new Date();
    const timeString = now.toLocaleString('zh-CN');
    document.getElementById('update-time').textContent = timeString;
}

// 格式化时间
function formatTime(timeString) {
    if (!timeString) return '未知';
    
    const date = new Date(timeString);
    const now = new Date();
    const diff = now - date;
    
    if (diff < 60000) { // 1分钟内
        return '刚刚';
    } else if (diff < 3600000) { // 1小时内
        return Math.floor(diff / 60000) + '分钟前';
    } else if (diff < 86400000) { // 24小时内
        return Math.floor(diff / 3600000) + '小时前';
    } else {
        return date.toLocaleDateString('zh-CN');
    }
}
