# web_crawler/file_manager.py (파일 및 디렉토리 관련 기능)

import os
import csv
import pandas as pd
import re
from date_utils import DateUtils

class FileUtils:
    @staticmethod
    def _ensure_directory(dir_path: str) -> None:
        """디렉토리 존재 여부 확인 및 생성"""
        os.makedirs(dir_path, exist_ok=True)
        
    @staticmethod
    def _ensure_file_existing(file_path: str) -> None:
        """파일 존재 여부 확인"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"파일이 존재하지 않습니다: {file_path}")
        
    @staticmethod
    def delete_old_csv_files(dir_path: str = None, days_threshold: int = 30) -> None:
        """
        지정한 디렉토리에서 days_threshold일 이상 지난 CSV 파일을 삭제하는 함수
        파일명은 'posts_'로 시작하고 '.csv'로 끝나는 파일만 삭제됨

        Args:
            dir_path (str, optional): 디렉토리 경로. 기본값은 None.
            days_threshold (int, optional): 삭제 기준일. 기본값은 30일.
        """
        if dir_path is None:
            file_path = os.path.abspath(__file__)
            dir_path = os.path.join(os.path.dirname(file_path), "..", "data")
        FileUtils._ensure_directory(dir_path)

        # cutoff 이전 날짜에 만들어진 파일 삭제 cutoff에 만든 파일은 생존
        cutoff = DateUtils.cutoff_date(days_threshold)

        for filename in os.listdir(dir_path):
            if filename.startswith("posts_") and filename.endswith(".csv"):
                try:
                    # 날짜 문자열만 추출 (posts_ 이후 ~ .csv 이전까지)
                    date_str = filename[len("posts_"):-len(".csv")]
                    file_datetime = DateUtils.str_to_datetime(date_str, "%Y-%m-%d_%H%M")

                    # 파일 날짜가 cutoff 이전이면 삭제
                    if file_datetime < cutoff:
                        file_path = os.path.join(dir_path, filename)
                        os.remove(file_path)
                        print(f"삭제됨: {file_path}")
                except ValueError:
                    print(f"[무시됨] 날짜 파싱 실패: {filename}")
                    
    @staticmethod
    def load_latest_csv_as_dataframe(output_dir: str = None) -> pd.DataFrame:
        """
        주어진 디렉토리에서 가장 최근 수정된 CSV 파일을 읽어 DataFrame으로 반환.

        Args:
            output_dir (str, optional): CSV 파일이 저장된 디렉토리 경로. 기본값은 None.

        Returns:
            pd.DataFrame: 가장 최근 수정된 CSV 파일의 데이터프레임
        """
        
        if output_dir is None:
            file_path = os.path.abspath(__file__)
            output_dir = os.path.join(os.path.dirname(file_path), "..", "data")
        FileUtils._ensure_directory(output_dir)
        
        csv_files = [f for f in os.listdir(output_dir) if f.endswith('.csv')]
        
        # CSV 파일이 없으면 빈 DataFrame 반환
        if not csv_files:
            return pd.DataFrame()

        # CSV 파일 목록을 수정 시간 기준으로 정렬 (최신 파일이 첫 번째)
        csv_files.sort(key=lambda f: os.path.getmtime(os.path.join(output_dir, f)), reverse=True)
        latest_csv_path = os.path.join(output_dir, csv_files[0])
        
        # CSV 파일 로드
        try:
            print(f"최신 CSV 파일 로드 중: {latest_csv_path}")
            return pd.read_csv(latest_csv_path, encoding="utf-8-sig")
        except Exception as e:
            print(f"[경고] CSV 파일 로드 실패: {e}")
            return pd.DataFrame()

    @staticmethod
    def load_latest_csv_as_dataframe2(output_dir: str = None) -> pd.DataFrame:
        """
        파일명에 포함된 날짜/시간을 기준으로 가장 최근 CSV 파일을 DataFrame으로 반환.
        파일명 형식: posts_YYYY-MM-DD_HHMM.csv

        Args:
            output_dir (str, optional): CSV 파일이 저장된 디렉토리 경로. 기본값은 ../data

        Returns:
            pd.DataFrame: 가장 최근 날짜의 CSV 파일의 데이터프레임
        """
        
        if output_dir is None:
            file_path = os.path.abspath(__file__)
            output_dir = os.path.join(os.path.dirname(file_path), "..", "data")
        FileUtils._ensure_directory(output_dir)

        csv_files = [f for f in os.listdir(output_dir) if f.endswith('.csv')]

        if not csv_files:
            return pd.DataFrame()

        # 파일명에서 날짜/시간 추출 후 datetime 객체로 변환
        pattern = r"posts_(\d{4}-\d{2}-\d{2})_(\d{4})\.csv"
        dated_files = []
        for filename in csv_files:
            match = re.match(pattern, filename)
            if match:
                date_str, time_str = match.groups()
                try:
                    dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H%M")
                    dated_files.append((dt, filename))
                except ValueError:
                    continue  # 날짜 형식이 잘못된 경우 무시

        if not dated_files:
            return pd.DataFrame()

        # 가장 최신 날짜의 파일 선택
        latest_file = max(dated_files, key=lambda x: x[0])[1]
        latest_csv_path = os.path.join(output_dir, latest_file)

        try:
            print(f"최신 CSV 파일 로드 중: {latest_csv_path}")
            return pd.read_csv(latest_csv_path, encoding="utf-8-sig")
        except Exception as e:
            print(f"[경고] CSV 파일 로드 실패: {e}")
            return pd.DataFrame()
        
        
        
    @staticmethod
    def merge_dataframes(df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
        """
        두 개의 DataFrame을 병합.

        Args:
            df1 (pd.DataFrame): 첫 번째 DataFrame
            df2 (pd.DataFrame): 두 번째 DataFrame

        Returns:
            pd.DataFrame: 병합된 DataFrame
        """
        return pd.concat([df1, df2], ignore_index=True)
    
    @staticmethod
    def save_dataframe_to_csv(df: pd.DataFrame, file_path: str = None) -> None:
        """
        DataFrame을 CSV 파일로 저장.

        Args:
            df (pd.DataFrame): 저장할 DataFrame
            file_path (str): 저장할 CSV 파일 경로
        """
        if file_path is None:
            file_path = os.path.abspath(__file__)
            file_path = os.path.join(os.path.dirname(file_path), "..", "data", DateUtils.get_timestamp_filename())

        try:
            df.to_csv(file_path, index=False, encoding="utf-8-sig")
            print(f"CSV 파일 저장 완료: {file_path}")
        except Exception as e:
            print(f"CSV 파일 저장 실패: {e}")

if __name__ == "__main__":
    # 테스트용 라이브러리
    from datetime import datetime, timedelta
    
    # 테스트를 위한 임시 디렉토리 생성 및 파일 생성
    test_dir = os.path.join(os.path.dirname(__file__), "..", "test_data")
    os.makedirs(test_dir, exist_ok=True)

    now = datetime.now()
    yesterday = now - timedelta(days=1)
    two_days_ago = now - timedelta(days=2)

    # CSV 파일 생성 (날짜 포함)
    with open(os.path.join(test_dir, f"posts_{two_days_ago.strftime('%Y-%m-%d_%H%M')}.csv"), "w", encoding="utf-8-sig") as f:
        f.write("col1,col2\n1,A\n2,B\n")
    with open(os.path.join(test_dir, f"other_file.txt"), "w", encoding="utf-8-sig") as f:
        f.write("not a csv")
    with open(os.path.join(test_dir, f"posts_{yesterday.strftime('%Y-%m-%d_%H%M')}.csv"), "w", encoding="utf-8-sig") as f:
        f.write("col1,col2\n3,C\n4,D\n")
        
    # 디렉토리 존재 여부 확인 및 생성
    FileUtils._ensure_directory(test_dir)
    # 파일 존재 여부 확인
    try:
        FileUtils._ensure_file_existing(os.path.join(test_dir, f"posts_{yesterday.strftime('%Y-%m-%d_%H%M')}.csv"))
        print("파일 존재 확인 성공")
    except FileNotFoundError as e:
        print(e)
        
    # CSV 파일 로드 테스트
    print("=== CSV 파일 로드 테스트 (load_latest_csv_as_dataframe) ===")
    test_df = FileUtils.load_latest_csv_as_dataframe(test_dir)
    if not test_df.empty:
        print("최신 CSV 파일 내용:")
        print(test_df.head())
    else:
        print("CSV 파일이 없거나 로드에 실패했습니다.")

    # 날짜 기반 CSV 파일 로드 테스트
    print("=== 날짜 기반 CSV 파일 로드 테스트 (load_latest_csv_as_dataframe2) ===")
    test_df2 = FileUtils.load_latest_csv_as_dataframe2(test_dir)
    if not test_df2.empty:
        print("날짜 기반 최신 CSV 파일 내용:")
        print(test_df2.head())
    else:
        print("CSV 파일이 없거나 날짜 기반 로드에 실패했습니다.")
        
    # 오래된 CSV 파일 삭제 테스트
    print("=== 오래된 CSV 파일 삭제 테스트 ===")
    print("삭제 전 파일 목록:", os.listdir(test_dir))
    FileUtils.delete_old_csv_files(test_dir, days_threshold=1)
    print("삭제 후 파일 목록:", os.listdir(test_dir))

    # 테스트 디렉토리 삭제
    import shutil
    shutil.rmtree(test_dir)
