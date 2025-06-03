import os
from llm_rag.embedding import load_faiss
from llm_rag.llm_utils import embedding_prompt, llm_prompt, llm_response
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
    prompt = llm_prompt(user_query, doc_texts)

    # LLM 응답
    response = llm_response(prompt)
    
    return response.text