# crawler_config.py (설정 관리)
# 수집할 사이트 정보가 담긴 파일을 읽어 URL 목록을 로드
# load_urls: JSON 파일에서 URL 목록을 로드

import os
import json
from urllib.parse import urlparse, parse_qs

class ConfigLoader:
    @staticmethod
    def load_urls(file_path: str = None) -> list:
        """
        JSON 파일에서 URL 목록을 로드합니다.

        Args:
            file_path (str): JSON 파일 경로(입력 없을 시 기본값은 None으로 하여 /information/crawler_url.json 을 사사용)

        Raises:
            ValueError: JSON 파일에 'url' 또는 'urls' 키가 없음

        Returns:
            list: URL 정보 목록
        """
        
        # 기본 경로 설정
        if file_path is None:
            current_dir = os.path.dirname(__file__)
            file_path = os.path.join(os.path.dirname(current_dir), "infomation", "crawler_url.json")

        # JSON 파일 읽기
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"파일이 존재하지 않습니다: {file_path}")
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
        
        if ("urls" in data) :
            return data["urls"]
        elif ("url" in data):
            return [data["url"]]
        
        raise ValueError("JSON 파일에 'url' 또는 'urls' 키가 없습니다")

# 테스트 코드
if __name__ == "__main__":
    print("=== ConfigLoader 테스트 ===\n")
    
    try:
        urls = ConfigLoader.load_urls()
        print("URL 목록:")
        for item in urls:
            print("- ", item)
    except Exception as e:
        print("오류 발생:", e)
