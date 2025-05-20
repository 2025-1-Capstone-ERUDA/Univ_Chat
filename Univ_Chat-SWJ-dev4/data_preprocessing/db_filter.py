import os
import re
import pandas as pd
from date_formatter import DateFormatter
from data_handler import DataHandler

class DataFilterExporter:
    @staticmethod
    def main_filter(df, list_of_university, list_of_department, output_dir="data"):
        """
        주어진 대학교 리스트와 학과 리스트의 모든 조합으로 데이터프레임을 필터링하고
        모든 결과를 하나의 데이터프레임으로 합쳐서 반환합니다.
        결과를 CSV 파일로도 저장합니다.
        
        Parameters:
            df (pd.DataFrame): 전체 데이터프레임
            list_of_university (list): 필터링할 대학교 이름 리스트
            list_of_department (list): 필터링할 학과 이름 리스트
            output_dir (str): CSV를 저장할 디렉토리
            
        Returns:
            pd.DataFrame: 모든 조합의 필터링 결과가 합쳐진 데이터프레임
        """
        # ✅ 중복 제거 먼저 수행
        df = DataFilterExporter.delete_duplication(df)
        
        # 결과를 저장할 리스트
        filtered_dfs = []
        
        # 대학교와 학과의 모든 조합을 순회
        for university in list_of_university:
            for department in list_of_department:
                # 대학교와 학과에 해당하는 데이터프레임 필터링
                filtered_df = DataFilterExporter.filter_dataframe_by_university_and_department(
                    df, university, department, output_dir
                )
                
                # 빈 데이터프레임이 아닌 경우에만 리스트에 추가
                if not filtered_df.empty:
                    filtered_dfs.append(filtered_df)
        
        # 결과가 하나도 없는 경우 빈 데이터프레임 반환
        if not filtered_dfs:
            print(f"⚠️ 선택한 모든 대학교-학과 조합에 해당하는 데이터가 없습니다.")
            return pd.DataFrame()
        
        # 모든 필터링된 데이터프레임을 하나로 합치기
        combined_df = pd.concat(filtered_dfs, ignore_index=True)
        
        # 결합된 결과를 CSV 파일로 저장
        DataFilterExporter.export_filtered_dataframe(
            combined_df, list_of_university, list_of_department, output_dir
        )
        
        return combined_df
        
    def delete_duplication(df):
        """
        articleNo 컬럼을 기준으로 중복된 행을 제거합니다.
        
        Parameters:
            df (pd.DataFrame): 중복 제거 대상 데이터프레임

        Returns:
            pd.DataFrame: 중복이 제거된 데이터프레임
        """
        if 'articleNo' not in df.columns:
            raise ValueError("DataFrame에 'articleNo' 컬럼이 없습니다.")
        
        # 중복 제거 (첫 번째 항목만 유지)
        deduplicated_df = df.drop_duplicates(subset='articleNo', keep='first').reset_index(drop=True)
        
        print(f"✅ 중복 제거 완료: {len(df) - len(deduplicated_df)}개의 중복 행이 삭제되었습니다.")
        return deduplicated_df

    
    
    @staticmethod
    def filter_dataframe_by_university_and_department(df, university, department, output_dir="data"):
        """
        주어진 DataFrame에서 university와 department가 일치하는 행만 필터링합니다.

        Parameters:
            df (pd.DataFrame): 전체 데이터프레임
            university (str): 필터링할 대학교 이름
            department (str): 필터링할 학과 이름
            output_dir (str): 더 이상 사용되지 않음 (호환성을 위해 유지)

        Returns:
            pd.DataFrame: 필터링된 데이터프레임
        """
        # 데이터프레임에 필요한 컬럼이 있는지 확인
        required_cols = {'university', 'department'}
        missing = required_cols - set(df.columns)
        if missing:
            raise ValueError(f"DataFrame에 필요한 컬럼이 없습니다: {missing}")

        # university와 department 컬럼이 일치하는 행만 필터링
        filtered_df = df[
            (df['university'] == university) &
            (df['department'] == department)
        ].reset_index(drop=True)

        return filtered_df

    @staticmethod
    def export_filtered_dataframe(df, university, department, output_dir="data"):
        """
        필터링된 DataFrame을 CSV 파일로 저장합니다.  
        
        Parameters:
            df (pd.DataFrame): 저장할 데이터프레임
            university (str 또는 list): 대학교 이름 (파일명에 사용)
            department (str 또는 list): 학과 이름 (파일명에 사용)
            output_dir (str): 저장 디렉토리
        """
        # 데이터프레임이 비어 있으면 저장하지 않음
        if df.empty:
            if isinstance(university, list) and isinstance(department, list):
                print(f"⚠️ 선택한 대학교와 학과 조합에 해당하는 데이터가 없습니다.")
            else:
                print(f"⚠️ [{university} - {department}]에 해당하는 데이터가 없습니다.")
            return

        # 저장할 디렉토리가 없으면 생성
        os.makedirs(output_dir, exist_ok=True)

        # 파일명 생성
        if isinstance(university, list) and isinstance(department, list):
            # 리스트를 문자열로 변환하여 파일명에 사용
            univ_str = f"[{', '.join(university)}]"
            dept_str = f"[{', '.join(department)}]"
            
            # 파일명에 사용할 수 없는 문자를 안전하게 변환
            safe_univ = re.sub(r'[\\/*?"<>|\.]', '_', univ_str)
            safe_dept = re.sub(r'[\\/*?"<>|\.]', '_', dept_str)
        else:
            # 단일 대학교 및 학과인 경우
            safe_univ = re.sub(r'[\\/*?:"<>|\.\s]', '_', university)
            safe_dept = re.sub(r'[\\/*?:"<>|\.\s]', '_', department)
        
        # 현재 날짜를 파일명에 추가
        date_str = DateFormatter.get_current_date()
        filename = f"{safe_univ},{safe_dept}_{date_str}.csv"
        csv_path = os.path.join(output_dir, filename)

        try:
            # CSV 파일로 저장
            df.to_csv(csv_path, index=False, encoding="utf-8-sig")
            print(f"✅ CSV 저장 완료: {csv_path}")
        except Exception as e:
            print(f"❌ CSV 저장 실패: {e}")


if __name__ == "__main__":
    from load_csv import load_latest_csv_as_dataframe

    data_dir = "data/"
    df = load_latest_csv_as_dataframe(data_dir)

    # 테스트 케이스 1: 단일 대학 & 단일 학과
    print("\n=== 테스트 케이스 1: 단일 대학 & 단일 학과 ===")
    university1 = ["강원대학교"]
    department1 = ["컴퓨터공학"]
    filtered_df1 = DataFilterExporter.main_filter(df, university1, department1, output_dir=data_dir)
    print(f"결과: {filtered_df1.shape[0]}행 x {filtered_df1.shape[1]}열")
    print(filtered_df1.head())

    # 테스트 케이스 2: 단일 대학 & 복수 학과
    print("\n=== 테스트 케이스 2: 단일 대학 & 복수 학과 ===")
    university2 = ["강원대학교"]
    department2 = ["컴퓨터공학", "AI융합학과"]
    filtered_df2 = DataFilterExporter.main_filter(df, university2, department2, output_dir=data_dir)
    print(f"결과: {filtered_df2.shape[0]}행 x {filtered_df2.shape[1]}열")
    print(filtered_df2.head())

    # 테스트 케이스 3: 단일 대학 & 학과 공백
    print("\n=== 테스트 케이스 3: 단일 대학 & 학과 공백 ===")
    university3 = ["강원대학교"]
    department3 = []
    filtered_df3 = DataFilterExporter.main_filter(df, university3, department3, output_dir=data_dir)
    print(f"결과: {filtered_df3.shape[0]}행 x {filtered_df3.shape[1]}열")
    print(filtered_df3.head())

    # 테스트 케이스 4: 복수 대학 & 단일 학과
    print("\n=== 테스트 케이스 4: 복수 대학 & 단일 학과 ===")
    university4 = ["강원대학교", "한림대학교"]
    department4 = ["컴퓨터공학"]
    filtered_df4 = DataFilterExporter.main_filter(df, university4, department4, output_dir=data_dir)
    print(f"결과: {filtered_df4.shape[0]}행 x {filtered_df4.shape[1]}열")
    print(filtered_df4.head())

    # 테스트 케이스 5: 복수 대학 & 복수 학과
    print("\n=== 테스트 케이스 5: 복수 대학 & 복수 학과 ===")
    university5 = ["강원대학교", "한림대학교"]
    department5 = ["컴퓨터공학", "AI융합학과"]
    filtered_df5 = DataFilterExporter.main_filter(df, university5, department5, output_dir=data_dir)
    print(f"결과: {filtered_df5.shape[0]}행 x {filtered_df5.shape[1]}열")
    print(filtered_df5.head())

    # 테스트 케이스 6: 복수 대학 & 학과 공백
    print("\n=== 테스트 케이스 6: 복수 대학 & 학과 공백 ===")
    university6 = ["강원대학교", "한림대학교"]
    department6 = []
    filtered_df6 = DataFilterExporter.main_filter(df, university6, department6, output_dir=data_dir)
    print(f"결과: {filtered_df6.shape[0]}행 x {filtered_df6.shape[1]}열")
    print(filtered_df6.head())

    # 테스트 케이스 7: 대학 공백 & 단일 학과
    print("\n=== 테스트 케이스 7: 대학 공백 & 단일 학과 ===")
    university7 = []
    department7 = ["컴퓨터공학"]
    filtered_df7 = DataFilterExporter.main_filter(df, university7, department7, output_dir=data_dir)
    print(f"결과: {filtered_df7.shape[0]}행 x {filtered_df7.shape[1]}열")
    print(filtered_df7.head())

    # 테스트 케이스 8: 대학 공백 & 복수 학과
    print("\n=== 테스트 케이스 8: 대학 공백 & 복수 학과 ===")
    university8 = []
    department8 = ["컴퓨터공학", "AI융합학과"]
    filtered_df8 = DataFilterExporter.main_filter(df, university8, department8, output_dir=data_dir)
    print(f"결과: {filtered_df8.shape[0]}행 x {filtered_df8.shape[1]}열")
    print(filtered_df8.head())

    # 테스트 케이스 9: 대학 공백 & 학과 공백
    print("\n=== 테스트 케이스 9: 대학 공백 & 학과 공백 ===")
    university9 = []
    department9 = []
    filtered_df9 = DataFilterExporter.main_filter(df, university9, department9, output_dir=data_dir)
    print(f"결과: {filtered_df9.shape[0]}행 x {filtered_df9.shape[1]}열")
    print(filtered_df9.head())