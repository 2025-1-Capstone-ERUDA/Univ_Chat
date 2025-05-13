from llm_rag.embedding import load_vectorstore
from llama_index.core import Settings
import os

def process_text2(text, department):
    """
    입력 텍스트와 학과 정보를 받아 처리하는 함수.
    department: 'computer_science' 또는 'ai_convergence'.
    """
    dept_name = {
        'all': '전체',
        'computer_science': '컴퓨터공학과',
        'ai_convergence': 'AI융합학과'
    }.get(department, '알 수 없는 학과')
    
    if not text:
        return f"{dept_name}: 텍스트가 입력되지 않았습니다."
    return f"{dept_name}: {text}"

def test(text, department):
    import llm_rag.llm_utils as llm_utils
    
    embedding_prompt = llm_utils.embedding_prompt(text)
    response = llm_utils.llm_response(embedding_prompt)
    print(f"LLM 응답:\n{response}")
    
    return response.text

def process_text(text, department):
    """
    임시시
    """
    
    file_path = os.path.join(os.path.dirname(__file__), "vectorstore", "vectorstore.pkl")
    index = load_vectorstore(file_path)
    
    import json
    secrets_path = os.path.join(os.path.dirname(__file__), "secrets.json")
    with open(secrets_path, "r") as f:
        secrets = json.load(f)
    # Gemini LLM 연결
    from llama_index.llms.google_genai import GoogleGenAI
    Settings.llm = GoogleGenAI(
        model="models/gemini-1.5-flash",
        api_key=secrets.get("GOOGLE_API_KEY")  # 또는 os.environ["GOOGLE_API_KEY"]
    )
    query_engine = index.as_query_engine()

    # 사용자가 질의
    response = query_engine.query(text)

    print(response)
    return response.response