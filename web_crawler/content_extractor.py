# content_extractor.py
import re
from datetime import datetime
from bs4 import BeautifulSoup

class ContentExtractor:
    def __init__(self, html_content):
        self.soup = BeautifulSoup(html_content, "html.parser")
    
    def extract_title(self):
        # 제목을 추출하는 로직
        title_tag = self.soup.select_one("#cms-content div:nth-child(1) div:nth-child(1) p span:last-child") 
        return title_tag.text.strip() if title_tag else "제목 없음"

    def extract_date(self):
        # 날짜를 추출하는 로직
        date_tag = self.soup.select_one("div.b-etc-box li.b-date-box")
        if date_tag:
            return re.sub(r"작성일\s*", "", date_tag.text.strip())
        return "날짜 없음"

    def extract_content(self):
        # 본문 내용을 추출하는 로직
        content_tag = self.soup.select_one("div.b-content-box div.fr-view")
        if content_tag:
            content = re.sub(r"\s+", " ", content_tag.text.strip())
            return content.replace("\u00a0", " ")
        return "내용 없음"

    def generate_post_dict(self):
        # 게시물 정보를 딕셔너리 형태로 생성하는 메서드
        return {
            "title": self.extract_title(),
            "date": self.extract_date(),
            "content": self.extract_content(),
            "last_crawled": datetime.utcnow().isoformat() + "Z",
            "status": "active",
            "crawl_frequency": "daily",
            "crawl_timeout": 30,
            "crawl_delay": 5
        }
