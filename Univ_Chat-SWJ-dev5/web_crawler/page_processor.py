# page_processor.py (페이지 처리)
from bs4 import BeautifulSoup

class PageProcessor:
    def __init__(self, html_content):
        """HTML 콘텐츠를 파싱하여 BeautifulSoup 객체를 생성."""
        self.soup = BeautifulSoup(html_content, "html.parser")
    
    def extract_posts(self, selector: str) -> list:
        """
        주어진 CSS 선택자를 사용하여 게시물 목록을 추출.

        Args:
            selector (str): CSS 선택자 (예: "td.title a")

        Returns:
            list: BeautifulSoup Tag 객체의 리스트
        """
        return self.soup.select(selector)
    
    def has_content(self) -> bool:
        """HTML 문서에 콘텐츠가 존재하는지 여부 반환."""
        return bool(self.soup.find())

# 테스트용 코드
if __name__ == "__main__":
    print("=== PageProcessor 테스트 ===\n")

    # 테스트용 HTML (공지사항 리스트 일부 가상 예시)
    test_html = """
    <html>
        <body>
            <table class="board-table">
                <tbody>
                    <tr>
                        <td class="td-subject"><a href="/notice/1">[공지] 2025 졸업요건 안내</a></td>
                    </tr>
                    <tr>
                        <td class="td-subject"><a href="/notice/2">[공지] 예비군 훈련 일정</a></td>
                    </tr>
                </tbody>
            </table>
        </body>
    </html>
    """

    # PageProcessor 인스턴스 생성
    processor = PageProcessor(test_html)

    # 콘텐츠 존재 여부 확인
    if processor.has_content():
        print("HTML 콘텐츠가 존재합니다.")
    else:
        print("HTML 콘텐츠가 없습니다.")

    # 게시글 추출 테스트
    posts = processor.extract_posts("td.td-subject a")
    if posts:
        print(f"\n총 {len(posts)}개의 게시글을 찾았습니다:")
        for i, post in enumerate(posts, 1):
            print(f"{i}. 제목: {post.get_text(strip=True)} | 링크: {post['href']}")
    else:
        print("게시글을 찾지 못했습니다.")
