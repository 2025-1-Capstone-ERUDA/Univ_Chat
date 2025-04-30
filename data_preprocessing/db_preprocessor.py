import pandas as pd
import re
import os
from bs4 import BeautifulSoup
from datetime import datetime
import csv

# [최종 수정 확인용] 2025-04-28

# === 전처리 세부 함수 정의 ===

#HTML 태그 제거
def remove_html_tags(text: str) -> str:
    return BeautifulSoup(text, "html.parser").get_text()

# 유니코드 특수문자 제거 (글머리 기호는 남김)
def remove_unicode_specials(text: str) -> str:
    # 글머리 기호(•, ‣ 등 U+2022~U+2027)는 남기고
    # 나머지 특수문자, 도형을 제거
    pattern = (
        r'['
        r'\u2000-\u2021'   # 다양한 일반 구두점 문자
        r'\u2028-\u206F'   # 추가 구두점 문자
        r'\u2E00-\u2E7F'   # 보충 구두점 문자
        r'\u2100-\u214F'   # 문자 형태 기호
        r'\u2200-\u22FF'   # 수학 기호
        r'\u2300-\u23FF'   # 다양한 기술용 기호
        r'\u2400-\u243F'   # 제어 문자 그림
        r'\u25A0-\u25FF'   # 도형 기호 (○, ▶ 등 도형)
        r'\uF000-\uFFFF'   # 사설 영역 문자 (󰋻 등)
        r']'
    )
    return re.sub(pattern, '', text)

#의미 없는 이모지 제거
def remove_unnecessary_emojis(text: str) -> str:
    emoji_pattern = re.compile("[" 
        u"\U0001F300-\U0001F5FF"  # 자연, 장소, 사물
        u"\U0001F600-\U0001F64F"  # 얼굴 감정
        u"\U0001F680-\U0001F6FF"  # 교통 수단
        u"\U0001F700-\U0001F77F"  # 연금술 기호
        u"\U0001F780-\U0001F7FF"  # 기하학 확장
        u"\U0001F800-\U0001F8FF"  # 화살표 확장
        u"\U0001F900-\U0001F9FF"  # 추가 이모지
        u"\U0001FA00-\U0001FA6F"  # 체스말, 보드게임 기호
        u"\U0001FA70-\U0001FAFF"  # 추가 픽토그램
        u"\u2600-\u26FF"          # Miscellaneous Symbols (☀, ☎, ☕)
        u"\u2700-\u27BF"          # Dingbats (✓, ✗)
    "]+", flags=re.UNICODE)
    return emoji_pattern.sub('', text)

#URL 링크 대체 (현재 미사용)
def replace_urls(text: str) -> str:
    return re.sub(r'(https?://[^\s\)\]\}\>,]+|www\.[^\s\)\]\}\>,]+)', ' [링크] ', text)

#과도한 공백 정리
def normalize_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()

# === 메인 전처리 함수 ===
def clean_text_advanced(text: str) -> str:
    if not isinstance(text, str) or not text.strip():
        return "[본문 없음]"

    text = remove_html_tags(text)
    text = remove_unicode_specials(text)
    text = remove_unnecessary_emojis(text)
    # text = replace_urls(text)
    text = normalize_spaces(text)

    if not text.strip():
        return "[본문 없음]"
    return text

# === CSV 처리 함수 ===
def preprocess_and_save(df: pd.DataFrame) -> pd.DataFrame:
    """
    content 컬럼의 텍스트를 전처리하여 /processing 디렉토리에 저장하고
    전처리된 DataFrame을 반환하는 함수
    """
    if 'content' not in df.columns:
        raise ValueError("입력 데이터프레임에 'content' 컬럼이 없습니다.")

    df = df.copy()
    df['content'] = df['content'].apply(clean_text_advanced)

    # 상위 디렉토리 기준으로 경로 설정
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(base_dir, "processing")
    os.makedirs(output_dir, exist_ok=True)

    date_str = datetime.today().strftime("%Y%m%d")
    output_path = os.path.join(output_dir, f"processing_{date_str}.csv")

    df.to_csv(output_path, index=False, encoding='utf-8-sig', quoting=csv.QUOTE_ALL)
    print(f"[\u2714] 전처리 완료 \u2192 저장: {output_path} (총 {len(df)}건)")

    return df

# === 메인 실행 ===
if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # 처리할 파일 경로 지정
    input_filename = "posts_2025-04-14_0629.csv"
    input_path = os.path.join(base_dir, "data", input_filename)

    # CSV 읽고 전처리
    df = pd.read_csv(input_path)
    preprocess_and_save(df)