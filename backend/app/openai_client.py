import os
from typing import Any, Dict, List, Optional

try:
    from openai import OpenAI
except ImportError:  # Allows non-chat endpoints and tests to run before optional deps are installed.
    OpenAI = None

from app.config import OPENAI_MODEL


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
