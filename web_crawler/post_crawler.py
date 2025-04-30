# web_crawler/post_extractor.py (게시물 추출기)
# 제목, 작성자, 날짜, 본문, 첨부파일 등을 추출

from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
import re
from crawler_utils import CrawlerUtils

class PostExtractor:
    def __init__(self, base_url):
        self.base_url = base_url

    def extract_articleID(self, url: str, site: dict) -> str:
        """URL에서 게시물 번호를 추출합니다. site 정보에서 파라미터 키를 가져올 수 있습니다."""
        
        parsed = urlparse(url)
        query = parse_qs(parsed.query)
        
        article_id_key = site.get("article_ID")
        if article_id_key is None:
            raise ValueError("사이트 설정에 'article_ID' 키가 없습니다.")
        
        article_id = query.get(article_id_key)
        if not article_id:
            raise ValueError(f"게시물 번호를 찾을 수 없습니다: {url}")

        return article_id[0]

    def extract_post_data(self, post_url: str, html_content: str, site: dict) -> dict:
        """HTML 내용과 사이트 설정에서 게시물 상세 정보를 추출합니다."""
        
        try:
            soup = BeautifulSoup(html_content, "html.parser")

            # 제목 추출
            title_selector = site.get("title_path")
            title_tag = soup.select_one(title_selector)
            title = title_tag.get_text(strip=True) if title_tag else None
            # print(f"    📜 제목: {title}")

            # 작성자 추출
            writer_selector = site.get("writer_path")
            writer_tag = soup.select_one(writer_selector)
            author = writer_tag.text.strip() if writer_tag else None
            # print(f"    ✍️ 작성자: {author}")

            # 게시 날짜 추출
            date_selector = site.get("date_path")
            date_tag = soup.select_one(date_selector)
            date = date_tag.text.strip() if date_tag else None
            # print(f"    📅 날짜: {date}")
            
            # 본문 추출
            content_selector = site.get("content_path")
            content_tag = soup.select_one(content_selector)
            if content_tag:
                content = re.sub(r"\s+", " ", content_tag.text.strip())  # 여러 개의 공백을 하나로
                content = content.replace("\u00a0", " ")  # `NBSP` 제거
            else:
                content = "no content"
            # print(f"    📄 내용: {content[:10]}")

            # 첨부파일 추출
            attachment_selector = site.get("attachment_path")
            attachment_tags = soup.select(attachment_selector)
            attachments = [CrawlerUtils.get_full_url(self.base_url, a['href'])
                           for a in attachment_tags if a.has_attr('href')]
            # print(f"    📎 첨부파일: {attachments}")

            # 게시글 번호 추출
            article_id = self.extract_articleID(post_url, site)

            return {
                "title": title,
                "date": date,
                "author": author,
                "article_id": article_id,
                "content": content,
                "link": post_url,
                "attachments": attachments,
                "university": site.get('university'),
                "department": site.get('department'),   
                "category": site.get('category')
            }
        except Exception as e:
            print(f"❌ 게시물 데이터 추출 실패: {post_url} - {str(e)}")
            return None
        
# 테스트용 코드
if __name__ == "__main__":
    # 테스트용 임포트
    from crawler_config import ConfigLoader
    from crawler_utils import CrawlerUtils
    
    print("=== PostExtractor 테스트 ===\n")
    site = ConfigLoader.load_urls()[1]  # 컴퓨터공학과 사이트 정보로 로드(json 파일보고 인덱스 설정 확인)
    url1 = "https://cse.kangwon.ac.kr/cse/community/undergraduate-notice.do?mode=view&articleNo=524640&article.offset=0&articleLimit=10#!/list"
    html1 = CrawlerUtils.make_request(url1)
    post_extractor = PostExtractor("https://cse.kangwon.ac.kr")
    
    # article ID 추출
    article_id = post_extractor.extract_articleID(url1, site)
    print(f"게시물 번호: {article_id}")
    
    # 게시물 데이터 추출
    post_data = post_extractor.extract_post_data(url1, html1, site)
    if post_data:
        print("게시물 데이터:")
        for key, value in post_data.items():
            if key == "content":
                continue    # content는 너무 길어서 생략
            print(f"{key}: {value}")
    else:
        print("게시물 데이터 추출 실패")
        
    print("\n\n")
    
    site = ConfigLoader.load_urls()[0]  # 보건진료소 사이트 정보로 로드(json 파일보고 인덱스 설정 확인)
    url2 = "https://health.kangwon.ac.kr/index.php?mp=4_1&BID=67&cmd=view"
    html2 = CrawlerUtils.make_request(url2)
    post_extractor = PostExtractor("https://health.kangwon.ac.kr")
    
    # article ID 추출
    article_id = post_extractor.extract_articleID(url2, site)
    print(f"게시물 번호: {article_id}")
    
    # 게시물 데이터 추출
    post_data = post_extractor.extract_post_data(url2, html2, site)
    if post_data:
        print("게시물 데이터:")
        for key, value in post_data.items():
            if key == "content":
                continue    # content는 너무 길어서 생략
            print(f"{key}: {value}")
    else:
        print("게시물 데이터 추출 실패")