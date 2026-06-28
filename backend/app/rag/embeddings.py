from google.genai import types

from app.core.genai_client import get_genai_client


def generate_embedding(text: str) -> list[float]:
    client = get_genai_client()

    response = client.models.embed_content(
        model="gemini-embedding-2",
        contents=text,
        config=types.EmbedContentConfig(output_dimensionality=768),
    )

    if response.embeddings and len(response.embeddings) > 0:
        values = response.embeddings[0].values
        if values is not None:
            return values

    if hasattr(response, "embedding") and response.embedding is not None:
        values = response.embedding.values
        if values is not None:
            return values

    raise ValueError(
        f"Failed to generate embedding. Response was: {response}"
    )