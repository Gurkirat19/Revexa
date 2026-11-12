from google import genai

from app.config import GEMINI_API_KEY


client = genai.Client(
    api_key=GEMINI_API_KEY
)


response = client.interactions.create(
    model="gemini-3.6-flash",
    input="Explain what a GitHub pull request is in one sentence."
)


print(response.output_text)