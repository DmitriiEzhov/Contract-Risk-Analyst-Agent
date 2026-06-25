import json
import re
from typing import Any


def parse_json_safely(text: str, fallback: Any) -> Any:
    try:
        return json.loads(text)
    except Exception:
        pass

    match = re.search(r"\{.*\}", text, flags=re.S)
    if match:
        try:
            return json.loads(match.group(0))
        except Exception:
            return fallback
    return fallback
