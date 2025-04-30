# crawler_utils.py (웹 크롤러 관련 기능)
# url 관련 기능들

from urllib.parse import urljoin, urlparse, parse_qs, urlencode
import requests
from bs4 import BeautifulSoup

class CrawlerUtils:
    @staticmethod
    def get_full_url(base_url: str, path: str) -> str:
        """
        주어진 base_url과 path를 결합하여 전체 URL을 생성합니다.
        상대 경로를 절대 경로로 변환합니다.

        Args:
            base_url (str): 기본 URL
            path (str): 상대 경로

        Returns:
            str: 결합된 전체 URL
        """
        return urljoin(base_url, path)

    @staticmethod
    def make_request(url: str, timeout: int = 30) -> str:
        """
        주어진 URL에 GET 요청을 보내고 응답을 반환합니다.
        요청이 실패하면 ConnectionError를 발생시킵니다.

        Args:
            url (str): URL
            timeout (int, optional): 요청 대기 시간(초). 기본값은 30초.

        Raises:
            ConnectionError: 요청 실패 시 발생

        Returns:
            str: 응답 본문(HTML)
        """
        
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            raise ConnectionError(f"Request failed: {e}")
        
    @staticmethod
    def build_paginated_url(base_url: str, site: dict) -> str:
        """
        다음 페이지 URL을 생성.

        Args:
            base_url (str): 기본 URL
            page (int): 페이지 번호
            site (dict): 사이트 설정 정보

        Raises:
            ValueError: 사이트 설정에 'page_id' 또는 'page_offset' 키가 없음
            ValueError: 사이트 설정에 'page_id' 또는 'page_offset' 키가 없음

        Returns:
            str: 생성된 페이지 URL
        """
        # URL 구문 분석
        parsed = urlparse(base_url)
        
        # 쿼리 파라미터 추출 및 수정
        query = parse_qs(parsed.query)
        page_id = site.get("page_id")
        if page_id is None:
            raise ValueError("사이트 설정에 'page_id' 키가 없습니다.")
        page_offset = site.get("page_offset")
        if page_offset is None:
            raise ValueError("사이트 설정에 'page_offset' 키가 없습니다.")
        
        page = int(query.get(page_id, [0])[0])  # 현재 페이지 번호
        query[page_id] = [str(page + page_offset)]
        
        # 새로운 쿼리 문자열 생성
        new_query = urlencode(query, doseq=True)
        
        # 수정된 URL 반환
        return parsed._replace(query=new_query).geturl()
        
# 테스트용 코드
if __name__ == "__main__":
    print("=== CrawlerUtils 테스트 ===\n")

    # 1. get_full_url 테스트
    base_url = "https://cse.kangwon.ac.kr"
    # path = "/cse/community/undergraduate-notice.do?mode=list&&articleLimit=10&article.offset=0"
    path = "/cse/community/undergraduate-notice.do?mode=view&articleNo=524640&article.offset=0&articleLimit=10#!/list"
    full_url = CrawlerUtils.get_full_url(base_url, path)
    print(f"전체 URL: {full_url}")

    # 2. make_request 테스트
    try:
        html = CrawlerUtils.make_request(full_url, timeout=10)
        soup = BeautifulSoup(html, "html.parser")
        title = soup.title.string if soup.title else "제목 없음"
        print(f"페이지 제목: {title}")      # 탭에 표시되는 제목
        print(f"HTML 일부분: {html[:100]}...")  # HTML의 처음 100자만 출력
    except Exception as e:
        print(f"요청 실패: {e}")
        
    # 3. build_paginated_url 테스트
    from crawler_config import ConfigLoader
    site = ConfigLoader.load_urls()[0]
    page_offset = site.get("page_offset")
    base_url = site.get("url")
    for i in range(1, 6):
        base_url = CrawlerUtils.build_paginated_url(base_url, site)
        print(f"다음 페이지 URL: {base_url}")