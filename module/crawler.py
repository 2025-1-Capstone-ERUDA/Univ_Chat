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

visited_posts = set()  # ✅ 3. 중복 게시물 방문 방지

# ✅ 4. 여러 개의 공지사항 URL 처리
for site in url_list:
    url = site["url"]
    crawl_delay = site.get("crawl_delay", 5)

    print(f"\n🔍 {url} 크롤링 중...")

    try:
        response = requests.get(url, timeout=site.get("crawl_timeout", 30))
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        rows = soup.select("tr")  # 게시글이 있는 행 전체 순회

        found_posts = 0

        for row in rows:
            # ✅ 5. 고정 공지 건너뛰기
            is_notice = row.select_one("td.b-num-box.b-notice")
            if is_notice:
                continue

            post_link = row.select_one("td.b-td-left.b-td-title a")
            if not post_link:
                continue

            title = post_link.text.strip()
            link = post_link["href"]

            if not link.startswith("http"):
                link = "https://cse.kangwon.ac.kr/cse/community/" + link.lstrip("/")

            if link in visited_posts:
                print(f"⚠️ 이미 방문한 게시물: {title} (건너뜀)")
                continue

            print(f"📌 제목: {title}, 링크: {link}")
            visited_posts.add(link)
            found_posts += 1

        if found_posts == 0:
            print("⚠️ 게시글을 찾을 수 없습니다. HTML 구조 확인 필요!")
            print(soup.prettify())
        else:
            print(f"✅ 총 {found_posts}개의 게시글을 수집했습니다.")

        time.sleep(crawl_delay)

    except requests.RequestException as e:
        print(f"❌ 요청 실패: {e}")
