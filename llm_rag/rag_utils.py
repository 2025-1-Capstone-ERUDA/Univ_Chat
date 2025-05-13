# rag_utils.py

def search_documents(query: str, index) -> list:
    """
    주어진 쿼리를 사용하여 벡터 스토어에서 문서를 검색합니다.

    Args:
        query (str): 검색할 쿼리
        vectorstore: 벡터 스토어 객체

    Returns:
        list: 검색된 문서 리스트
    """

    # 5개 문서를 반환하는 retriever 생성
    retriever = index.as_retriever(similarity_top_k=5)

    # 문서 검색
    retrieved_nodes = retriever.retrieve(query)

    # 결과 출력
    for i, node in enumerate(retrieved_nodes, 1):
        print(f"\n📄 문서 {i}")
        print(node.get_content())  # 또는 print(node.text)
    
    return retrieved_nodes

# 테스트용 코드
if __name__ == "__main__":
    from embedding import load_index
    import os

    # 벡터 스토어 로드
    dir_path = os.path.join(os.path.dirname(__file__), "..", "vectorstore")
    index = load_index(dir_path)

    # 사용자 쿼리
    user_query = "예비군"
    
    # # 문서 검색
    # documents = search_documents(user_query, index)
    
    # print(documents)