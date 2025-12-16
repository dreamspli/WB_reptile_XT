import csv
import os

import numpy as np
import requests


def init_csv():
    if not os.path.exists('arcTypeData.csv'):
        with open('arcTypeData.csv', 'w', newline="", encoding='utf-8') as f:
            csv.writer(f).writerow(['类别标题', '分组id', '分类id'])
    else:
        return True


def getJsonHtml(url):
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
    url = "https://weibo.com/ajax/feed/allGroups"
    params = {
        "is_new_segment": "1",
        "fetch_hot": "1"
    }
    response = requests.get(url, headers=headers, cookies=cookies, params=params)
    return response.json()


def parseJson(json):
    arcTypeList = np.append(json['groups'][3]['group'], json['groups'][4]['group'])
    for arcType in arcTypeList:
        with open('arcTypeData.csv', 'a+', newline="", encoding='utf-8') as f:
            csv.writer(f).writerow([arcType['title'], arcType['gid'], arcType['containerid']])


def start():
    if init_csv():
        print('csv文件已存在')
        return None
    else:
        url = 'https://weibo.com/ajax/feed/allGroups'
        json_html = getJsonHtml(url)
        parseJson(json_html)


if __name__ == '__main__':
    start()
