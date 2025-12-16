"""
爬虫配置文件
"""

# 请求配置
REQUEST_CONFIG = {
    # 每小时最大请求数
    'max_requests_per_hour': 60,
    
    # 请求间隔（秒）
    'min_request_interval': 60,
    'max_request_interval': 180,
    
    # 重试配置
    'max_retries': 3,
    'retry_delay': 30,
    
    # 超时配置
    'request_timeout': 30,
    
    # 错误处理
    'max_consecutive_errors': 5,
    'error_cooldown_time': 1800,  # 30分钟
    
    # 重复内容处理
    'duplicate_cooldown_time': 300,  # 5分钟
}

# User-Agent池
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0 Safari/537.36"
]

# 代理配置（如果需要）
PROXY_CONFIG = {
    'enabled': False,
    'proxies': [
        # 格式: {'http': 'http://proxy:port', 'https': 'https://proxy:port'}
    ],
    'rotation_enabled': True
}

# 数据保存配置
DATA_CONFIG = {
    'csv_encoding': 'utf-8',
    'backup_enabled': True,
    'backup_interval_hours': 24,
    'max_backup_files': 7
}

# 监控配置
MONITORING_CONFIG = {
    'log_level': 'INFO',
    'log_file': 'logs/spider.log',
    'status_report_interval': 300,  # 5分钟
    'health_check_enabled': True
}

# 智能调节配置
ADAPTIVE_CONFIG = {
    'enabled': True,
    'success_rate_threshold': 0.8,  # 成功率阈值
    'slow_down_factor': 1.5,  # 减速因子
    'speed_up_factor': 0.8,   # 加速因子
    'min_interval': 30,       # 最小间隔
    'max_interval': 600       # 最大间隔
}
