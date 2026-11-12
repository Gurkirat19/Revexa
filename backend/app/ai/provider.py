from dataclasses import dataclass


@dataclass
class ToolCall:
    name: str
    arguments: dict


@dataclass
class AIResponse:
    text: str | None = None
    tool_call: ToolCall | None = None


class AIProvider:

    def ask(
        self,
        question: str,
        context: str = "",
        tools=None
    ) -> AIResponse:

        raise NotImplementedError(
            "AI provider must implement ask()"
        )


def get_repository_tools():
    return [
        {
            "name": "search_repository",
            "description": (
                "Search the repository source code "
                "for a keyword, function name, "
                "variable, class, or code pattern."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": (
                            "A keyword, function name, "
                            "variable name, class name, "
                            "or code pattern to search for."
                        )
                    }
                },
                "required": ["query"]
            }
        },
        {
            "name": "read_repository_file",
            "description": (
                "Read the complete contents of a "
                "specific file from the repository."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": (
                            "Repository-relative file path."
                        )
                    }
                },
                "required": ["path"]
            }
        }
    ]