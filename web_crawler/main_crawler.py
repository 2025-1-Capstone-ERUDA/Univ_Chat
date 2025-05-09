# main_crawler.py (실행 로직)
# 크롤러 프로그램

import os
import time
import pandas as pd

from crawler_config import ConfigLoader
from crawler_utils import CrawlerUtils
from page_processor import PageProcessor
from date_utils import DateUtils
from post_crawler import PostExtractor
from file_utils import FileUtils

class NoticeCrawler:
    def __init__(self, config_path: str = None, csv_save_directory: str = None):
        self.url_list = ConfigLoader.load_urls(config_path)     # URL 목록 로드
        self.collected_data = []                                # 수집된 데이터 저장 리스트
        self.csv_save_directory = csv_save_directory            # CSV 저장 디렉토리 설정
        self.existing_df = self._load_existing_dataframe()      # 기존 데이터프레임 로드

    def _load_existing_dataframe(self):
        """기존의 최신 CSV 파일을 로드하거나, 파일이 없으면 빈 DataFrame을 반환합니다."""
        
        output_dir = self.csv_save_directory
        try:
            return FileUtils.load_latest_csv_as_dataframe(output_dir)
        except FileNotFoundError:
            print("⚠️ 기존 CSV 파일을 찾을 수 없습니다. 새로운 DataFrame으로 시작합니다.")
            return pd.DataFrame()
        except Exception as e:
            print(f"⚠️ 기존 CSV 파일 로드 실패: {e}")
            return pd.DataFrame()

    def process_site(self, site):
        """crawler_url.json에 정의된 각 사이트를 순회하며 게시물을 처리합니다."""
           
        current_url = site.get("url", "")
        post_extractor = PostExtractor(current_url)   
        board_path = site.get("board_path", "")
        crawl_delay = site.get("crawl_delay", 5)
        timeout = site.get("crawl_timeout", 30)
        page = 1

        print(f"\n🔍 {current_url} 크롤링 시작...")

        while True:
            try:
                print(f"    🔄 [{page}페이지({current_url})] 요청 중...")
                html_content = CrawlerUtils.make_request(current_url, timeout)
                processor = PageProcessor(html_content)

                if not processor.has_content():
                    print(f"⚠️ [{page}페이지] 컨텐츠 없음")
                    break

                posts = processor.extract_posts(board_path)
                print(f"    📄 [{page}페이지] 게시물 수: {len(posts)}")
                newly_collected = self._process_posts(post_extractor, posts, current_url, site)
                print(f"    📥 [{page}페이지] 수집된 게시물 수: {len(newly_collected) if newly_collected else 0}")

                if not newly_collected:
                    print(f"⛔ 페이지 {page}에서 새로운 게시물 없음. 해당 URL 크롤링 완료.")
                    break

                self.collected_data.extend(newly_collected)
                page += 1
                time.sleep(crawl_delay)

            except Exception as e:
                print(f"❌ 에러 발생: {e}")
                break
            
            # 다음 페이지 URL 생성
            current_url = CrawlerUtils.build_paginated_url(current_url, site)


    def _process_posts(self, post_extractor, posts, base_url, site):
        """게시물 목록에서 각 게시물의 링크를 따라가 상세 정보를 추출하고 중복을 확인합니다."""
        
        newly_collected_posts = []
        new_post_found = False
        duplicate_check_key = site.get("duplicate_check_key")
        if not duplicate_check_key:
            print("⚠️ 중복 확인 키가 설정되지 않았습니다.")
            return None

        # collected_data 중복 확인을 위한 set (튜플 형태로 저장하여 해싱 가능하게 함)
        collected_data_keys = set([(item.get(duplicate_check_key), item.get("university"), item.get("department"), item.get("category"))
                                     for item in self.collected_data if item.get(duplicate_check_key)])

        # existing_df 중복 확인을 위한 set (튜플 형태로 저장)
        existing_df_keys = set()
        if not self.existing_df.empty and duplicate_check_key in self.existing_df.columns and \
           "university" in self.existing_df.columns and "department" in self.existing_df.columns:
            existing_df_keys = set(zip(self.existing_df[duplicate_check_key].astype(str),
                                       self.existing_df["university"].astype(str),
                                       self.existing_df["department"].astype(str),
                                       self.existing_df["category"].astype(str)))

        for post_element in posts:
            title = "".join(post_element.stripped_strings).strip()
            href = post_element.get("href")

            full_url = CrawlerUtils.get_full_url(base_url, href)

            post_data = self._crawl_and_extract_post(post_extractor, full_url, site)
            if post_data:
                duplicate_key = post_data.get(duplicate_check_key)
                post_university = post_data.get("university")
                post_department = post_data.get("department")
                post_category = post_data.get("category")

                if duplicate_key:
                    # collected_data 중복 확인
                    current_key = (duplicate_key, post_university, post_department, post_category)
                    if current_key in collected_data_keys:
                        # print(f"⚠️ 이번 수집 데이터 중 중복 게시물 발견 ({duplicate_check_key}={duplicate_key}): {title}")
                        continue

                    # existing_df 중복 확인
                    if (str(duplicate_key), str(post_university), str(post_department), str(post_category)) in existing_df_keys:
                        # print(f"⚠️ 기존 데이터 중 중복 게시물 발견 ({duplicate_check_key}={duplicate_key}): {title}")
                        continue

                    newly_collected_posts.append(post_data)
                    collected_data_keys.add(current_key) # 새로 수집된 데이터의 키 추가
                    new_post_found = True
                    # print(f"📌 새 게시물 수집 완료: {title} ({full_url})")

        if new_post_found:
            return newly_collected_posts
        else:
            return None

    def _crawl_and_extract_post(self, post_extractor, post_url, site):
        """주어진 URL의 게시물 상세 정보를 크롤링하고 추출합니다."""
        
        try:
            response = CrawlerUtils.make_request(post_url)
            post = post_extractor.extract_post_data(post_url, response, site)
            return post
        except Exception as e:
            print(f"❌ 게시물 처리 실패: {post_url} - {str(e)}")
            return None

    def run(self):
        """크롤러를 실행하고 결과를 CSV 파일로 저장합니다."""
        
        for site in self.url_list:
            self.process_site(site)

        all_collected_df = pd.DataFrame(self.collected_data)

        if not all_collected_df.empty:
            # 기존 데이터프레임과 새로 수집된 데이터를 병합
            final_df = FileUtils.merge_dataframes(self.existing_df, all_collected_df)
        else:
            # 수집된 데이터가 없으면 기존 데이터프레임 유지
            final_df = self.existing_df

        FileUtils.save_dataframe_to_csv(final_df, self.csv_save_directory)
        print(f"\n✅ 크롤링 완료. {len(self.collected_data)}개의 게시물 수집됨.")

        # 오래된 CSV 파일 삭제 (현재는 개발단계이기에 작동하지 않음)
        # FileUtils.delete_old_csv_files(output_dir, days_threshold=7)

if __name__ == "__main__":
    crawler = NoticeCrawler()
    crawler.run()