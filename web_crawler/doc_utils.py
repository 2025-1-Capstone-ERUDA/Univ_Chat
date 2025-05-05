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

    def download_file(self, url):
        
        try:
            response = requests.get(url)
            cd = response.headers.get('Content-Disposition', '')
            filename_match = re.search(r'filename\*?=[\'"]?(?:UTF-8\'\')?([^\'";]+)', cd)
            
            if filename_match:
                encoded_name = filename_match.group(1)
                decoded_name = unquote(encoded_name)
            else:
                raise ValueError("파일 이름을 찾을 수 없습니다.")
                
            # print(f"파일명: {decoded_name}")

            file_path = os.path.join(self.download_dir, decoded_name)
            open(file_path, "wb").write(response.content)

            print(f"✅ 다운로드 완료: {file_path}")
            return file_path
        except Exception as e:
            print(f"❌ 다운로드 실패: {e}")
            return None
        
    def pdf_extractor(self, file_path: str) -> str:
        """PDF 파일에서 텍스트를 추출합니다."""
        return "pdf text"
    
    def docx_extractor(self, file_path: str) -> str:
        """DOCX 파일에서 텍스트를 추출합니다."""
        return "docx text"
    
    def txt_extractor(self, file_path: str) -> str:
        """TXT 파일에서 텍스트를 추출합니다."""
        return "txt text"
    
    def hwp_extractor(self, file_path: str) -> str:
        """HWP 파일에서 텍스트를 추출합니다."""
        if not olefile.isOleFile(file_path):
            raise ValueError("올바른 HWP 파일이 아닙니다.")

        with olefile.OleFileIO(file_path) as ole:
            if not ole.exists('PrvText'):
                raise ValueError("텍스트 스트림(PrvText)을 찾을 수 없습니다.")
        
            with ole.openstream('PrvText') as stream:
                text_bytes = stream.read()
                text = text_bytes.decode('utf-16', errors='ignore')
                return text
    
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
        for url in url_list:
            file_path = self.download_file(url)
            if file_path:
                text = self.extract_text(file_path)
                results[url] = text
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f"다운로드한 파일 삭제 실패: {file_path} -> {e}")
            else:
                results[url] = None
        return results
    
# 테스트용 코드
if __name__ == "__main__":  
    # 테스트용 URL 목록
    hwp_url = "https://cse.kangwon.ac.kr/cse/community/undergraduate-notice.do?mode=download&articleNo=501724&attachNo=537931"
    hwpx_url = ""
    xlsx_url = "https://cse.kangwon.ac.kr/cse/community/undergraduate-notice.do?mode=download&articleNo=516526&attachNo=539616"
    pdf_url = "https://cse.kangwon.ac.kr/cse/community/undergraduate-notice.do?mode=download&articleNo=516526&attachNo=539615"
    docx_url = ""
    txt_url = ""
    image_url = "https://cse.kangwon.ac.kr/cse/community/undergraduate-notice.do?mode=download&articleNo=441793&attachNo=484103"
    error_url = "https://cse.kangwon.ac.kr/cse/community/undergraduate-notice.do?mode=download&articleNo=364536&attachNo=367495"
    hwp_url = "https://cse.kangwon.ac.kr/cse/community/undergraduate-notice.do?mode=download&articleNo=501724&attachNo=537931"
    hwpx_url = "https://account.kangwon.ac.kr/account/community/notice.do?mode=download&articleNo=515279&attachNo=539600"

    
    test_urls = [
        hwp_url,
        hwpx_url,
        # xlsx_url,
        # pdf_url,
        # docx_url,
        # txt_url,
        # image_url,
        # error_url
    ]

    processor = AttachmentProcessor()
    results = processor.process_attachments(test_urls)

    for url, text in results.items():
        print(f"URL: {url}\n텍스트: {text[:100]}\n")
        # 텍스트 전문 확인용
        with open("extracted_text.txt", "a", encoding="utf-8") as f:
            f.write(text + "\n")
            f.write("="*50 + "\n")