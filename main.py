import os
from llm_rag.embedding import load_faiss
from llm_rag.llm_utils import embedding_prompt, llm_query_prompt, llm_response
from llm_rag.rag_utils import search_documents

dir_path = os.path.join(os.path.dirname(__file__), "vectorstore")
vectorstore = load_faiss(dir_path)

def process_query(text, department):
    
    # 사용자 입력
    user_query = text
    dp = department
    
    # 프롬프트 생성
    search_prompt = embedding_prompt(user_query)
    
    # LLM 응답
    search_query = llm_response(search_prompt)
    print(f"search_query: {search_query.text}")
    
    documents = search_documents(search_query.text, vectorstore)
    doc_texts = "\n".join([doc.page_content for doc in documents])
    
    # LLM 프롬프트 생성
    prompt = llm_query_prompt(user_query, doc_texts, dp)

    # LLM 응답
    response = llm_response(prompt)
    
    return response.text

# 테스트용 코드
if __name__ == "__main__":
    while True:
        # 사용자 입력 받기
        user_input = input("질문을 입력하세요 (종료하려면 'exit' 입력): ")
     
        # 부서 선택
        department_id = input("부서를 선택하세요 (0: 전체, 1: 컴퓨터공학과, 2: AI융합학과): ")
        if department_id == "0":
            department = "전체"
        elif department_id == "1":
            department = "컴퓨터공학과"
        elif department_id == "2":
            department = "AI융합학과"
        else:
            print("잘못된 부서 선택입니다.")
            continue
        
        # 쿼리 처리
        result = process_query(user_input, department)
        print(result)