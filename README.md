# Crawling
113-2 電機所 生成式AI HW4 Crawling

## Author：國立陽明交通大學 資訊管理與財務金融學系財務金融所碩一 313707043 翁智宏

本次是生成式AI課程的第四次作業，是做爬蟲的練習，爬 PTT Beauty 板 2024 一整年的文章，2024 年的第一篇文章為 [正妹] aespa WINTER，然後再根據爬完的檔案進行三個操作。

[連結](https://www.ptt.cc/bbs/Beauty/M.1704040318.A.E87.html) 

## 任務&目標

### 1. Crawl
   
(1) 功能：

- **爬2024年所有文章。**

- 忽略標題含有 [公告] 和 Fw:[公告] 的文章。

- 忽略缺少標題、標題是空字串的文章。

- 忽略沒有對應網址的文章。

- 列表頁面顯示的文章標題可能會和內文顯示的標題有差異，在這裡以列表頁面的為準。

(2) 輸入格式：

```
$ python {student_id}.py crawl
```

```
$ python　313707043.py crawl
```

(3) 輸出：

- articles.jsonl
  - 包含所有文章。
- popular_articles.jsonl
  - 包含所有推爆的文章。


### 2. Push
   
(1) 功能：

- 找出在{start_date} (含) 跟{end_date}  (含) 之間的以下資訊：
  - 推文和噓文兩種各自的總數。
  - 推文最多次的前 10 名 user_id 。
  - 噓文最多次的前 10 名 user_id 。

(2) 輸入格式：

```
$ python {student_id}.py push {start_date} {end_dat
```
```
$ python 313707043.py push 0304 1231
```

(3) 輸出：

```
        {
            "push": {
                "total": 1040,
                "top10": [
                    {"user_id": "maxxxxxx", "count": 6},
                    {"user_id": "Krishna", "count": 6},
                    {"user_id": "yggyygy", "count": 5},
                    {"user_id": "tyrande", "count": 5},
                    {"user_id": "monarch0301", "count": 5},
                    {"user_id": "johnwu", "count": 5},
                    {"user_id": "cityhunter04", "count": 5},
                    {"user_id": "adamlovedogc", "count": 5},
                    {"user_id": "abellea85209", "count": 5},
                    {"user_id": "Lailungsheng", "count": 5}
                ]
            },
            "boo": {
                "total": 247,
                "top10": [
                    {"user_id": "QVQ9487", "count": 6},
                    {"user_id": "theclgy2001", "count": 4},
                    {"user_id": "cczoz", "count": 4},
                    {"user_id": "zss40401", "count": 3},
                    {"user_id": "cityhunter04", "count": 3},
                    {"user_id": "yushenglu", "count": 2},
                    {"user_id": "un94su3", "count": 2},
                    {"user_id": "srmember", "count": 2},
                    {"user_id": "sion1993", "count": 2},
                    {"user_id": "saw6904", "count": 2}
                ]
            }
```


### 3. Popular
   
(1) 功能：

- 找出在 {start_date} (含) 跟{end_date}  (含) 之間的以下資訊：
  - 推爆的文章數量。
  - 推爆文章中的所有圖片 URL，包括內文和留言中的圖片 URL。
  - 圖片 URL定義：開頭必須是 http:// 或 https:// ，並且要以 .jpg 、.jpeg 、.png 、.gif 為副檔名結尾，副檔名不限大小寫。


(2) 輸入格式：

```
$ python {student_id}.py popular {start_date} {end_date}
```
```
$ python 313707043.py popular 0304 1231
```

(3) 輸出：

```
{
    "number_of_popular_articles": 2,
    "image_urls": [
       "https://i.imgur.com/UDJQEyi.jpg",
       "https://i.imgur.com/jUrvWQM.jpg",
       "https://i.imgur.com/lU5JTIT.jpg",
       "http://i.imgur.com/spn4dNg.jpg",
       ...
 ]
}
```   


### 4. Keyword
   
(1) 功能：

- 找出在 {start_date} (含) 和 {end_date} (含) 之間內文包含 {keyword} 的文章，並統計這些文章的以下資訊：
     - 文章中的所有圖片 URL，包括內文和留言中的圖片 URL。
     - 圖片 URL定義：開頭必須是http://  或 https:// ，並且要以 .jpg、.jpeg 、.png 、.gif 為副檔名結尾，副檔名不限大小寫。
     - 內文範圍說明：.png 、.gif 為副檔名結尾，副檔名不限大小寫。
     - 從「作者」(含)開始到綠色的「※ 發信站」(不含)之間，只要有出現這篇文章包含 {keyword} 。
     - 如果「※ 發信站」不存在，則忽略這篇文章。內文標題和文章列表顯示的標題可能不同，以內文為準。內文出現的網址也在 keyword 匹配範圍內。

(2) 輸入格式：

```
$ python {student_id}.py keyword {start_date} {end_date} {keyword}
```
```
$ python 313707043.py keyword 0304 1231 正妹
```

(3) 輸出：

```
        {
            "image_urls": [
                "https://i.imgur.com/LNFIMk9.jpg",
                "https://i.imgur.com/KpWP9Dm.jpg",
                "http://i.imgur.com/A2LqXBB.jpg",
                ...
            ]
 
```
