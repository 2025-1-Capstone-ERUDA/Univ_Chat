# date_utils.py (날짜 관련 기능)

from datetime import datetime, timedelta

class DateUtils:
    @staticmethod
    def get_current_date(format_str="%Y-%m-%d_%H%M"):
        """유연한 날짜 포맷 제공"""
        return datetime.now().strftime(format_str)

    @staticmethod
    def get_timestamp_filename():
        """CSV 파일명 생성 전문 메서드"""
        return f"posts_{DateUtils.get_current_date()}.csv"
    
    @staticmethod
    def cutoff_date(days_threshold: int = 30) -> datetime:
        """지정한 일수(days_threshold) 이전 날짜를 반환"""
        return datetime.now() - timedelta(days=days_threshold)
    
    @staticmethod
    def str_to_datetime(date_str: str, format_str="%Y-%m-%d_%H%M") -> datetime:
        """문자열을 datetime 객체로 변환"""
        return datetime.strptime(date_str, format_str)
    
# 테스트용 코드
if __name__ == "__main__":
    print("=== DateFormatter 테스트 ===\n")
    
    # 1. get_current_date 테스트
    current_date1 = DateUtils.get_current_date()
    # 현재 날짜를 기본 형식(YYYY-MM-DD_HHMM)으로 출력
    print(f"현재 날짜1: {current_date1}")
    
    current_date2 = DateUtils.get_current_date("%Y-%m-%d")
    # 현재 날짜를 YYYY-MM-DD 형식으로 출력
    print(f"현재 날짜2: {current_date2}")
    
    
    # 2. get_timestamp_filename 테스트
    timestamp_filename = DateUtils.get_timestamp_filename()
    print(f"타임스탬프 파일명: {timestamp_filename}")