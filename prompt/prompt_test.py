# 테스트용

import os
import json
import yaml
from llama_index.core.prompts import PromptTemplate
from llama_index.llms.google_genai import GoogleGenAI


# YAML 파일에서 프롬프트 불러오기
def load_prompts(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

# 테스트용 코드
if __name__ == "__main__":
    # secrets.json 에서 API 키 로드
    with open(os.path.join("secrets.json"), "r", encoding="utf-8") as f:
        secrets = json.load(f)

    # 프롬프트 로드
    prompt_path = os.path.join(os.path.dirname(__file__), "LLM_prompts.yaml")
    prompts = load_prompts(prompt_path)

    # 프롬프트 템플릿 생성
    embedding_prompt = PromptTemplate(prompts["embedding_prompt"])

    # 사용자 입력
    user_query = "2025학년도 컴퓨터공학과 졸업요건이 어떻게 되나요?"

    # 템플릿 채우기
    prompt_text = embedding_prompt.format(user_query=user_query)

    print(f"프롬프트 템플릿:\n{prompt_text}\n")
    
    llm = GoogleGenAI(
        model="gemini-2.0-flash",
        api_key=secrets.get("GOOGLE_API_KEY"),
    )

    # 응답 받기
    # resp = llm.complete(prompt_text)
    resp = llm.complete("gemini api에서 gemini-2.0-flash 모델과 gemini-1.5-flash 모델의 토큰량 비교해줘.")
    print(f"LLM 응답:\n{resp}")
    
    
    # ChatMessage 사용 예시
    # from llama_index.core.llms import ChatMessage

    # messages = [
    #     ChatMessage(role="user", content="Hello friend!"),
    #     ChatMessage(role="assistant", content="Yarr what is shakin' matey?"),
    #     ChatMessage(
    #         role="user", content="Help me decide what to have for dinner."
    #     ),
    # ]
    # resp = llm.chat(messages)
    # print(resp)