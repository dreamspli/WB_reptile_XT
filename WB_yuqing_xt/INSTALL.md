# 微博舆情监测系统 - 安装指南

## 系统要求

- Python 3.7+
- Windows/Linux/macOS
- 至少 2GB 可用内存
- 5GB 可用磁盘空间

## 快速安装

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

如果安装失败，可以分别安装：

```bash
# Web框架
pip install Flask Flask-SocketIO

# 数据处理
pip install pandas numpy jieba

# 系统监控
pip install psutil

# HTTP请求
pip install requests

# 缓存（可选）
pip install redis

# WebSocket支持
pip install python-socketio python-engineio eventlet
```

### 2. 测试系统

运行集成测试确保所有组件正常：

```bash
python test_integration.py
```

所有测试应该显示 `[PASS]` 状态。

### 3. 启动系统

#### 方法1：启动完整系统（推荐）
```bash
python start_system.py
```

#### 方法2：仅启动Web服务
```bash
python start_web.py
```

#### 方法3：直接启动Flask应用
```bash
python app.py
```

### 4. 访问系统

启动后访问以下地址：

- **基础仪表板**: http://localhost:5000
- **增强仪表板**: http://localhost:5000/enhanced
- **系统状态**: http://localhost:5000/status

## 项目结构

```
WB_yuqing_xt/
├── app.py                    # Flask主应用
├── start_system.py          # 系统启动脚本
├── start_web.py             # Web服务启动脚本
├── spider_launcher.py       # 爬虫启动器
├── test_integration.py      # 集成测试脚本
├── requirements.txt          # 依赖列表
├── README.md                # 项目说明
├── analysis/                # 数据分析模块
│   ├── data_analyzer.py     # 数据分析器
│   └── data_manager.py      # 数据管理器
├── integration/             # 系统集成模块
│   └── spider_integration.py # 爬虫集成器
├── spider/                  # 爬虫模块
│   ├── article_data/        # 文章爬虫
│   └── comment_spider/      # 评论爬虫
├── templates/               # HTML模板
├── static/                  # 静态资源
├── config/                  # 配置文件
├── util/                    # 工具模块
├── data/                    # 数据存储
└── logs/                    # 日志文件
```

## 功能说明

### 数据采集
- 自动抓取微博热门话题文章
- 采集相关评论数据
- 智能去重和防封禁机制

### 数据分析
- 情感分析：识别正面、负面、中性情感
- 关键词提取：TF-IDF算法提取热门关键词
- 趋势分析：时间序列数据分析
- 地域分析：按地区统计发布情况
- 作者分析：识别活跃用户

### 可视化展示
- 实时数据更新（WebSocket）
- 交互式图表（Chart.js）
- 响应式设计，支持移动端
- 多标签页数据分析界面

## 常见问题

### 1. 依赖安装失败

如果某些包安装失败，可以尝试：

```bash
# 使用清华镜像
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

# 或者逐个安装
pip install flask pandas numpy jieba psutil requests
```

### 2. 端口占用

如果5000端口被占用，可以修改 `app.py` 中的端口号：

```python
socketio.run(app, debug=True, host='0.0.0.0', port=8080)  # 改为8080
```

### 3. Redis连接失败

如果Redis不可用，系统会自动使用内存缓存，不影响主要功能。

### 4. 爬虫无法获取数据

检查网络连接，可能需要更新爬虫配置文件中的Cookie信息。

### 5. 中文显示问题

确保系统支持UTF-8编码，在Windows上可能需要设置环境变量：

```cmd
set PYTHONIOENCODING=utf-8
```

## 性能优化

### 1. 启用Redis缓存

安装并启动Redis服务：

```bash
# Windows
# 下载Redis for Windows并启动

# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis-server
```

### 2. 调整爬虫频率

修改 `config/spider_config.py` 中的请求间隔：

```python
REQUEST_CONFIG = {
    'min_request_interval': 30,    # 最小间隔30秒
    'max_request_interval': 120,   # 最大间隔120秒
    ...
}
```

### 3. 限制数据量

在 `analysis/data_manager.py` 中调整获取数据的数量：

```python
def get_recent_articles(self, limit=100):  # 减少获取数量
```

## 开发扩展

### 添加新的分析算法

1. 在 `analysis/data_analyzer.py` 中添加新方法
2. 在 `app.py` 中添加对应的API接口
3. 在前端添加展示组件

### 添加新的数据源

1. 在 `spider/` 目录下创建新的爬虫模块
2. 在 `integration/spider_integration.py` 中添加集成逻辑
3. 更新数据管理器支持新的数据格式

### 自定义前端界面

1. 修改 `templates/` 中的HTML模板
2. 更新 `static/css/` 中的CSS样式
3. 扩展 `static/js/` 中的JavaScript功能

## 监控和维护

### 查看日志

系统日志保存在 `logs/` 目录下。

### 数据备份

定期备份 `data/` 目录中的数据库文件。

### 性能监控

访问 http://localhost:5000/status 查看系统运行状态。

## 技术支持

如遇问题，请：

1. 查看控制台输出的错误信息
2. 运行 `python test_integration.py` 进行诊断
3. 检查 `logs/` 目录下的日志文件
4. 确认所有依赖已正确安装

## 许可证

本项目采用MIT许可证。