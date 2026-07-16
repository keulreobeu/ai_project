import os
import time
import traceback
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

# class OpenAIClient:
#     def __init__(self) -> None:
#         self.api_key = os.getenv("OPENAI_API_KEY", "").strip()
#         self._client: Optional[Any] = OpenAI(api_key=self.api_key) if OpenAI and self.api_key else None

#     def ensure_api_key(self) -> None:
#         if not self._client:
#             raise RuntimeError(
#                 "OpenAI 클라이언트가 설치되지 않았거나 OPENAI_API_KEY 환경 변수가 설정되지 않았습니다."
#             )

#     def chat_completion(
#         self,
#         messages: List[Dict[str, str]],
#         model: str = OPENAI_MODEL,
#         temperature: float = 0.5,
#         max_tokens: int = 500,
#     ) -> str:
#         self.ensure_api_key()
#         assert self._client is not None
#         print("🔄 [OpenAIClient] API 호출 프로세스 시작...")
#         response = self._client.chat.completions.create(
#             model=model,
#             messages=messages,
#             temperature=temperature,
#             max_tokens=max_tokens,
#         )
#         print(f"💬 [OpenAIClient] API 응답 데이터: {response}")
#         content = response.choices[0].message.content
#         return content.strip() if content else ""

class OpenAIClient:
    def __init__(self) -> None:
        self.api_key = os.getenv("OPENAI_API_KEY", "").strip()
        # API 키 마스킹 처리하여 출력 (보안 유지 및 설정 여부 확인)
        masked_key = self.api_key[:6] + "..." + self.api_key[-4:] if len(self.api_key) > 10 else "없음"
        print(f"🔍 [OpenAIClient] 초기화 중... 로드된 API Key: {masked_key}")
        
        try:
            self._client: Optional[Any] = OpenAI(api_key=self.api_key) if 'OpenAI' in globals() and self.api_key else None
            print(f"🔍 [OpenAIClient] 라이브러리 및 클라이언트 상태: OpenAI 존재여부={'OpenAI' in globals()}, 클라이언트 생성여부={self._client is not None}")
        except Exception as e:
            print(f"❌ [OpenAIClient] 초기화 중 에러 발생: {e}")
            self._client = None

    def ensure_api_key(self) -> None:
        if not self._client:
            raise RuntimeError(
                f"OpenAI 클라이언트가 설치되지 않았거나 OPENAI_API_KEY 환경 변수가 설정되지 않았습니다. (현재 Key 존재여부: {bool(self.api_key)})"
            )

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-5-mini", # 예시 기본값 변경
        temperature: float = 0.5,
        max_tokens: int = 50000,
    ) -> str:
        # gpt-5-mini(reasoning 계열)는 커스텀 temperature와 max_tokens를 지원하지 않는다.
        # temperature는 기본값(1)만 허용되어 전달하지 않고, max_tokens는 max_completion_tokens로 보낸다.
        # reasoning_tokens가 max_completion_tokens 예산을 함께 소비하므로 여유 있게 잡는다.
        self.ensure_api_key()
        assert self._client is not None
        
        # 1. 입력 매개변수 디버깅 출력
        print("\n🔄 ================= [OpenAIClient] API 호출 시작 =================")
        print(f"🚀 호출 모델: {model}")
        print(f"🎛️ 설정 매개변수: temperature={temperature}, max_tokens={max_tokens}")
        print(f"✉️ 전달 데이터 (Messages 요약): 총 {len(messages)}개의 메시지")
        for i, msg in enumerate(messages):
            print(f"  [{i}] role: {msg.get('role')} | content 일부: {str(msg.get('content'))[:50]}...")
        print("====================================================================")

        start_time = time.time()
        try:
            # 2. 실제 API 호출 및 시간 측정
            response = self._client.chat.completions.create(
                model=model,
                messages=messages,
                max_completion_tokens=max_tokens,
            )
            
            elapsed_time = time.time() - start_time
            print(f"✅ [OpenAIClient] API 호출 성공! (소요 시간: {elapsed_time:.2f}초)")
            print(f"💬 [OpenAIClient] 전체 응답 객체 데이터: {response}")
            
            content = response.choices[0].message.content
            return content.strip() if content else ""

        except Exception as e:
            # 3. 에러 발생 시 상세 트레이스백 출력
            elapsed_time = time.time() - start_time
            print(f"❌ [OpenAIClient] API 호출 실패... (최종 소요 시간: {elapsed_time:.2f}초)")
            print(f"🚨 에러 유형: {type(e).__name__}")
            print(f"🚨 에러 메시지: {e}")
            print("📋 [상세 에러 트레이스백]")
            traceback.print_exc()
            print("====================================================================\n")
            raise e # 상위 레이어로 에러 전파