# Revexa PR review: Gemini + Groq

Revexa supports Gemini, Groq, and a side-by-side comparison of both providers for pull-request reviews. Claude/Anthropic is not part of this build.

Configure these values in `backend/.env`:

```env
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-3.8-flash
GROQ_API_KEY=your_groq_api_key
GROQ_REVIEW_MODEL=openai/gpt-oss-120b
```

Install dependencies from `backend` with `pip install -r requirements.txt`. Select Gemini, Groq, or Compare Gemini + Groq in the Pull Request Reviews page.

If one provider fails during comparison, the successful provider result is still returned and the failure is listed separately. If both fail, the API returns an error rather than a fabricated review.
