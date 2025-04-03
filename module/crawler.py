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
for url in url_list:
    crawl_delay = data.get("crawl_delay", 5)  # 크롤링 간격 기본값 5초

    print(f"🔍 {url} 크롤링 중...")

    try:
        response = requests.get(url, timeout=data.get("crawl_timeout", 30))
        response.raise_for_status()  # 요청 오류 발생 시 예외 처리

        soup = BeautifulSoup(response.text, "html.parser")

        # ✅ 4. 게시글 목록 크롤링 (제목 & 링크)
        posts = soup.select("table.board-table td.title a")  

        if not posts:
            print(f"⚠️ 게시글을 찾을 수 없습니다. HTML 구조 확인 필요!")
            print(soup.prettify())  # 🔥 페이지 전체 HTML 출력해서 구조 확인
            continue

        for post in posts:
            title = post.text.strip()  # 게시글 제목
            link = post["href"]  # 상대 URL

            # ✅ 5. 링크가 상대경로라면 절대경로로 변환
            if not link.startswith("http"):  
                link = "https://cse.kangwon.ac.kr/cse/community/" + link

            # ✅ 6. 중복 게시물 방문 방지
            if link in visited_posts:
                print(f"⚠️ 이미 방문한 게시물: {title} (건너뜀)")
                continue

            print(f"📌 제목: {title}, 링크: {link}")
            visited_posts.add(link)  # 방문한 게시물 기록

        time.sleep(crawl_delay)  # 크롤링 간격 조절
    
    except requests.RequestException as e:
        print(f"❌ 요청 실패: {e}")
