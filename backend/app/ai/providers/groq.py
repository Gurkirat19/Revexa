from groq import Groq

from app.config import GROQ_API_KEY
from app.ai.provider import (
    AIProvider,
    AIResponse,
    ToolCall
)


class GroqProvider(AIProvider):

    def __init__(self):
        self.client = Groq(
            api_key=GROQ_API_KEY
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
"""

        messages = [
            {
                "role": "user",
                "content": prompt
            }
        ]

        # -----------------------------------------
        # Convert our tool definitions to Groq
        # format
        # -----------------------------------------

        groq_tools = None

        if tools:

            groq_tools = []

            for tool in tools:

                groq_tools.append({
                    "type": "function",
                    "function": tool
                })

        # -----------------------------------------
        # Ask Groq
        # -----------------------------------------

        response = self.client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=messages,
            tools=groq_tools
        )

        message = response.choices[0].message

        # -----------------------------------------
        # Check for tool call
        # -----------------------------------------

        if message.tool_calls:

            tool_call = message.tool_calls[0]

            import json

            arguments = json.loads(
                tool_call.function.arguments
            )

            return AIResponse(
                tool_call=ToolCall(
                    name=tool_call.function.name,
                    arguments=arguments
                )
            )

        # -----------------------------------------
        # Normal answer
        # -----------------------------------------

        return AIResponse(
            text=message.content
        )