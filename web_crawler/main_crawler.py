# main_crawler.py (실행 로직)
import os
import time
from datetime import datetime

from crawler_config import ConfigLoader
from crawler_utils import CrawlerUtils
from page_processor import PageProcessor
from url_builder import URLBuilder
from content_extractor import ContentExtractor
from data_handler import DataHandler
from date_formatter import DateFormatter

class NoticeCrawler:
    def __init__(self, config_path):
        self.url_list = ConfigLoader.load_urls(config_path)
        self.visited_posts = set()
        self.collected_data = []
    
    def process_site(self, site):
        base_url = site["url"]
        board_path = site["board_path"]
        crawl_delay = site.get("crawl_delay", 5)
        timeout = site.get("crawl_timeout", 30)
        page = 0
        
        print(f"\n🔍 {base_url} 크롤링 시작...")
        
        while True:
            # 디버깅용 => 현재 중복 게시물 처리가 안되어있어서 무한 반복되기에 0,1,2페이지까지만 크롤링
            if (page > 2):
                break
            
            current_url = URLBuilder.build_paginated_url(base_url, page)
            print(f"   🔄 [{page}페이지] 요청 중...")
            
            try:
                html_content = CrawlerUtils.make_request(current_url, timeout)
                processor = PageProcessor(html_content)
                
                if not processor.has_content():
                    print(f"⚠️ [{page}페이지] 컨텐츠 없음")
                    break
                
                posts = processor.extract_posts(board_path)
                self._process_posts(posts, base_url)
                
                if not posts:
                    print(f"⛔ 페이지 {page}에서 중단")
                    break
                
                page += 1
                time.sleep(crawl_delay)
            
            except Exception as e:
                print(f"❌ 에러 발생: {e}")
                break
    
    def _process_posts(self, posts, base_url):
        new_post_found = False
        for post in posts:
            title = "".join(post.stripped_strings)
            href = post.get("href")
            full_url = CrawlerUtils.get_full_url(base_url, href)
            
            if full_url in self.visited_posts:
                print(f"⚠️ 중복 게시물: {title}")
                continue
                
            print(f"📌 새 게시물 처리 시작: {title}")
            self._process_individual_post(full_url)
            self.visited_posts.add(full_url)
            new_post_found = True
        
        if not new_post_found:
            print("⚠️ 새로운 게시물 없음")

    def _process_individual_post(self, post_url):
        try:
            # 게시물 상세 페이지 요청
            html_content = CrawlerUtils.make_request(post_url)
            extractor = ContentExtractor(html_content)
            
            # 데이터 추출 및 저장
            post_data = extractor.generate_post_dict()
            self.collected_data.append(post_data)
            print(f"   📄 게시물 데이터: {post_data}")
            
            print(f"✅ 게시물 저장 완료: {post_data['title']}")
        except Exception as e:
            print(f"❌ 게시물 처리 실패: {post_url} - {str(e)}")

    def run(self):        
        for site in self.url_list:
            self.process_site(site)
        print(f"\n✅ 총 {len(self.visited_posts)}개 수집 완료")
        
        csv_filename = DateFormatter.get_timestamp_filename()
        DataHandler.export_to_csv(
            self.collected_data,
            output_dir=os.path.join(os.path.dirname(__file__), "..", "data"),
            filename=csv_filename
        )

# 실행 예시
if __name__ == "__main__":
    crawler = NoticeCrawler("infomation/crawler_url.json")
    crawler.run()
