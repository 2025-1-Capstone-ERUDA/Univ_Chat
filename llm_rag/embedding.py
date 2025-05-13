# embedding_utils.py
import os
import torch
import pandas as pd
from llama_index.core.schema import Document
from llama_index.core import VectorStoreIndex, Settings
from llama_index.core import VectorStoreIndex, StorageContext, load_index_from_storage
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

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
            text=content.strip(),
            metadata={key: row[key] for key in ['title', 'date', 'author', 'articleNo', 'link', 'attachments', 'university', 'department']}
        )
        documents.append(doc)
        
    return documents

def configure_embedding_model():
    """임베딩 모델 설정 (KoBERT 기반)"""
    
    Settings.embed_model = HuggingFaceEmbedding(
        model_name="jhgan/ko-sroberta-multitask",
        device="cuda" if torch.cuda.is_available() else "cpu"
    )

def make_index(df):
    """DataFrame으로부터 VectorStoreIndex 생성"""
    
    configure_embedding_model()
    documents = dataframe_to_documents(df)
    
    index = VectorStoreIndex.from_documents(documents)
    
    return index

def save_index(index, dir_path):
    """VectorStoreIndex를 지정 디렉토리에 저장"""
    
    os.makedirs(dir_path, exist_ok=True)
    
    try:
        index.storage_context.persist(persist_dir=dir_path)
        print(f"✅ Index saved: {dir_path}")
        
        return dir_path
    except Exception as e:
        print(f"❌ 저장 실패: {e}")
        return None

def load_index(dir_path):
    """VectorStoreIndex를 파일로부터 로드"""
    
    try:
        storage_context = StorageContext.from_defaults(persist_dir=dir_path)
        index = load_index_from_storage(storage_context)
        print(f"✅ Index loaded: {dir_path}")
        
        return index
    except Exception as e:
        print(f"❌ 로드 실패: {e}")
        return None

# 테스트 실행
if __name__ == "__main__":
    csv_path = os.path.join(os.path.dirname(__file__), "..", "data", "posts_2025-04-28_1501.csv")
    df = pd.read_csv(csv_path, encoding="utf-8-sig")

    index = make_index(df)

    out_dir = os.path.join(os.path.dirname(__file__), "..", "vectorstore")
    dir_path = save_index(index, out_dir)

    loaded_index = load_index(dir_path)
    if loaded_index:
        print("VectorStoreIndex 로드 성공")
    else:
        print("VectorStoreIndex 로드 실패")