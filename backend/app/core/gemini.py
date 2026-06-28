import re
import time

from google.genai import types
from app.core.genai_client import get_genai_client


def call_with_retry(
    model: str,
    contents: str,
    config: types.GenerateContentConfig,
    max_retries: int = 3,
) -> types.GenerateContentResponse:
    """
    Calls Gemini with automatic retry on 429 RESOURCE_EXHAUSTED (per-minute limit).
    Extracts the suggested retry delay from the error response when available.
    Daily quota exhaustion (limit: 20/day) is re-raised immediately — no retry.
    """
    for attempt in range(max_retries):
        try:
            return get_genai_client().models.generate_content(
                model=model,
                contents=contents,
                config=config,
            )
        except Exception as e:
            err_str = str(e)
            is_rate_limit = "429" in err_str or "RESOURCE_EXHAUSTED" in err_str
            is_daily_exhausted = "PerDay" in err_str or "per_day" in err_str.lower()

            if is_rate_limit and not is_daily_exhausted and attempt < max_retries - 1:
                # Parse the suggested retry delay from the error message if present
                match = re.search(r"retry(?:[\s_-]in)?[:\s]*([\d.]+)s", err_str, re.I)
                wait = float(match.group(1)) if match else (2 ** attempt * 5)
                time.sleep(wait)
                continue

            # Daily quota exhausted or non-retryable — surface a clean message
            if is_daily_exhausted:
                raise RuntimeError(
                    "Daily AI quota reached. Please wait until tomorrow or upgrade your API plan."
                ) from e
            raise

    raise RuntimeError("Max retries exhausted without a successful response.")