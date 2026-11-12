import time
import os

from google import genai
from google.genai import types

from app.config import GEMINI_API_KEY
from app.ai.provider import (
    AIProvider,
    AIResponse,
    ToolCall
)


class GeminiProvider(AIProvider):

    def __init__(self):

        self.client = genai.Client(
            api_key=GEMINI_API_KEY
        )


    def ask(
        self,
        question: str,
        context: str = "",
        tools=None
    ) -> AIResponse:

        prompt = f"""
You are a senior software engineer
analyzing a GitHub repository.

Repository context:

{context}

User question:

{question}

Base your answer only on the
repository information provided.

Do not invent files, functions,
classes, or behavior.

If you need more information
from the repository, use one of
the available tools.
"""


        config = types.GenerateContentConfig()


        # ---------------------------------
        # GEMINI TOOL CONFIGURATION
        # ---------------------------------

        if tools:

            gemini_tool = types.Tool(
                function_declarations=tools
            )

            config.tools = [
                gemini_tool
            ]

            config.automatic_function_calling = (
                types.AutomaticFunctionCallingConfig(
                    disable=True
                )
            )


        # ---------------------------------
        # SEND REQUEST WITH RETRY
        # ---------------------------------

        max_retries = 2

        response = None

        for attempt in range(max_retries + 1):

            try:

                print(
                    f"Gemini request attempt "
                    f"{attempt + 1}"
                )

                response = (
                    self.client.models.generate_content(

                        model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),

                        contents=prompt,

                        config=config

                    )
                )

                break


            except Exception as error:

                error_message = str(error)

                # -----------------------------
                # RETRY ONLY TEMPORARY 503
                # -----------------------------

                is_temporary_error = (
                    "503" in error_message
                    or
                    "UNAVAILABLE" in error_message
                )


                if not is_temporary_error:

                    raise


                # -----------------------------
                # NO RETRIES LEFT
                # -----------------------------

                if attempt >= max_retries:

                    raise RuntimeError(
                        "Gemini is temporarily "
                        "unavailable after multiple "
                        "attempts. Please try again "
                        "or select Groq."
                    )


                # -----------------------------
                # EXPONENTIAL BACKOFF
                # -----------------------------

                delay = 2 ** attempt

                print(
                    "Gemini temporarily unavailable."
                )

                print(
                    f"Retrying in {delay} seconds..."
                )

                time.sleep(delay)


        # ---------------------------------
        # CHECK FUNCTION CALL
        # ---------------------------------

        for part in response.candidates[0].content.parts:

            if part.function_call:

                function_call = part.function_call

                return AIResponse(

                    tool_call=ToolCall(

                        name=function_call.name,

                        arguments=dict(
                            function_call.args
                        )

                    )

                )


        # ---------------------------------
        # NORMAL TEXT RESPONSE
        # ---------------------------------

        answer_parts = []


        for part in response.candidates[0].content.parts:

            if part.text:

                answer_parts.append(
                    part.text
                )


        return AIResponse(

            text="\n".join(
                answer_parts
            )

        )