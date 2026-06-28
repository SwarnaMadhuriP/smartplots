import os
import google.auth


def configure_google():
    try:
        _, project_id = google.auth.default()
        if not project_id:
            project_id = "mock-project-id"
    except Exception:
        project_id = os.environ.get(
            "GOOGLE_CLOUD_PROJECT",
            "mock-project-id",
        )

    os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
    os.environ["GOOGLE_CLOUD_LOCATION"] = "global"

    use_vertex = os.environ.get("GOOGLE_GENAI_USE_VERTEXAI")

    if use_vertex is None:
        if os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY"):
            os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "False"
        else:
            os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"

    if os.environ["GOOGLE_GENAI_USE_VERTEXAI"] == "False":
        gemini_key = os.environ.get("GEMINI_API_KEY")
        if gemini_key and not os.environ.get("GOOGLE_API_KEY"):
            os.environ["GOOGLE_API_KEY"] = gemini_key