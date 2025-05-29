# llm_utils.py

import os
import json
import yaml
from llama_index.core.prompts import PromptTemplate

# YAML 파일에서 프롬프트 불러오기
def load_prompts(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
    
def embedding_prompt(user_query: str) -> str:
    """
    사용자 질의에 대해 vectorstore 검색에 최적화된 사용자 질의를 생성합니다.

    Args:
        user_query (str): 사용자 질의

    Returns:
        str: 최적화된 사용자 질의
    """
    
    # 프롬프트 로드
    prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompt", "prompts.yaml")
    prompts = load_prompts(prompt_path)
    
    # 프롬프트 템플릿 생성
    embedding_prompt = PromptTemplate(prompts["embedding_prompt"])
    
    # 템플릿 채우기
    prompt_text = embedding_prompt.format(user_query=user_query)
    
    return prompt_text

def llm_query_prompt(user_query: str, department: str, documents: list) -> str:
    """
    사용자 질의와 유사한 문서를 통해 LLM에 최적화된 사용자 질의를 생성합니다.

    Args:
        user_query (str): 사용자 질의
        documents (list): 검색된 문서 리스트

    Returns:
        str: 최적화된 사용자 질의
    """
    
    # 프롬프트 로드
    prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompt", "prompts.yaml")
    prompts = load_prompts(prompt_path)
    
    # 프롬프트 템플릿 생성
    llm_prompt = PromptTemplate(prompts["llm_prompt"])
    
    # 템플릿 채우기
    prompt_text = llm_prompt.format(user_query=user_query, dp=department, document_content=documents)
    
    return prompt_text

def llm_response(prompt_text):
    # secrets.json 에서 API 키 로드
    with open(os.path.join("secrets.json"), "r", encoding="utf-8") as f:
        secrets = json.load(f)
    
    # LLM 연결
    from llama_index.llms.google_genai import GoogleGenAI
    llm = GoogleGenAI(
        model="gemini-1.5-flash",
        api_key=secrets.get("GOOGLE_API_KEY"),
        temperature=0
    )
    
    # 응답 받기
    resp = llm.complete(prompt_text)
    
    return resp

# 테스트용 코드
if __name__ == "__main__":
    # 사용자 입력
    user_query = "2025학년도 컴퓨터공학과 졸업요건이 어떻게 되나요?"
    
    # 프롬프트 생성
    query_text = embedding_prompt(user_query)
    
    print(f"프롬프트 템플릿:\n{query_text}\n")
    
    # LLM 응답
    response = llm_response(query_text)
    
    print(f"LLM 응답:\n{response}")
    
    # 문서 검색
    from embedding import load_faiss
    from rag_utils import search_documents
    dir_path = os.path.join(os.path.dirname(__file__), "..", "vectorstore")
    vectorstore = load_faiss(dir_path)
    documents = search_documents(query_text, vectorstore)
    doc_texts = "\n".join([doc.page_content for doc in documents])
    
    # LLM 프롬프트 생성
    llm_query_text = llm_query_prompt(user_query, doc_texts)
    print(f"LLM 프롬프트 템플릿:\n{llm_query_text}\n")
    # LLM 응답
    llm_response = llm_response(llm_query_text)
    print(f"LLM 응답:\n{llm_response}")