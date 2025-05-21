# doc_utils.py (첨부파일 처리 및 텍스트 추출 관련 기능)
# 첨부파일을 다운로드하고 텍스트를 추출하는 기능

# 적절하게 import 문 추가
import os
import re
import olefile
import zipfile
import xml.etree.ElementTree as ET
from PIL import Image
import easyocr
import numpy as np
import requests
import fitz  # PyMuPDF
from docx import Document
from urllib.parse import unquote

# 라이브러리 설치 후 requirements.txt에 추가 필수
from file_utils import FileUtils

class AttachmentProcessor:
    def __init__(self, download_dir: str = None):
        if download_dir is None:
            current_dir = os.path.dirname(__file__)
            download_dir = os.path.join(os.path.dirname(current_dir), "tmp")
        self.download_dir = download_dir
        FileUtils._ensure_directory(self.download_dir)
    
    def remove_control_chars(self, text: str) -> str:
        # 텍스트 내 SOH 포함 모든 제어문자 제거 (줄바꿈, 탭은 유지) 
        return ''.join(c for c in text if ord(c) >= 32 or c in '\n\t')

    def download_file(self, url):
        def decode_filename(filename_raw):
            def fully_unquote(encoded_str):
                prev = None
                decoded = encoded_str
                # 반복해서 unquote 하면서 더 이상 변하지 않을 때까지 수행
                while prev != decoded:
                    prev = decoded
                    decoded = unquote(decoded)
                return decoded
            
            #-------------fully_unquote 끝-----------------

            # 우선 완전 디코딩 시도
            filename = fully_unquote(filename_raw)

            # 인코딩 변환 시도
            try:
                filename = filename.encode('latin1').decode('utf-8')
                return filename
            except Exception:
                pass

            try:
                filename = filename.encode('latin1').decode('cp949')
                return filename
            except Exception:
                pass

            return filename
        #---------------------decode_filename 끝----------------------------
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        try:
            response = requests.get(url, verify=False)
            cd = response.headers.get('Content-Disposition', '')

            # filename* 가 있는지 확인 (RFC 5987 스타일 인코딩)
            filename_match_star = re.search(r"filename\*\s*=\s*([^;]+)", cd)
            # filename= 만 있는 경우
            filename_match = re.search(r'filename\s*=\s*["\']?([^"\';]+)', cd)

            if filename_match_star:
                # filename*=UTF-8''인 경우
                raw_name = filename_match_star.group(1)
                # 예: UTF-8''%ED%95%9C%EA%B8%80.jpg 이런 형식일 수 있음
                if raw_name.lower().startswith("utf-8''"):
                    raw_name = raw_name[7:]  # 'UTF-8'' 제거
                filename = unquote(raw_name)
            elif filename_match:
                raw_name = filename_match.group(1)
                filename = decode_filename(raw_name)
            else:
                # Content-Disposition에 없으면 URL에서 추출
                raw_name = os.path.basename(url)
                filename = decode_filename(raw_name)

            if not filename:
                raise ValueError("파일 이름을 찾을 수 없습니다.")

            file_path = os.path.join(self.download_dir, filename)
            with open(file_path, "wb") as f:
                f.write(response.content)

            print(f"✅ 다운로드 완료: {file_path}")
            return file_path, filename

        except Exception as e:
            print(f"❌ 다운로드 실패: {e}")
            return None, None


    def pdf_extractor(self, file_path: str) -> str:
        """PDF 파일에서 텍스트를 추출합니다."""
        try:
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text()
            return text.strip()
        except Exception as e:
            return f"[❌ PDF 추출 실패: {e}]"

    def xlsx_extractor(self, file_path: str) -> str:
        from openpyxl import load_workbook
        workbook = load_workbook(filename=file_path, data_only=True)
        extracted_text = ""

        for sheet in workbook.worksheets:
            for row in sheet.iter_rows(values_only=True):
                row_text = [str(cell) for cell in row if cell is not None]
                if row_text:
                    extracted_text += " ".join(row_text) + "\n"

        return extracted_text.strip()

    def docx_extractor(self, file_path: str) -> str:
        """DOCX 파일에서 텍스트를 추출합니다."""
        try:
            from docx import Document
            doc = Document(file_path)
            document_element = doc._element.body

            texts = []

            for child in document_element:
                if child.tag.endswith('}p'):  # 일반 문단
                    texts.append(''.join([r.text or '' for r in child.iter() if r.tag.endswith('}t')]))
                elif child.tag.endswith('}tbl'):  # 표
                    for row in child.iter():
                        if row.tag.endswith('}tr'):
                            row_text = []
                            for cell in row.iter():
                                if cell.tag.endswith('}tc'):
                                    cell_text = ''.join([t.text or '' for t in cell.iter() if t.tag.endswith('}t')])
                                    row_text.append(cell_text)
                            if row_text:
                                texts.append('\t'.join(row_text))

            return '\n'.join([t for t in texts if t.strip()])
        except Exception as e:
            return f"[❌ DOCX 추출 실패: {e}]"

    
    def txt_extractor(self, file_path: str) -> str:
        """TXT 파일에서 텍스트를 추출합니다."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read().strip()
        except UnicodeDecodeError:
            # CP949 (euc-kr)로 재시도: 윈도우에서 저장된 텍스트 파일 대응
            try:
                with open(file_path, "r", encoding="cp949") as f:
                    return f.read().strip()
            except Exception as e:
                return f"[❌ TXT 추출 실패 (인코딩 오류): {e}]"
        except Exception as e:
            return f"[❌ TXT 추출 실패: {e}]"
    
    def hwp_extractor(self, file_path: str) -> str:
        """HWP 파일에서 텍스트를 추출합니다."""
        import zlib
        import struct
        import re
        def remove_hanja(text):
            # 한자 유니코드 범위: \u4E00 - \u9FFF
            hanja_pattern = re.compile(r'[\u4E00-\u9FFF]+')
            return hanja_pattern.sub('', text)

        f = olefile.OleFileIO(file_path)
        dirs = f.listdir()

        # HWP 파일 검증
        if ["FileHeader"] not in dirs or \
                ["\x05HwpSummaryInformation"] not in dirs:
            raise Exception("Not Valid HWP.")

        # 문서 포맷 압축 여부 확인
        header = f.openstream("FileHeader")
        header_data = header.read()
        is_compressed = (header_data[36] & 1) == 1

        # Body Sections 불러오기
        nums = []
        for d in dirs:
            if d[0] == "BodyText":
                nums.append(int(d[1][len("Section"):]))
        sections = ["BodyText/Section" + str(x) for x in sorted(nums)]

        # 전체 text 추출
        text = ""
        for section in sections:
            bodytext = f.openstream(section)
            data = bodytext.read()
            if is_compressed:
                unpacked_data = zlib.decompress(data, -15)
            else:
                unpacked_data = data

            # 각 Section 내 text 추출
            section_text = ""
            i = 0
            size = len(unpacked_data)
            while i < size:
                header = struct.unpack_from("<I", unpacked_data, i)[0]
                rec_type = header & 0x3ff
                rec_len = (header >> 20) & 0xfff

                if rec_type in [67]:
                    rec_data = unpacked_data[i + 4:i + 4 + rec_len]
                    section_text += rec_data.decode('utf-16')
                    section_text += "\n"

                i += 4 + rec_len

            text += section_text
            text += "\n"

        f.close()
        return remove_hanja(text)
    
    def hwpx_extractor(self, file_path: str) -> str:
        """HWPX 파일에서 텍스트를 추출합니다."""
        text_output = []

        # .hwpx는 ZIP 형식이므로 압축 해제
        with zipfile.ZipFile(file_path, 'r') as zip_file:
            # 'Contents/section*.xml' 파일에서 텍스트를 추출
            section_files = [name for name in zip_file.namelist() if name.startswith("Contents/section") and name.endswith(".xml")]
            for section_file in sorted(section_files):
                with zip_file.open(section_file) as file:
                    tree = ET.parse(file)
                    root = tree.getroot()

                    # 'w:t' 요소에서 텍스트 추출
                    for elem in root.iter():
                        if 't' in elem.tag:  # 태그 이름에 't'가 포함된 경우
                            if elem.text:
                                text_output.append(elem.text)

        return '\n'.join(text_output)
    
    def image_extractor(self, file_path: str) -> str:
        """이미지 파일에서 텍스트를 추출합니다."""
        
        if not os.path.exists(file_path):
            return f"[❌ 이미지 파일이 존재하지 않습니다: {file_path}]"

        # 이미지 파일 열기
        try:
            image = Image.open(file_path).convert("RGB")
            image_np = np.array(image)
        except Exception as e:
            return f"[❌ 이미지 열기 실패: {e}]"

        # easyocr로 텍스트 추출
        try:
            reader = easyocr.Reader(['ko', 'en'], gpu=False)
            results = reader.readtext(image_np, detail=0)
            return "\n".join(results).strip()
        except Exception as e:
            return f"[❌ easyocr 텍스트 추출 실패: {e}]"
        
    def extract_text(self, file_path):
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()

        try:
            if ext == ".pdf":
                text = self.pdf_extractor(file_path)
                return text

            elif ext == ".docx":
                text = self.docx_extractor(file_path)
                return text

            elif ext == ".xlsx":
                text = self.xlsx_extractor(file_path)
                return text

            elif ext == ".txt":
                text = self.txt_extractor(file_path)
                return text

            elif ext == ".hwp":
                text = self.hwp_extractor(file_path)
                return text
            
            elif ext == ".hwpx":
                text = self.hwpx_extractor(file_path)
                return text
            
            elif ext == '.jpg' or ext == '.jpeg' or ext == '.png':
                text = self.image_extractor(file_path)
                return text

            else:
                return f"[지원되지 않는 파일 형식: {ext}]"
        except Exception as e:
            return f"[텍스트 추출 실패: {e}]"

    def process_attachments(self, url_list):
        results = {}
        file_name_list = []
        for url in url_list:
            file_path, file_name = self.download_file(url)
            if file_path is None and file_name is None: #### 즉, 다운로드 실패한 경우
                return None, None

            if file_path:
                text = self.extract_text(file_path)
                results[url] = text
                file_name_list.append(file_name)
                try:
                    os.remove(file_path)
                    print(f"✅ 다운로드한 파일 삭제 성공")
                except Exception as e:
                    print(f"❌ 다운로드한 파일 삭제 실패: {file_path} -> {e}")
            else:
                results[url] = None
                file_name_list.append(None)
        return results, file_name_list
    
# 테스트용 코드
if __name__ == "__main__":  
    # 테스트용 URL 목록
    hwp_url = "https://cse.kangwon.ac.kr/cse/community/undergraduate-notice.do?mode=download&articleNo=501724&attachNo=537931"
    hwpx_url = "https://ai.kangwon.ac.kr/ai/community/notice.do?mode=download&articleNo=456806&attachNo=507730"
    xlsx_url = "https://cse.kangwon.ac.kr/cse/community/undergraduate-notice.do?mode=download&articleNo=516526&attachNo=539616"
    pdf_url = "https://cse.kangwon.ac.kr/cse/community/undergraduate-notice.do?mode=download&articleNo=516526&attachNo=539615"
    docx_url = "https://wwwk.kangwon.ac.kr/www/downloadBbsFile.do?atchmnflNo=103343&bbsNo=34&nttNo=176921&&pageUnit=10&key=232&pageIndex=8"
    #docx_url = "https://admission.kangwon.ac.kr/www/downloadBbsFile.do?atchmnflNo=66929&bbsNo=81&nttNo=146995&&pageUnit=10&key=277&pageIndex=1097"
    txt_url = "https://jw.kangwon.ac.kr/jw/community/notice.do?mode=download&articleNo=365222&attachNo=368559"
    image_url = "https://wwwk.kangwon.ac.kr/itservice/downloadBbsFile.do?atchmnflNo=103829&bbsNo=107&nttNo=177358&&pageUnit=10&key=735&pageIndex=1"
    error_url = "https://wwwk.kangwon.ac.kr/itservice/downloadBbsFile.do?atchmnflNo=43000&bbsNo=107&nttNo=127152&&pageUnit=10&key=735&pageIndex=12"
    

    
    test_urls = [
        hwp_url, ## 검증 완료
        #hwpx_url, ## 검증 완료
        #xlsx_url, ## 검증 완료
        #pdf_url, ## 검증 완료
        #docx_url, ## 검증 완료
        #txt_url, ## 검증 완료
        #image_url, ## 검증 완료
        #error_url
    ]

    processor = AttachmentProcessor()
    results = processor.process_attachments(test_urls)
    
    
    for url, text in results.items():
        print(f"URL: {url}\n텍스트: {text}\n")
        # 텍스트 전문 확인용
        # with open("extracted_text.txt", "a", encoding="utf-8") as f:
        #     f.write(text + "\n")
        #     f.write("="*50 + "\n")

    

