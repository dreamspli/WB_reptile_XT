# 微博舆情监测系统

一个完整的实时微博数据采集、分析和展示系统。

## 功能特性

### 🕷️ 智能爬虫系统
- **防封禁机制**: User-Agent轮换、智能延迟、错误重试
- **自适应调节**: 根据成功率自动调整请求频率
- **多重保护**: 请求限制、连接超时、异常处理

### 📊 多维度数据分析
- **情感分析**: 基于词典的情感倾向分析
- **关键词提取**: TF-IDF算法提取热门关键词
- **地域分析**: 按地区统计发布情况和参与度
- **作者分析**: 活跃作者识别和影响力评估
- **时间分析**: 发布时间模式和活跃时段分析
- **分类分析**: 按内容类别进行统计分析

### 🎨 增强版可视化界面
- **多标签页设计**: 总览、分类、地域、作者、时间分析
- **交互式图表**: 基于Chart.js的动态数据可视化
- **文章详情**: 点击查看完整文章信息和评论
- **分类筛选**: 按文章类别筛选和分析
- **实时更新**: WebSocket推送最新数据

### 💾 数据存储与缓存
- **SQLite数据库**: 存储分析结果和历史数据
- **Redis缓存**: 提高查询性能（可选）
- **智能缓存**: 根据数据更新频率调整缓存策略

## 系统架构

```
微博舆情监测系统/
├── spider/                 # 爬虫模块
│   ├── article_data/       # 文章数据爬虫
│   ├── comment_spider/     # 评论数据爬虫
│   └── arcType/           # 文章类型配置
├── analysis/              # 数据分析模块
│   ├── data_analyzer.py   # 数据分析器
│   └── data_manager.py    # 数据管理器
├── integration/           # 系统集成模块
│   └── spider_integration.py
├── templates/             # Web模板
├── static/               # 静态资源
├── view/                 # Flask视图
├── util/                 # 工具模块
├── app.py               # Flask应用主文件
└── start_system.py      # 系统启动脚本
```

## 安装和配置

### 1. 环境要求

- Python 3.7+
- Redis (可选，用于缓存)

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置Redis (可选)

如果要使用Redis缓存，请确保Redis服务正在运行：

```bash
# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis-server

# Windows
# 下载并安装Redis for Windows
```

## 使用方法

### 快速启动

```bash
# 启动完整系统（包括爬虫）
python start_system.py

# 仅启动Web服务（不包括爬虫）
python start_system.py --web-only

# 启动系统但不包括爬虫
python start_system.py --no-spider
```

### 分别启动各个模块

#### 1. 启动文章爬虫
```bash
cd spider/article_data
python article_spider.py
```

#### 2. 启动评论爬虫
```bash
cd spider/comment_spider
python comment_spider.py
```

#### 3. 启动数据集成服务
```bash
python integration/spider_integration.py
```

#### 4. 启动Web应用
```bash
python app.py
```

### 访问监控面板

启动系统后，在浏览器中访问：

**基础版仪表板:**
```
http://localhost:5000
```

**增强版仪表板 (推荐):**
```
http://localhost:5000/enhanced
```

**系统状态监控:**
```
http://localhost:5000/status
```

## 功能说明

### 数据采集

- **文章采集**: 自动抓取微博热门话题文章
- **评论采集**: 针对热门文章采集用户评论
- **去重机制**: 自动识别和过滤重复内容
- **增量更新**: 只采集新增数据，提高效率

### 数据分析

- **情感分析**: 基于词典的情感倾向分析
- **关键词提取**: 使用TF-IDF算法提取热门关键词
- **趋势分析**: 分析发布时间、参与度等趋势
- **统计分析**: 各类数据的统计汇总

### 实时展示

- **实时更新**: 基于WebSocket的实时数据推送
- **多维度展示**: 统计卡片、趋势图表、关键词云等
- **响应式设计**: 支持桌面和移动设备访问
- **交互式图表**: 基于Chart.js的动态图表

## API接口

系统提供以下REST API接口：

- `GET /api/stats` - 获取基础统计数据
- `GET /api/sentiment` - 获取情感分析数据
- `GET /api/keywords` - 获取热门关键词
- `GET /api/trends` - 获取趋势分析数据
- `GET /api/recent_articles` - 获取最新文章列表

## 配置说明

### 爬虫配置

在 `spider/article_data/article_spider.py` 中可以配置：
- 抓取间隔时间
- 抓取数量限制
- 请求头和Cookie信息

### 分析配置

在 `analysis/data_analyzer.py` 中可以配置：
- 情感词典
- 关键词提取参数
- 分析算法参数

### Web配置

在 `app.py` 中可以配置：
- 服务器端口
- 数据更新频率
- WebSocket设置

## 数据存储

### CSV文件
- `spider/article_data/article_data.csv` - 文章数据
- `spider/comment_spider/comment_data.csv` - 评论数据

### SQLite数据库
- `data/analysis.db` - 分析结果存储

### Redis缓存 (可选)
- 实时数据缓存
- 提高查询性能

## 故障排除

### 常见问题

1. **爬虫无法获取数据**
   - 检查网络连接
   - 更新Cookie和请求头信息
   - 检查目标网站是否有反爬虫措施

2. **Web界面无法访问**
   - 确认Flask应用已启动
   - 检查端口5000是否被占用
   - 查看控制台错误信息

3. **数据分析结果异常**
   - 检查CSV文件格式是否正确
   - 确认jieba分词库已正确安装
   - 查看分析日志信息

### 日志查看

系统运行时会在控制台输出详细日志信息，包括：
- 数据采集状态
- 分析处理进度
- 错误和警告信息

## 扩展开发

### 添加新的分析算法

1. 在 `analysis/data_analyzer.py` 中添加新的分析方法
2. 在 `app.py` 中添加对应的API接口
3. 在前端添加相应的展示组件

### 添加新的数据源

1. 在 `spider/` 目录下创建新的爬虫模块
2. 在 `integration/spider_integration.py` 中添加集成逻辑
3. 更新数据管理器以支持新的数据格式

## 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 贡献

欢迎提交Issue和Pull Request来改进这个项目。

## 联系方式

如有问题或建议，请通过以下方式联系：
- 提交GitHub Issue
- 发送邮件至项目维护者
