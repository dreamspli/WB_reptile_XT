from datetime import datetime, timedelta
import time
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from util.stringUtil import clean_string
import requests
import os
import csv
import json
import hashlib
import argparse
import threading
from concurrent.futures import ThreadPoolExecutor
import random


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='微博评论爬虫')
    parser.add_argument('--force-all', action='store_true', help='强制重新检查所有文章')
    parser.add_argument('--article-id', type=str, help='指定处理特定文章ID')
    parser.add_argument('--high-freq', type=int, help='设置高频检查间隔(小时)')
    parser.add_argument('--medium-freq', type=int, help='设置中频检查间隔(小时)')
    parser.add_argument('--low-freq', type=int, help='设置低频检查间隔(小时)')
    return parser.parse_args()


# 创建线程锁，用于保护文件写入操作
csv_lock = threading.Lock()


def init_csv():
    if not os.path.exists("comment_data.csv"):
        with open("comment_data.csv", "w", encoding="utf-8", newline="") as f:
            csv.writer(f).writerow(
                [
                    'articleId',  # 文章id
                    'id',  # 评论信息id
                    'text_raw',  # 评论内容
                    'created_at',  # 创建日期
                    'source',  # 发布位置 少部分没有这个值
                    'like_counts',  # 点赞数
                    'articleId',  # 微博id
                    'userId',  # 评论用户id
                    'userName',  # 评论用户名称
                    'gender',  # 性别
                    'userHomeUrl'  # 评论用户主页地址
                ])


# 存储上次处理状态的文件
LAST_PROCESSED_FILE = "last_processed.json"


# 初始化或加载上次处理状态
def init_or_load_last_processed():
    if os.path.exists(LAST_PROCESSED_FILE):
        with open(LAST_PROCESSED_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return {
            "last_processed_time": "",
            "processed_articles": {},
            "check_frequency": {
                "high": 1,  # 高频检查间隔(小时)
                "medium": 6,  # 中频检查间隔(小时)
                "low": 24  # 低频检查间隔(小时)
            }
        }


# 保存处理状态
def save_last_processed(last_processed):
    with open(LAST_PROCESSED_FILE, "w", encoding="utf-8") as f:
        json.dump(last_processed, f, ensure_ascii=False, indent=2)


def getJsonHtml(url, params, max_retries=5, retry_delay=30):
    """获取JSON数据，添加重试机制和动态延迟"""
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
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0",
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

    for attempt in range(max_retries):
        try:
            # 使用动态延迟，避免请求过于频繁
            delay = random.uniform(0.5, 1.5)
            time.sleep(delay)

            response = requests.get(url, headers=headers, cookies=cookies, params=params)
            return response.json()
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"请求失败: {e}，{retry_delay}秒后重试...")
                time.sleep(retry_delay)
            else:
                print(f"请求失败，已达到最大重试次数: {e}")
                raise


def get_article_modification_time():
    """获取文章数据文件的修改时间"""
    if os.path.exists("../article_data/article_data.csv"):
        return datetime.fromtimestamp(os.path.getmtime("../article_data/article_data.csv")).strftime(
            "%Y-%m-%d %H:%M:%S")
    return ""


def get_updated_articles(last_processed, args=None):
    """获取需要处理的文章列表，包括新文章和需要重新检查的旧文章"""
    article_list = []
    current_time = datetime.now()
    last_processed_time = last_processed.get("last_processed_time", "")
    processed_articles = last_processed.get("processed_articles", {})
    check_frequency = last_processed.get("check_frequency", {
        "high": 1,  # 高频检查间隔(小时)
        "medium": 6,  # 中频检查间隔(小时)
        "low": 24  # 低频检查间隔(小时)
    })

    # 如果提供了命令行参数，更新检查频率
    if args:
        if args.high_freq is not None:
            check_frequency["high"] = args.high_freq
            last_processed["check_frequency"]["high"] = args.high_freq
        if args.medium_freq is not None:
            check_frequency["medium"] = args.medium_freq
            last_processed["check_frequency"]["medium"] = args.medium_freq
        if args.low_freq is not None:
            check_frequency["low"] = args.low_freq
            last_processed["check_frequency"]["low"] = args.low_freq

    for attempt in range(3):
        try:
            # 读取所有文章
            all_articles = {}
            with open("../article_data/article_data.csv", "r", encoding="utf-8", newline="") as f:
                reader = csv.reader(f)
                headers = next(reader)

                for row in reader:
                    article_id = row[0]
                    all_articles[article_id] = row

                    # 如果指定了特定文章ID，只处理该文章
                    if args and args.article_id and article_id != args.article_id:
                        continue

                    # 如果是新文章，直接添加到待处理列表
                    if article_id not in processed_articles:
                        article_list.append(row)
                        print(f"发现新文章: {article_id}")
        except (IOError, PermissionError) as e:
            if attempt < 3 - 1:
                print(f"读取文章数据失败: {e}，{5}秒后重试...")
                time.sleep(5)
            else:
                print(f"读取文章数据失败，已达到最大重试次数: {e}")
                raise

    # 检查已处理的文章是否需要重新获取评论
    for article_id, article_info in processed_articles.items():
        # 如果指定了特定文章ID，只处理该文章
        if args and args.article_id and article_id != args.article_id:
            continue

        # 如果文章不在当前文章列表中，跳过
        if article_id not in all_articles:
            continue

        # 如果强制重新检查所有文章，直接添加到待处理列表
        if args and args.force_all:
            article_list.append(all_articles[article_id])
            print(f"强制重新检查文章: {article_id}")
            continue

        # 获取文章的下次检查时间
        next_check_time = article_info.get("next_check_time", "")
        if not next_check_time:
            # 如果没有设置下次检查时间，设置一个默认值
            next_check_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
            processed_articles[article_id]["next_check_time"] = next_check_time

        # 如果当前时间已经超过下次检查时间，将文章添加到待处理列表
        if current_time >= datetime.strptime(next_check_time, "%Y-%m-%d %H:%M:%S"):
            article_list.append(all_articles[article_id])
            print(f"重新检查文章: {article_id}")

    return article_list


def determine_check_frequency(article_info):
    """根据文章信息确定检查频率"""
    # 这里可以根据文章的评论数量、热度等因素确定检查频率
    # 简单实现：根据评论数量确定
    comment_count = article_info.get("comment_count", 0)

    if comment_count > 100:
        return "high"
    elif comment_count > 20:
        return "medium"
    else:
        return "low"


def getAllArticleList():
    articleList = []
    with open("../article_data/article_data.csv", "r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            articleList.append(row)
        return articleList


def pareseJson(json, articleId, params, processed_comments=None):
    """解析评论JSON数据，检测重复评论"""
    if processed_comments is None:
        processed_comments = set()

    duplicate_found = False
    params['max_id'] = json['max_id']
    commentList = json['data']

    if not commentList:
        return False, processed_comments

    for comment in commentList:
        # 创建评论唯一标识（用户ID + 评论内容的哈希值）
        userId = comment['user']['id']
        text_raw = clean_string(comment['text_raw'])
        comment_hash = f"{userId}_{hashlib.md5(text_raw.encode()).hexdigest()}"

        # 检查是否重复
        if comment_hash in processed_comments:
            print(f"发现重复评论，文章ID: {articleId}, 用户ID: {userId}")
            duplicate_found = True
            break

        processed_comments.add(comment_hash)

        # 处理评论数据
        id = comment['id']
        created_at = datetime.strptime(comment['created_at'], "%a %b %d %H:%M:%S %z %Y").strftime(
            "%Y-%m-%d %H:%M:%S")
        source = comment.get('source', '来自').replace('来自', '').strip()
        like_counts = comment['like_counts']
        userName = comment['user']['screen_name']
        gender = '男'
        g = comment['user']['gender']
        if g == 'f':
            gender = '女'
        userHomeUrl = 'https://weibo.com/u/%s' % comment['user']['id']

        print(articleId, id, text_raw, created_at, source, like_counts, userId, userName, gender, userHomeUrl)

        # 使用线程锁保护文件写入操作
        with csv_lock:
            with open("comment_data.csv", "a", encoding="utf-8", newline="") as f:
                csv.writer(f).writerow(
                    [articleId, id, text_raw, created_at, source, like_counts, userId, userName, gender, userHomeUrl])

    # 如果发现重复评论，停止处理
    if duplicate_found:
        return True, processed_comments

    # 如果没有重复且有下一页，继续处理
    if json['max_id'] != 0:
        jsonHtml = getJsonHtml('https://weibo.com/ajax/statuses/buildComments', params)
        return pareseJson(jsonHtml, articleId, params, processed_comments)

    return False, processed_comments


def process_article(article, last_processed, url):
    """处理单个文章的评论，用于多线程处理"""
    try:
        articleId = article[0]
        print(f"处理文章ID: {articleId}")

        # 获取当前时间
        current_time = datetime.now()
        current_time_str = current_time.strftime("%Y-%m-%d %H:%M:%S")

        # 获取该文章已处理的评论集合
        article_processed_comments = set()
        if articleId in last_processed.get("processed_articles", {}):
            # 如果之前已经处理过这篇文章，可以从保存的状态中恢复
            # 但由于我们没有保存完整的评论哈希集合（这可能会很大），所以这里使用空集合
            # 在实际应用中，可以考虑为每篇文章保存一个单独的评论哈希文件
            pass

        params = {
            "id": articleId,
            "is_show_bulletin": "2",
        }
        jsonHtml = getJsonHtml(url, params)

        if jsonHtml:
            duplicate_found, processed_comments = pareseJson(jsonHtml, articleId, params, article_processed_comments)

            # 获取文章信息
            with threading.Lock():  # 保护对共享数据的访问
                article_info = last_processed["processed_articles"].get(articleId, {})
                article_info.update({
                    "last_processed_time": current_time_str,
                    "duplicate_found": duplicate_found,
                    "comment_count": len(processed_comments)
                })

                # 确定下次检查时间
                frequency_type = determine_check_frequency(article_info)
                hours_to_add = last_processed["check_frequency"].get(frequency_type, 24)  # 默认24小时
                next_check_time = current_time + timedelta(hours=hours_to_add)
                article_info["next_check_time"] = next_check_time.strftime("%Y-%m-%d %H:%M:%S")
                article_info["check_frequency"] = frequency_type

                # 更新处理状态
                last_processed["processed_articles"][articleId] = article_info

            print(f"文章 {articleId} 处理完成，下次检查时间: {article_info['next_check_time']} (频率: {frequency_type})")
            return True
        return False
    except Exception as e:
        print(f"处理文章 {article[0]} 时出错: {e}")
        return False


def start():
    url = "https://weibo.com/ajax/statuses/buildComments"
    init_csv()

    # 加载上次处理状态
    last_processed = init_or_load_last_processed()
    current_time = datetime.now()
    current_time_str = current_time.strftime("%Y-%m-%d %H:%M:%S")
    check_frequency = last_processed.get("check_frequency", {
        "high": 1,  # 高频检查间隔(小时)
        "medium": 6,  # 中频检查间隔(小时)
        "low": 24  # 低频检查间隔(小时)
    })

    # 获取需要处理的文章列表
    articles_to_process = get_updated_articles(last_processed)

    if not articles_to_process:
        print("没有需要处理的文章")
        return

    print(f"微博评论信息抓取中...共有 {len(articles_to_process)} 篇文章需要处理")

    # 处理每篇文章
    for article in articles_to_process:
        articleId = article[0]
        print(f"处理文章ID: {articleId}")

        # 获取该文章已处理的评论集合
        article_processed_comments = set()
        if articleId in last_processed.get("processed_articles", {}):
            # 如果之前已经处理过这篇文章，可以从保存的状态中恢复
            # 但由于我们没有保存完整的评论哈希集合（这可能会很大），所以这里使用空集合
            # 在实际应用中，可以考虑为每篇文章保存一个单独的评论哈希文件
            pass

        time.sleep(1)
        params = {
            "id": articleId,
            "is_show_bulletin": "2",
        }
        jsonHtml = getJsonHtml(url, params)

        if jsonHtml:
            duplicate_found, processed_comments = pareseJson(jsonHtml, articleId, params, article_processed_comments)

            # 获取文章信息
            article_info = last_processed["processed_articles"].get(articleId, {})
            article_info.update({
                "last_processed_time": current_time_str,
                "duplicate_found": duplicate_found,
                "comment_count": len(processed_comments)
            })

            # 确定下次检查时间
            frequency_type = determine_check_frequency(article_info)
            hours_to_add = check_frequency.get(frequency_type, 24)  # 默认24小时
            next_check_time = current_time + timedelta(hours=hours_to_add)
            article_info["next_check_time"] = next_check_time.strftime("%Y-%m-%d %H:%M:%S")
            article_info["check_frequency"] = frequency_type

            # 更新处理状态
            last_processed["processed_articles"][articleId] = article_info

            print(f"文章 {articleId} 处理完成，下次检查时间: {article_info['next_check_time']} (频率: {frequency_type})")

    # 更新最后处理时间
    last_processed["last_processed_time"] = current_time_str

    # 保存处理状态
    save_last_processed(last_processed)

    print("微博评论信息抓取完成")


def main():
    # 解析命令行参数
    args = parse_arguments()

    # 加载上次处理状态
    last_processed = init_or_load_last_processed()

    # 打印当前配置信息
    check_frequency = last_processed.get("check_frequency", {})
    print(f"当前检查频率配置:")
    print(f"  高频: {check_frequency.get('high', 1)}小时")
    print(f"  中频: {check_frequency.get('medium', 6)}小时")
    print(f"  低频: {check_frequency.get('low', 24)}小时")

    if args.force_all:
        print("强制重新检查所有文章")

    if args.article_id:
        print(f"只处理文章ID: {args.article_id}")

    # 初始化CSV文件
    init_csv()

    # 获取需要处理的文章列表
    articles_to_process = get_updated_articles(last_processed, args)

    if not articles_to_process:
        print("没有需要处理的文章")
        return

    print(f"微博评论信息抓取中...共有 {len(articles_to_process)} 篇文章需要处理")

    # 使用线程池并行处理文章
    url = 'https://weibo.com/ajax/statuses/buildComments'
    max_workers = min(10, len(articles_to_process))  # 最多10个线程，或者文章数量（取较小值）
    processed_count = 0

    print(f"启动多线程处理，线程数: {max_workers}")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有文章处理任务
        futures = [executor.submit(process_article, article, last_processed, url) for article in articles_to_process]

        # 等待所有任务完成
        for future in futures:
            try:
                if future.result():
                    processed_count += 1
            except Exception as e:
                print(f"处理文章时出错: {e}")

    print(f"成功处理了 {processed_count}/{len(articles_to_process)} 篇文章")

    # 更新最后处理时间
    last_processed["last_processed_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 保存处理状态
    save_last_processed(last_processed)

    print("微博评论信息抓取完成")


if __name__ == "__main__":
    main()
