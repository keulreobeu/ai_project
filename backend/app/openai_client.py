import os
from typing import Dict, List

import openai


class OpenAIClient:
    def __init__(self) -> None:
        self.api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if self.api_key:
            openai.api_key = self.api_key

    def ensure_api_key(self) -> None:
        if not self.api_key:
            raise RuntimeError(
                "OPENAI_API_KEY 환경 변수가 설정되어 있지 않습니다. 프로젝트 루트 또는 환경에 키를 추가하세요."
            )

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.5,
        max_tokens: int = 500,
    ) -> str:
        self.ensure_api_key()
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        choice = response.choices[0]
        return choice.message.content.strip()
