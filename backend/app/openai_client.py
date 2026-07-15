import os
from typing import Dict, List, Optional

from openai import OpenAI


class OpenAIClient:
    def __init__(self) -> None:
        self.api_key = os.getenv("OPENAI_API_KEY", "").strip()
        self._client: Optional[OpenAI] = OpenAI(api_key=self.api_key) if self.api_key else None

    def ensure_api_key(self) -> None:
        if not self._client:
            raise RuntimeError(
                "OPENAI_API_KEY 환경 변수가 설정되어 있지 않습니다. .env 또는 실행 환경에 키를 추가하세요."
            )

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4o-mini",
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
