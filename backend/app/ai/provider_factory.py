"""Create AI providers lazily so optional SDKs do not prevent API startup."""


def get_provider(model: str):
    model = model.lower().strip()

    if model == "gemini":
        try:
            from app.ai.providers.gemini import GeminiProvider
        except ImportError as exc:
            raise RuntimeError(
                "Gemini SDK is missing. Install backend dependencies with: "
                "pip install -r requirements.txt"
            ) from exc
        return GeminiProvider()

    if model == "groq":
        try:
            from app.ai.providers.groq import GroqProvider
        except ImportError as exc:
            raise RuntimeError(
                "Groq SDK is missing. Install backend dependencies with: "
                "pip install -r requirements.txt"
            ) from exc
        return GroqProvider()

    raise ValueError(f"Unsupported AI model: {model}")
