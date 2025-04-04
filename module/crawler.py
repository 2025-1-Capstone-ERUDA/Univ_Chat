import json
import requests
from bs4 import BeautifulSoup
import time

# ✅ 1. JSON 파일에서 URL 읽기
with open("data/crawler_url.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# ✅ 2. "urls" 또는 "url" 키 확인
if "urls" in data:
    url_list = data["urls"]
elif "url" in data:
    url_list = [data["url"]]
else:
    print("⚠️ 오류: 'url' 또는 'urls' 키가 JSON 파일에 없습니다.")
    url_list = []

visited_posts = set()  # ✅ 5. 중복 게시물 방문 방지

# ✅ 3. 여러 개의 공지사항 URL 처리
for site in url_list:
    url = site["url"]
    crawl_delay = site.get("crawl_delay", 5)  # site에서 꺼내야 해!

    print(f"🔍 {url} 크롤링 중...")

    try:
        response = requests.get(url, timeout=site.get("crawl_timeout", 30))  # site에서 timeout도 꺼내고
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        posts = soup.select("table.board-table td.title a")  

        if not posts:
            print(f"⚠️ 게시글을 찾을 수 없습니다. HTML 구조 확인 필요!")
            print(soup.prettify())
            continue

        for post in posts:
            title = post.text.strip()
            link = post["href"]

            if not link.startswith("http"):
                link = "https://cse.kangwon.ac.kr/cse/community/" + link

            if link in visited_posts:
                print(f"⚠️ 이미 방문한 게시물: {title} (건너뜀)")
                continue

            print(f"📌 제목: {title}, 링크: {link}")
            visited_posts.add(link)

        time.sleep(crawl_delay)

    except requests.RequestException as e:
        print(f"❌ 요청 실패: {e}")
