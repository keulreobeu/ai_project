import os
from typing import Any, Dict, List, Optional

from pydantic import types

try:
    from openai import OpenAI
except ImportError:  # Allows non-chat endpoints and tests to run before optional deps are installed.
    OpenAI = None

from app.config import OPENAI_MODEL
from app.config import GEMINI_MODEL

from google import genai
from google.genai import types



class GeminiClient:
    def __init__(self) -> None:
        self.api_key = os.getenv("GEMINI_API_KEY", "").strip()
        self._client: Optional[genai.Client] = (
            genai.Client(api_key=self.api_key) if genai and self.api_key else None
        )

    def ensure_api_key(self) -> None:
        if not self._client:
            raise RuntimeError(
                "Gemini 클라이언트가 설치되지 않았거나 GEMINI_API_KEY 환경 변수가 설정되지 않았습니다."
            )

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "gemini-3.5-flash",
        temperature: float = 0.5,
        max_tokens: int = 500,
    ) -> str:
        self.ensure_api_key()
        assert self._client is not None
        
        print("🔄 [GeminiClient] API 호출 프로세스 시작...")

        # 1. 메시지 변환 (SDK에서 가장 안전하게 처리하는 '딕셔너리' 형태로 가공합니다)
        gemini_contents = []
        system_instruction = None

        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")

            if role == "system":
                system_instruction = content
            else:
                gemini_role = "model" if role == "assistant" else "user"
                # types.Content 객체 대신 API 가 가증 잘 이해하는 표준 Dict 구조로 변환
                gemini_contents.append({
                    "role": gemini_role,
                    "parts": [{"text": content}]
                })

        print(f"💬 [GeminiClient] 변환된 Contents 데이터: {gemini_contents}")
        if system_instruction:
            print(f"⚙️ [GeminiClient] 시스템 프롬프트 감지됨: {system_instruction[:30]}...")

        # 2. 예외 처리 범위를 위로 끌어올려 config 생성 시점의 에러도 잡아냅니다.
        try:
            print("⚙️ [GeminiClient] GenerateContentConfig 구성 중...")
            config = types.GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
                system_instruction=system_instruction
            )

            print(f"⚡ [GeminiClient] '{model}' 모델로 구글 서버에 전송 중...")
            response = self._client.models.generate_content(
                model=model,
                contents=gemini_contents,
                config=config,
            )
            
            print("✅ [GeminiClient] API 호출 완료! 응답 데이터를 성공적으로 받았습니다.")
            content = response.text
            return content.strip() if content else ""

        except Exception as e:
            # 백엔드 콘솔 터미널에 진짜 에러 원인을 찍어줍니다.
            print(f"❌ [GeminiClient ERROR] API 전송 혹은 응답 분석 중 오류 발생: {str(e)}")
            import traceback
            traceback.print_exc() # 에러가 발생한 정확한 코드 라인 추적을 위해 출력
            raise e

# class GeminiClient:
#     def __init__(self) -> None:
#         # google-genai SDK는 기본적으로 GEMINI_API_KEY 환경 변수를 자동으로 감지합니다.
#         self.api_key = os.getenv("GEMINI_API_KEY", "").strip()
        
#         # 클라이언트 초기화
#         self._client: Optional[genai.Client] = (
#             genai.Client(api_key=self.api_key) if genai and self.api_key else None
#         )

#     def ensure_api_key(self) -> None:
#         if not self._client:
#             raise RuntimeError(
#                 "Gemini 클라이언트가 설치되지 않았거나 GEMINI_API_KEY 환경 변수가 설정되지 않았습니다."
#             )

#     def chat_completion(
#         self,
#         messages: List[Dict[str, str]],
#         model: str = "gemini-3.5-flash",
#         temperature: float = 0.5,
#         max_tokens: int = 500,
#     ) -> str:
#         self.ensure_api_key()
#         assert self._client is not None
#         print("🔄 Gemini API 호출 중...")
#         # 1. OpenAI 형식의 messages [{'role': 'user', 'content': '...'}]를
#         # Gemini의 Content 형식으로 변환합니다.
#         gemini_contents = []
#         system_instruction = None

#         for msg in messages:
#             role = msg.get("role", "user")
#             content = msg.get("content", "")

#             # Gemini에서는 System Instruction(System Prompt)을 contents 배열이 아닌 
#             # 별도의 config 매개변수로 주입하는 것이 가장 안정적입니다.
#             if role == "system":
#                 system_instruction = content
#             else:
#                 # OpenAI의 'assistant' 역할 이름은 Gemini에서 'model'로 대응됩니다.
#                 gemini_role = "model" if role == "assistant" else "user"
#                 gemini_contents.append(
#                     types.Content(
#                         role=gemini_role,
#                         parts=[types.Part.from_text(text=content)]
#                     )
#                 )
#         print(f"💬 변환된 Gemini Contents: {gemini_contents}")
#         # 2. 실행 파라미터(GenerateContentConfig) 설정
#         config = types.GenerateContentConfig(
#             temperature=temperature,
#             max_output_tokens=max_tokens,  # OpenAI의 max_tokens에 대응
#             system_instruction=system_instruction
#         )
#         print(f"⚙️ Gemini Config: {config}")
#         # 3. Gemini API 호출
#         response = self._client.models.generate_content(
#             model=model,
#             contents=gemini_contents,
#             config=config,
#         )
#         print (f"✅ Gemini API 호출 완료. Raw Response: {response}")
#         # 4. 결과 반환
#         content = response.text


#         print("✅ Gemini API 호출 완료. 결과:", content)
#         return content.strip() if content else ""
        

class OpenAIClient:
    def __init__(self) -> None:
        self.api_key = os.getenv("OPENAI_API_KEY", "").strip()
        self._client: Optional[Any] = OpenAI(api_key=self.api_key) if OpenAI and self.api_key else None

    def ensure_api_key(self) -> None:
        if not self._client:
            raise RuntimeError(
                "OpenAI 클라이언트가 설치되지 않았거나 OPENAI_API_KEY 환경 변수가 설정되지 않았습니다."
            )

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = OPENAI_MODEL,
        temperature: float = 0.5,
        max_tokens: int = 500,
    ) -> str:
        self.ensure_api_key()
        assert self._client is not None
        response = self._client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        content = response.choices[0].message.content
        return content.strip() if content else ""
