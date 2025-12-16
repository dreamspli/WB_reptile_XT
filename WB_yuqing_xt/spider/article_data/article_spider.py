import csv
import os
import sys
import time
from datetime import datetime
import requests
import sqlite3

# 添加项目根目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from util import stringUtil

seen_ids = set()


def setup_db(db_name='seen_ids.db'):
    """设置数据库并创建表"""
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS seen_ids (id TEXT PRIMARY KEY)''')
    conn.commit()
    conn.close()


def load_seen_ids_from_db(db_name='seen_ids.db'):
    """从数据库加载 seen_ids"""
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute("SELECT id FROM seen_ids")
    ids = {row[0] for row in c.fetchall()}
    conn.close()
    return ids


def add_seen_id_to_db(_id, db_name='seen_ids.db'):
    """向数据库添加 seen_id"""
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO seen_ids (id) VALUES (?)", (_id,))
        conn.commit()
    except sqlite3.IntegrityError:
        pass  # 如果ID已经存在，则忽略错误
    finally:
        conn.close()


def init_csv():
    if not os.path.exists("article_data.csv"):
        with open("article_data.csv", "w", encoding="utf-8", newline="") as f:
            csv.writer(f).writerow(
                [
                    "id",  # 帖子id
                    "title_raw",  # 帖子内容
                    "reposts_count",  # 转发数
                    "comments_count",  # 评论数
                    "attitudes_count",  # 点赞数
                    "region_name",  # 地区
                    "created_at",  # 发布时间
                    "articleType",  # 帖子类型
                    "articleUrl",  # 帖子链接
                    "authorId",  # 作者id
                    "authorName",  # 作者名称
                    "authorHomeUrl"  # 作者主页链接
                ])


def getAllTypeList():
    allTypeList = []
    with open("../arcType/arcTypeData.csv", "r", encoding="utf-8", newline='') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            allTypeList.append(row)
    return allTypeList


def get_random_user_agent():
    """获取随机User-Agent"""
    import random
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/120.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ]
    return random.choice(user_agents)

def getJsonHtml(url, params):
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "cache-control": "no-cache",
        "client-version": "v2.47.91",
        "pragma": "no-cache",
        "priority": "u=1, i",
        "referer": "https://weibo.com/hot/weibo/102803",
        "sec-ch-ua": "\"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"138\", \"Microsoft Edge\";v=\"138\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "server-version": "v2025.07.18.2",
        "user-agent": get_random_user_agent(),  # 使用随机User-Agent
        "x-requested-with": "XMLHttpRequest",
        "x-xsrf-token": "wyg8pnAyjxd215-Q53y-GR-C"
    }
    cookies = {
    "SCF": "ArEQ8pxN7wYjmTJHmnDz5jxxqNIc-Pz-V8FIrb6MiibXB36OhhLech6DftGrDD4ged2PjGVCZ9uFfQfkoVC9204.",
    "XSRF-TOKEN": "jp54kLVJ01qadBrKuIYujf2Y",
    "ALF": "1756041241",
    "SUB": "_2A25Fh_NJDeRhGeFL4loQ9SjKzDqIHXVm_QqBrDV8PUJbkNANLUKlkW1NfW51jH5F2k3xHTlfPwfXmoK8E5jYDbqr",
    "SUBP": "0033WrSXqPxfM725Ws9jqgMF55529P9D9WFB4FMKCmXCvbWfKDSlwcFN5JpX5KMhUgL.FoMf1KnpSKqcS0q2dJLoIp7LxKML1KBLBKnLxKqL1hnLBoMNSK.ReK-cSoMc",
    "WBPSESS": "Yv60eaCdB1ow4UjL989SB07OjqRCUL3fHeGANXk6kPt2hiBnK2oqLpLpSPP0_akfRvF4bP5bSxLMoykoh9cPMv-NreCiIqJ20h9FVuBWhaMbNg-yjRM4n9bmVchXLp6wObUYCeD_G16yC9dzzS9b4w=="
}

    # 添加重试机制
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # 添加随机延迟，避免请求过于频繁
            import random
            time.sleep(random.uniform(1, 3))

            response = requests.get(url, headers=headers, cookies=cookies, params=params, timeout=30)

            # 检查响应状态
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:  # 请求过于频繁
                print(f"请求过于频繁 (429)，等待 {60 * (attempt + 1)} 秒...")
                time.sleep(60 * (attempt + 1))
                continue
            elif response.status_code in [403, 401]:  # 被封禁
                print(f"访问被拒绝 ({response.status_code})，可能IP被封禁")
                raise Exception(f"IP可能被封禁: {response.status_code}")
            else:
                print(f"请求失败，状态码: {response.status_code}")
                if attempt < max_retries - 1:
                    time.sleep(30 * (attempt + 1))
                    continue
                else:
                    raise Exception(f"请求失败: {response.status_code}")

        except requests.exceptions.Timeout:
            print(f"请求超时 (尝试 {attempt + 1}/{max_retries})")
            if attempt < max_retries - 1:
                time.sleep(30)
                continue
            else:
                raise Exception("请求超时")

        except requests.exceptions.ConnectionError:
            print(f"连接错误 (尝试 {attempt + 1}/{max_retries})")
            if attempt < max_retries - 1:
                time.sleep(60)
                continue
            else:
                raise Exception("连接错误")

        except Exception as e:
            print(f"请求异常 (尝试 {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(30)
                continue
            else:
                raise e

    raise Exception("所有重试都失败了")


def parseJson(json, articleTypes):
    global seen_ids
    articleList = json.get('statuses', [])
    found_duplicate = False

    for article in articleList:
        _id = article['id']
        if _id in seen_ids:
            found_duplicate = True
            print(f"发现重复内容 ID: {_id}，准备暂停爬取...")
            break  # 遇到重复就不再写入新的数据

        seen_ids.add(_id)
        add_seen_id_to_db(_id)  # 每次添加新ID时都保存到数据库

        # 以下是你原本的数据提取部分
        title_raw = stringUtil.clean_string(article['text_raw'])
        reposts_count = article['reposts_count']
        comments_count = article['comments_count']
        attitudes_count = article.get('attitudes_count', 0)
        region_name = article.get('region_name', '发布于').replace('发布于', '').strip()
        created_at = datetime.strptime(article['created_at'], '%a %b %d %H:%M:%S %z %Y').strftime('%Y-%m-%d %H:%M:%S')
        articleType = articleTypes
        articleUrl = f"https://weibo.com/article/{article['user']['id']}/{article['mblogid']}"
        authorId = article['user']['id']
        authorName = article['user']['screen_name']
        authorHomeUrl = f"https://weibo.com/u/{article['user']['id']}"

        with open("article_data.csv", "a", encoding="utf-8", newline="") as f:
            csv.writer(f).writerow(
                [_id, title_raw, reposts_count, comments_count, attitudes_count, region_name, created_at, articleType,
                 articleUrl, authorId, authorName, authorHomeUrl])

    return found_duplicate


def for_get(url, arcTypeList):
    global seen_ids
    found_duplicate = False

    for arcType in arcTypeList:
        print("正在爬取" + arcType[0] + "类型微博")
        time.sleep(1)
        params = {
            "since_id": 0,
            "refresh": 1,
            "group_id": arcType[1],
            "containerid": arcType[2],
            "extparam": "discover|new_feed",
            "max_id": 0,
            "count": 10
        }
        jsonHtml = getJsonHtml(url, params)
        if parseJson(jsonHtml, arcType[0]):
            found_duplicate = True
            break  # 如果这个类型发现了重复，就跳出循环

    return found_duplicate


def start():
    url = 'https://weibo.com/ajax/feed/hottimeline'
    init_csv()
    arcTypeList = getAllTypeList()
    # 初始化数据库
    setup_db()
    load_seen_ids_from_db()

    # 添加请求计数器和错误计数器
    request_count = 0
    error_count = 0
    max_requests_per_hour = 100  # 每小时最大请求数

    while True:
        try:
            print(f"微博内容爬取开始 (第{request_count + 1}次请求)")
            duplicate_found = for_get(url, arcTypeList)
            request_count += 1
            error_count = 0  # 重置错误计数

            if duplicate_found:
                print("检测到重复内容，暂停爬取 5 分钟...")
                time.sleep(300)  # 5分钟
                seen_ids.clear()  # 清空缓存，重新开始
            else:
                print("本次爬取未发现重复内容")

            # 智能延迟策略
            if request_count >= max_requests_per_hour:
                print("已达到每小时请求限制，休息1小时...")
                time.sleep(3600)  # 休息1小时
                request_count = 0
            elif error_count > 0:
                # 如果有错误，延长等待时间
                wait_time = min(300, 60 * (2 ** error_count))  # 指数退避，最多5分钟
                print(f"由于错误，等待 {wait_time} 秒...")
                time.sleep(wait_time)
            else:
                # 正常情况下随机等待30-120秒
                import random
                wait_time = random.randint(30, 120)
                print(f"正常等待 {wait_time} 秒...")
                time.sleep(wait_time)

        except Exception as e:
            error_count += 1
            print(f"爬取过程中出错 (第{error_count}次): {e}")

            if error_count >= 5:
                print("连续错误次数过多，暂停30分钟...")
                time.sleep(1800)  # 30分钟
                error_count = 0
            else:
                # 错误后等待时间逐渐增加
                wait_time = 60 * error_count
                print(f"等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)


if __name__ == '__main__':
    start()
