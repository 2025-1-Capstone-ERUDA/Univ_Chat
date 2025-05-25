import pandas as pd
import re
import os
from bs4 import BeautifulSoup
from datetime import datetime
import csv

import db_preprocessor
from file_utils import FileUtils
from date_utils import DateUtils

def preprocess_and_save(file_path: str = None) -> str:
    """
    csv 파일 경로를 받아(만약 주어지지 않을 경우 가장 최근의 csv 파일 찾아와서 수행)
    해당 csv 파일에 대해 전처리 수행후 저장(preprocess_data 디렉토리)및 경로 반환하는 함수
    """
    df_init = pd.DataFrame()

    if file_path is None:
        file_path = os.path.abspath(__file__)
        output_dir = os.path.join(os.path.dirname(file_path), "..", "data")
        df_init = FileUtils.load_latest_csv_as_dataframe(output_dir)
    else:
        df_init = pd.read_csv(file_path, encoding="utf-8-sig")

    #-------------기존 코드 재활용 부분------------
    if 'content' not in df_init.columns:
        raise ValueError("입력 데이터프레임에 'content' 컬럼이 없습니다.")

    df = df_init.copy()
    df['content'] = df['content'].apply(db_preprocessor.clean_text_advanced) # 함수 호출 형식 수정

    # 상위 디렉토리 기준으로 경로 설정
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(base_dir, "preprocess_data") # 이름 수정
    os.makedirs(output_dir, exist_ok=True)

    date_str = datetime.today().strftime("%Y%m%d")
    output_path = os.path.join(output_dir, f"preprocess_{date_str}.csv") # 이름 수정

    df.to_csv(output_path, index=False, encoding='utf-8-sig', quoting=csv.QUOTE_ALL)
    print(f"[\u2714] 전처리 완료 \u2192 저장: {output_path} (총 {len(df)}건)")
    #-------------기존 코드 재활용 부분------------

    return output_path

# === 메인 실행 ===
if __name__ == "__main__":
    preprocess_and_save()