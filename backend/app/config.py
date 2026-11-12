import os
from pathlib import Path

from dotenv import load_dotenv


# Resolve .env relative to this module, not the shell's current directory.
load_dotenv(Path(__file__).resolve().parents[1] / ".env", override=False)


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


# Provider credentials are checked when their integrations are used.
