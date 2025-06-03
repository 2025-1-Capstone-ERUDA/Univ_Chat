# rag_utils.py

def search_documents(query: str, vectorstore) -> list:
    """
    주어진 쿼리를 사용하여 벡터 스토어에서 문서를 검색합니다.

    Args:
        query (str): 검색할 쿼리
        vectorstore: 벡터 스토어 객체

    Returns:
        list: 검색된 문서 리스트
    """

    faiss_results = vectorstore.similarity_search(query, k=10)
    
    return faiss_results

# 테스트용 코드
if __name__ == "__main__":
    from embedding import load_faiss
    import os

    # 벡터 스토어 로드
    dir_path = os.path.join(os.path.dirname(__file__), "..", "vectorstore")
    index = load_faiss(dir_path)

    # 사용자 쿼리
    user_query = "예비군"
    
    # 문서 검색
    documents = search_documents(user_query, index)
    for doc in documents:
        print(doc.page_content[:100])