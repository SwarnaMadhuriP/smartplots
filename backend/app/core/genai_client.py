import os

from dotenv import load_dotenv
from google import genai

_client: genai.Client | None = None


def get_genai_client() -> genai.Client:
    global _client

    if _client is not None:
        return _client

    load_dotenv()

    use_vertex = os.environ.get("GOOGLE_GENAI_USE_VERTEXAI", "True") == "True"

    if use_vertex:
        try:
            import google.auth

            google.auth.default()
        except Exception:
            os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "False"
            use_vertex = False

    if use_vertex:
        _client = genai.Client(
            vertexai=True,
            location="global",
        )
    else:
        gemini_key = os.environ.get("GEMINI_API_KEY")
        if not os.environ.get("GOOGLE_API_KEY") and gemini_key:
            os.environ["GOOGLE_API_KEY"] = gemini_key

        _client = genai.Client(vertexai=False)

    return _client