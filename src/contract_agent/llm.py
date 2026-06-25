from openai import OpenAI
from .config import YANDEX_API_KEY, YANDEX_BASE_URL, YANDEX_MODEL

_client = OpenAI(api_key=YANDEX_API_KEY, base_url=YANDEX_BASE_URL)


def call_llm(system_prompt: str, user_prompt: str, temperature: float = 0.1, max_tokens: int = 1600) -> str:
    if not YANDEX_API_KEY or not YANDEX_MODEL:
        raise RuntimeError("YANDEX_API_KEY and YANDEX_MODEL must be set in .env")

    response = _client.chat.completions.create(
        model=YANDEX_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content or ""
