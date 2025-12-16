// 全局变量
let socket;
let sentimentChart, sentimentPieChart, categoryChart, regionalChart, authorChart, hourlyChart, weeklyChart;
let currentCategory = '';

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeSocket();
    initializeCharts();
    loadInitialData();
    setupEventListeners();
    
    // 设置定时刷新
    setInterval(loadInitialData, 30000);
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

// 设置事件监听器
function setupEventListeners() {
    // 分类选择器
    document.getElementById('categorySelect').addEventListener('change', function() {
        currentCategory = this.value;
        loadCategoryData();
    });
    
    // 标签切换事件
    document.querySelectorAll('[data-bs-toggle="tab"]').forEach(tab => {
        tab.addEventListener('shown.bs.tab', function(event) {
            const targetId = event.target.getAttribute('data-bs-target');
            switch(targetId) {
                case '#category':
                    loadCategoryData();
                    break;
                case '#regional':
                    loadRegionalData();
                    break;
                case '#author':
                    loadAuthorData();
                    break;
                case '#time':
                    loadTimeData();
                    break;
            }
        });
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
    
    // 分类图表
    const categoryCtx = document.getElementById('categoryChart').getContext('2d');
    categoryChart = new Chart(categoryCtx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: '文章数量',
                data: [],
                backgroundColor: 'rgba(54, 162, 235, 0.6)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
    
    // 地域图表
    const regionalCtx = document.getElementById('regionalChart').getContext('2d');
    regionalChart = new Chart(regionalCtx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: '文章数量',
                data: [],
                backgroundColor: 'rgba(255, 99, 132, 0.6)',
                borderColor: 'rgba(255, 99, 132, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
    
    // 作者图表
    const authorCtx = document.getElementById('authorChart').getContext('2d');
    authorChart = new Chart(authorCtx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: '平均参与度',
                data: [],
                backgroundColor: 'rgba(75, 192, 192, 0.6)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
    
    // 小时分布图表
    const hourlyCtx = document.getElementById('hourlyChart').getContext('2d');
    hourlyChart = new Chart(hourlyCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: '文章数量',
                data: [],
                borderColor: '#007bff',
                backgroundColor: 'rgba(0, 123, 255, 0.1)',
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
    
    // 星期分布图表
    const weeklyCtx = document.getElementById('weeklyChart').getContext('2d');
    weeklyChart = new Chart(weeklyCtx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: '文章数量',
                data: [],
                backgroundColor: 'rgba(153, 102, 255, 0.6)',
                borderColor: 'rgba(153, 102, 255, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                y: {
                    beginAtZero: true
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
        fetch('/api/recent_articles?limit=10').then(r => r.json()),
        fetch('/api/categories').then(r => r.json())
    ]).then(([stats, sentiment, keywords, articles, categories]) => {
        updateStats(stats);
        updateSentimentChart(sentiment);
        updateKeywords(keywords);
        updateRecentArticles(articles);
        updateCategorySelect(categories);
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
                <a href="#" class="article-title" onclick="showArticleDetail('${article.id}')">
                    ${title}
                </a>
                <div class="article-meta">
                    <small>
                        <i class="fas fa-user"></i> ${article.author_name} | 
                        <i class="fas fa-clock"></i> ${formatTime(article.created_at)} |
                        <i class="fas fa-map-marker-alt"></i> ${article.region_name || '未知'} |
                        <i class="fas fa-tag"></i> ${article.article_type || '未分类'}
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

// 更新分类选择器
function updateCategorySelect(categories) {
    const select = document.getElementById('categorySelect');
    
    // 清除现有选项（保留"全部分类"）
    while (select.children.length > 1) {
        select.removeChild(select.lastChild);
    }
    
    // 添加新选项
    categories.forEach(category => {
        const option = document.createElement('option');
        option.value = category.name;
        option.textContent = `${category.name} (${category.count})`;
        select.appendChild(option);
    });
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
    
    if (diff < 60000) {
        return '刚刚';
    } else if (diff < 3600000) {
        return Math.floor(diff / 60000) + '分钟前';
    } else if (diff < 86400000) {
        return Math.floor(diff / 3600000) + '小时前';
    } else {
        return date.toLocaleDateString('zh-CN');
    }
}

// 显示文章详情
function showArticleDetail(articleId) {
    fetch(`/api/article_detail/${articleId}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert('获取文章详情失败: ' + data.error);
                return;
            }
            
            const content = document.getElementById('articleDetailContent');
            content.innerHTML = `
                <div class="mb-3">
                    <h6>标题:</h6>
                    <p>${data.title}</p>
                </div>
                <div class="row mb-3">
                    <div class="col-md-6">
                        <h6>作者:</h6>
                        <p><a href="${data.author_home_url}" target="_blank">${data.author_name}</a></p>
                    </div>
                    <div class="col-md-6">
                        <h6>发布时间:</h6>
                        <p>${data.created_at}</p>
                    </div>
                </div>
                <div class="row mb-3">
                    <div class="col-md-4">
                        <h6>转发数:</h6>
                        <p>${data.reposts_count}</p>
                    </div>
                    <div class="col-md-4">
                        <h6>评论数:</h6>
                        <p>${data.comments_count}</p>
                    </div>
                    <div class="col-md-4">
                        <h6>点赞数:</h6>
                        <p>${data.attitudes_count}</p>
                    </div>
                </div>
                <div class="row mb-3">
                    <div class="col-md-6">
                        <h6>地区:</h6>
                        <p>${data.region_name || '未知'}</p>
                    </div>
                    <div class="col-md-6">
                        <h6>分类:</h6>
                        <p>${data.article_type || '未分类'}</p>
                    </div>
                </div>
                <div class="mb-3">
                    <h6>原文链接:</h6>
                    <p><a href="${data.article_url}" target="_blank">查看原文</a></p>
                </div>
                <div class="mb-3">
                    <h6>评论 (${data.comment_count}):</h6>
                    <div style="max-height: 200px; overflow-y: auto;">
                        ${data.comments && data.comments.length > 0 ? 
                            data.comments.slice(0, 10).map(comment => `
                                <div class="border-bottom pb-2 mb-2">
                                    <small><strong>${comment.user_name}</strong> - ${comment.created_at}</small>
                                    <p class="mb-1">${comment.text}</p>
                                    <small class="text-muted">👍 ${comment.like_counts}</small>
                                </div>
                            `).join('') : 
                            '<p class="text-muted">暂无评论</p>'
                        }
                    </div>
                </div>
            `;
            
            const modal = new bootstrap.Modal(document.getElementById('articleDetailModal'));
            modal.show();
        })
        .catch(error => {
            console.error('Error fetching article detail:', error);
            alert('获取文章详情失败');
        });
}

// 加载分类数据
function loadCategoryData() {
    fetch('/api/categories')
        .then(response => response.json())
        .then(data => {
            updateCategoryChart(data);
        })
        .catch(error => {
            console.error('Error loading category data:', error);
        });

    // 加载分类文章
    const category = currentCategory || '';
    fetch(`/api/recent_articles?limit=20&category=${category}`)
        .then(response => response.json())
        .then(data => {
            updateCategoryArticles(data);
        })
        .catch(error => {
            console.error('Error loading category articles:', error);
        });
}

// 更新分类图表
function updateCategoryChart(data) {
    if (data && data.length > 0) {
        const labels = data.slice(0, 10).map(item => item.name);
        const counts = data.slice(0, 10).map(item => item.count);

        categoryChart.data.labels = labels;
        categoryChart.data.datasets[0].data = counts;
        categoryChart.update();
    }
}

// 更新分类文章列表
function updateCategoryArticles(data) {
    const container = document.getElementById('category-articles');
    container.innerHTML = '';

    if (data && data.length > 0) {
        data.forEach(article => {
            const articleDiv = document.createElement('div');
            articleDiv.className = 'article-item';

            const title = article.title.length > 40 ?
                article.title.substring(0, 40) + '...' : article.title;

            articleDiv.innerHTML = `
                <a href="#" class="article-title" onclick="showArticleDetail('${article.id}')">
                    ${title}
                </a>
                <div class="article-meta">
                    <small>
                        <i class="fas fa-user"></i> ${article.author_name} |
                        <i class="fas fa-clock"></i> ${formatTime(article.created_at)}
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
        container.innerHTML = '<p class="text-muted">该分类暂无文章数据</p>';
    }
}

// 加载地域数据
function loadRegionalData() {
    fetch('/api/regional_analysis')
        .then(response => response.json())
        .then(data => {
            updateRegionalChart(data);
        })
        .catch(error => {
            console.error('Error loading regional data:', error);
        });
}

// 更新地域图表
function updateRegionalChart(data) {
    if (data.regional_data && data.regional_data.length > 0) {
        const labels = data.regional_data.slice(0, 15).map(item => item.region);
        const counts = data.regional_data.slice(0, 15).map(item => item.count);

        regionalChart.data.labels = labels;
        regionalChart.data.datasets[0].data = counts;
        regionalChart.update();
    }
}

// 加载作者数据
function loadAuthorData() {
    fetch('/api/author_analysis')
        .then(response => response.json())
        .then(data => {
            updateAuthorChart(data);
        })
        .catch(error => {
            console.error('Error loading author data:', error);
        });
}

// 更新作者图表
function updateAuthorChart(data) {
    if (data.top_authors && data.top_authors.length > 0) {
        const labels = data.top_authors.slice(0, 10).map(item => item.name);
        const engagements = data.top_authors.slice(0, 10).map(item => item.avg_engagement);

        authorChart.data.labels = labels;
        authorChart.data.datasets[0].data = engagements;
        authorChart.update();
    }
}

// 加载时间数据
function loadTimeData() {
    fetch('/api/time_analysis')
        .then(response => response.json())
        .then(data => {
            updateTimeCharts(data);
        })
        .catch(error => {
            console.error('Error loading time data:', error);
        });
}

// 更新时间图表
function updateTimeCharts(data) {
    // 更新小时分布图表
    if (data.hourly_analysis && data.hourly_analysis.length > 0) {
        const hourLabels = data.hourly_analysis.map(item => item.hour + ':00');
        const hourCounts = data.hourly_analysis.map(item => item.count);

        hourlyChart.data.labels = hourLabels;
        hourlyChart.data.datasets[0].data = hourCounts;
        hourlyChart.update();
    }

    // 更新星期分布图表
    if (data.weekly_analysis && data.weekly_analysis.length > 0) {
        const weekLabels = data.weekly_analysis.map(item => item.weekday_name);
        const weekCounts = data.weekly_analysis.map(item => item.count);

        weeklyChart.data.labels = weekLabels;
        weeklyChart.data.datasets[0].data = weekCounts;
        weeklyChart.update();
    }
}
