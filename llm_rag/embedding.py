# embedding_utils.py
import os
import torch
import pandas as pd
from langchain.schema import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# CPU/GPU 사용 설정
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# 임베딩 모델 초기화
embedding_model = HuggingFaceEmbeddings(
    model_name="upskyy/kf-deberta-multitask",       # 한국어 문장과 단락에 특화된 모델
    model_kwargs={'device': f'{device}'},
    encode_kwargs={"normalize_embeddings": True}
)

def dataframe_to_documents(df):
    """Pandas DataFrame을 LlamaIndex Document 리스트로 변환"""
    
    documents = []
    for _, row in df.iterrows():
        content = f"""
        제목: {row['title']}
        날짜: {row['date']}
        작성자: {row['author']}
        링크: {row['link']}
        학교: {row['university']}
        학과: {row['department']}
        첨부파일: {', '.join(row['attachments']) if row['attachments'] else '없음'}

        내용:
        {row['content']}
        """
        doc = Document(
            page_content=content.strip(),
            metadata={key: row[key] for key in ['title', 'date', 'author', 'articleNo', 'link', 'attachments', 'university', 'department']}
        )
        documents.append(doc)
        
    return documents

def save_faiss(documents: list, dir_path: str):
    """
    Document 객체 리스트를 임베딩하여 FAISS DB에 저장.
    기존 FAISS DB가 존재 시 임베딩 결과를 결합

    Params:
    documents: Document 객체 리스트

    Return:
    dir_path: FAISS DB 저장 경로
    """

    try:
        faiss_vectorstore = FAISS.from_documents(documents, embedding_model)

        faiss_vectorstore.save_local(dir_path)
        print(f"✅ FAISS DB 저장 완료: {dir_path}")
        
        return dir_path
    except Exception as e:
        print(f"FAISS 저장 오류: {e}")
        return None

def load_faiss(dir_path: str) -> bool:
    """
    주어진 디렉토리에서 FAISS DB를 로드하여 vectorstore를 반환.

    Return:
    성공 시: FAISS vectorstore 객체
    실패 시: None
    """

    try:
        vectorstore = FAISS.load_local(
            folder_path=dir_path,
            embeddings=embedding_model,
            allow_dangerous_deserialization=True,
        )
    except Exception as e:
        print(f"FAISS DB 로드 오류: {e}")
        return None
    
    return vectorstore

# 테스트 실행
if __name__ == "__main__":
    csv_path = os.path.join(os.path.dirname(__file__), "..", "data", "posts_2025-05-17_2130.csv")
    df = pd.read_csv(csv_path, encoding="utf-8-sig")
    
    documents = dataframe_to_documents(df)

    dir_path = os.path.join(os.path.dirname(__file__), "..", "vectorstore")
    
    db_path = save_faiss(documents, dir_path)
    vectorstore = load_faiss(db_path)
    if vectorstore:
        print("FAISS DB 로드 성공")
    else:
        print("FAISS DB 로드 실패")