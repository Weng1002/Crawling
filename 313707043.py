import click
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import json
import random
import os
import re
from tqdm import tqdm
from collections import Counter

@click.command()
@click.argument("command")
@click.argument("start_date", required=False)
@click.argument("end_date", required=False)
@click.argument("keyword", required=False)

def main(command, start_date, end_date, keyword):
    if command == "crawl":
        for filename in ['articles.jsonl', 'popular_articles.jsonl']:
            if os.path.exists(filename):
                os.remove(filename)
        crawl_articles()
        
    elif command == "push":
        if not start_date or not end_date:
            print("請輸入起始與結束日期。")
            return
        try:
            start_date = normalize_date(start_date)
            end_date = normalize_date(end_date)
        except ValueError as e:
            print(f"日期格式錯誤：{e}")
            return
        
        Push(start_date, end_date)
    
    elif command == "popular":
        if not start_date or not end_date:
            print("請輸入起始與結束日期。")
            return
        try:
            start_date = normalize_date(start_date)
            end_date = normalize_date(end_date)
        except ValueError as e:
            print(f"日期格式錯誤：{e}")
            return
        
        Popular(start_date, end_date)
    
    elif command == "keyword":
        if not start_date or not end_date:
            print("請輸入起始與結束日期。")
            return
        try:
            start_date = normalize_date(start_date)
            end_date = normalize_date(end_date)
        except ValueError as e:
            print(f"日期格式錯誤：{e}")
            return
        
        if not keyword:
            print("請輸入關鍵字。")
            return
        if any(c.isspace() for c in keyword):
            print("關鍵字不能包含空白字元（space、tab 等）。")
            return

        Keyword(start_date, end_date, keyword)
             
    else:
        print(f"未知指令：{command}")

HEADERS = {
    'User-Agent':'Mozilla/5.0',
    'cookie':'over18=1'
}

def normalize_date(date_str):
    if '/' in date_str:
        parts = date_str.split('/')
        if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
            mm = parts[0].zfill(2)
            dd = parts[1].zfill(2)
            date_str = mm + dd
        else:
            raise ValueError("請使用正確的格式")
    elif len(date_str) == 4 and date_str.isdigit():
        pass
    else:
        raise ValueError("請使用正確的格式")

    try:
        datetime.strptime(date_str, "%m%d") 
    except ValueError:
        raise ValueError("日期無效")

    return date_str

# ----------------------------- Crawl -----------------------------

def extract_meta_value(soup, label):
    tags = soup.select('span.article-meta-tag')
    vals = soup.select('span.article-meta-value')

    for tag, val in zip(tags, vals):
        if tag.text.strip() == label:
            return val.text.strip()
    
    # 處理特殊情況，沒有時間欄位時
    if label == '時間':
        f2_texts = [span.text.strip() for span in soup.select('span.f2')]

        for line in f2_texts:
            match = re.search(r'(\d{2}/\d{2}/\d{4})\s+(\d{2}:\d{2}:\d{2})', line)
            if match:
                date_part = match.group(1)  
                time_part = match.group(2)  
                dt = datetime.strptime(date_part + ' ' + time_part, '%m/%d/%Y %H:%M:%S')
                return dt.strftime('%a %b %d %H:%M:%S %Y')

    return None


def crawl_articles():
    is_2024_started = False
    start_index = 3640  #3647(2024)   3371(2023)
    end_index = 3920   #3916(2024)   3647(2023)

    articles = []
    popular_articles = []

    for index in range(start_index, end_index+1):  
        url = f'https://www.ptt.cc/bbs/Beauty/index{index}.html'
        print("\n")
        print(f'目前的列表: {url}')

        res = requests.get(url, headers=HEADERS, timeout=10)
        res.raise_for_status() # 檢查是否取得成功
        soup = BeautifulSoup(res.text, 'html.parser')

        entries = soup.select('div.r-ent') # 取得文章列表
        for entry in entries:
            link_tag = entry.select_one('a')
            if not link_tag:
                continue  # 無網址的文章

            post_url = 'https://www.ptt.cc' + link_tag['href']
            title_text = link_tag.text.strip()
            date_tag = entry.select_one('div.date')
            post_date = date_tag.text.strip() if date_tag else ''
            print(f'抓到的文章：{post_url} | 標題：{title_text} | 列表時間：{post_date}')
            
            # 判斷是否為熱門文章
            popular_tag = entry.select_one('div.nrec > span')
            is_popular = popular_tag and popular_tag.text.strip() == '爆'

            # 還沒進入 2024，先用舊邏輯
            if not is_2024_started:
                res_post = requests.get(post_url, headers=HEADERS, timeout=10)
                res_post.raise_for_status()
                post_soup = BeautifulSoup(res_post.text, 'html.parser')
                post_time = extract_meta_value(post_soup, '時間')
                if not post_time:
                    print(f"無法解析時間")
                    continue
                dt = datetime.strptime(post_time, '%a %b %d %H:%M:%S %Y')

                if dt.year < 2024:
                    print('跳過早於 2024 年的文章')
                    continue
                elif dt.year > 2024:
                    print('跳過 2025 年的文章')
                    continue

                # 確認已進入 2024 年
                is_2024_started = True
                mmdd = dt.strftime('%m%d')
            else:
                # 已進入 2024，直接從列表時間推斷
                if post_date >= '01/01':
                    res_post = requests.get(post_url, headers=HEADERS, timeout=10)
                    res_post.raise_for_status()
                    post_soup = BeautifulSoup(res_post.text, 'html.parser')
                    post_time = extract_meta_value(post_soup, '時間')
                    if not post_time:
                        continue
                    dt = datetime.strptime(post_time, '%a %b %d %H:%M:%S %Y')

                    if dt.year == 2025:
                        print("抓到 2025 年文章，結束爬蟲")
                        return
                    elif dt.year != 2024:
                        continue        
                    mmdd = dt.strftime('%m%d')
                else:
                    mmdd = post_date.replace("/", "").zfill(4)

            # 篩選
            if not title_text.strip():
                print(f'略過標題為空白或空字串')
                continue
            if '[公告]' in title_text or 'Fw:[公告]' in title_text:
                print('略過公告文')
                continue
            
            article_data = {
                'date': mmdd,
                'title': title_text,
                'url': post_url
            }
            
            with open('articles.jsonl', 'a', encoding='utf-8') as fa:
                fa.write(json.dumps(article_data, ensure_ascii=False) + '\n')

            if is_popular:
                with open('popular_articles.jsonl', 'a', encoding='utf-8') as fp:
                    fp.write(json.dumps(article_data, ensure_ascii=False) + '\n')
            
            time.sleep(random.uniform(0.1, 0.2)) 

    save_and_quit(articles, popular_articles)


def save_and_quit(articles=None, popular_articles=None):
    total_articles = 0
    total_popular = 0

    if os.path.exists('articles.jsonl'):
        total_articles = sum(1 for _ in open('articles.jsonl', 'r', encoding='utf-8'))

    if os.path.exists('popular_articles.jsonl'):
        total_popular = sum(1 for _ in open('popular_articles.jsonl', 'r', encoding='utf-8'))

    print("-" * 100)
    print(f'爬蟲完成，共收錄 {total_articles} 篇文章，其中 {total_popular} 篇為推爆')

# ----------------------------- PUSH -----------------------------

def Push(start_date: str, end_date: str):
    push_count = Counter()
    boo_count = Counter()
    push_total = 0
    boo_total = 0
    target_articles = []
    
    with open('articles.jsonl', 'r', encoding='utf-8') as f:
        for line in f:
            article = json.loads(line)
            date = article["date"]
            if start_date <= date <= end_date:
                url = article["url"]
                target_articles.append(article)

    print(f"共找到 {len(target_articles)} 篇在 {start_date}~{end_date} 的文章")
    
    for article in target_articles:
        url = article["url"]
        print(f"處理中：{url}")            
        res = requests.get(url, headers=HEADERS, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        pushes = soup.select("div.push")
        for push in pushes:
            tag = push.select_one("span.push-tag")
            userid = push.select_one("span.push-userid")
            if not tag or not userid:
                    continue
            tag_text = tag.text.strip()
            user_id = userid.text.strip()
            
            if tag_text == "推":
                push_count[user_id] += 1
                push_total += 1
            elif tag_text == "噓":
                boo_count[user_id] += 1
                boo_total += 1

        time.sleep(random.uniform(0.1, 0.3))

    def top10(counter):
        return sorted(
            [{"user_id": uid, "count": cnt} for uid, cnt in counter.items()],
            key=lambda x: (x["count"], x["user_id"]),
            reverse=True
        )[:10]
    
    result = {
        "push": {
            "total": push_total,
            "top10": top10(push_count)
        },
        "boo": {
            "total": boo_total,
            "top10": top10(boo_count)
        }
    }
    
    outname = f"push_{start_date}_{end_date}.json"
    with open(outname, "w", encoding="utf-8") as fw:
        json.dump(result, fw, indent=4, ensure_ascii=False)

    print(f"完成 push 分析：{outname}")
    
# ----------------------------- Popular -----------------------------

def extract_image_urls(text):
    pattern = r'https?://[^\s"]+\.(?:jpg|jpeg|png|gif)(?=\b|$)'
    return re.findall(pattern, text, flags=re.IGNORECASE)

def Popular(start_date: str, end_date: str): 
    target_articles = []
    image_urls = []
    
    with open('popular_articles.jsonl', 'r', encoding='utf-8') as f:
        for line in f:
            article = json.loads(line)
            date = article["date"]
            if start_date <= date <= end_date:
                url = article["url"]
                target_articles.append(article)
    
    print(f"共找到 {len(target_articles)} 篇推爆文章在 {start_date}~{end_date}")
    
    for article in target_articles:
        url = article["url"]
        print(f"處理中：{url}")            
        res = requests.get(url, headers=HEADERS, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        
        main_content = soup.get_text() # 內文
        pushes = soup.select("div.push span.push-content") # 留言
        for push in pushes:
                main_content += push.text
        image_urls += extract_image_urls(main_content)
        
        time.sleep(random.uniform(0.1, 0.3))
        
    # unique_image_urls = list(set(image_urls))  #清除重複的url 看題目需不需要
    result = {
        "number_of_popular_articles": len(target_articles),
        "image_urls": image_urls
    }

    outname = f"popular_{start_date}_{end_date}.json"
    with open(outname, "w", encoding="utf-8") as fw:
        json.dump(result, fw, indent=2, ensure_ascii=False)

    print(f"完成 popular 統計：{outname}")
    
    
# ----------------------------- Keyword -----------------------------
  
def Keyword(start_date: str, end_date: str, keyword: str):
    target_articles = []
    image_urls = []
    
    with open('articles.jsonl', 'r', encoding='utf-8') as f:
        for line in f:
            article = json.loads(line)
            if start_date <= article["date"] <= end_date:
                target_articles.append(article)

    print(f"找到 {len(target_articles)} 篇文章在 {start_date}~{end_date}，開始搜尋關鍵字：{keyword}")
    
    for article in target_articles:
        url = article["url"]
        print(f"處理中：{url}")            
        res = requests.get(url, headers=HEADERS, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        
        main_content = soup.select_one("#main-content") # 內文
        if not main_content:
            continue
    
        text = main_content.get_text(separator="\n")
        content_split = text.split("※ 發信站")
        if len(content_split) < 2:
            print("無法找到發信站的標記，跳過這篇文章")
            continue 
        
        content = content_split[0]
        if keyword not in content:
            print(f"沒有找到關鍵字：{keyword}")
            continue  

        print(f"符合條件！")
        
        pushes = soup.select("div.push span.push-content") # 留言
        for push in pushes:
            content += push.text

        image_urls += extract_image_urls(content)

        time.sleep(random.uniform(0.1, 0.3))
        
    # unique_image_urls = list(set(image_urls)) # 去除重複圖片
    result = {
        "image_urls": image_urls
    }

    outname = f"keyword_{start_date}_{end_date}_{keyword}.json"
    with open(outname, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"完成 keyword 統計：{outname}")
       
       
        
if __name__ == "__main__":
    main()