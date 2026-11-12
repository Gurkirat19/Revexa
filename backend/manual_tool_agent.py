from google import genai
from google.genai import types

from app.config import GEMINI_API_KEY

from app.github.client import get_repository_tree

from app.repository.discovery import discover_files
from app.repository.context import load_repository_files

from app.agent.tools import (
    search_repository,
    read_repository_file
)


# --------------------------------------------------
# Gemini client
# --------------------------------------------------

client = genai.Client(
    api_key=GEMINI_API_KEY
)


# --------------------------------------------------
# Repository
# --------------------------------------------------

owner = "Gurkirat19"
repo = "JavaScript"


# --------------------------------------------------
# Load repository
# --------------------------------------------------

print("\nLoading repository...")


tree_result = get_repository_tree(
    owner,
    repo
)


discovered_files = discover_files(
    tree_result["tree"]
)


loaded_files = load_repository_files(
    owner,
    repo,
    discovered_files
)


print(
    f"Loaded {len(loaded_files)} files."
)


# --------------------------------------------------
# Gemini tools
# --------------------------------------------------

tools = [

    types.Tool(

        function_declarations=[

            # ------------------------------------------
            # Search repository
            # ------------------------------------------

            types.FunctionDeclaration(

                name="search_repository",

                description=(
                    "Search the repository source code "
                    "for a keyword, function name, "
                    "variable, class, or concept."
                ),

                parameters=types.Schema(

                    type="OBJECT",

                    properties={

                        "query": types.Schema(

                            type="STRING",

                            description=(
                                "A keyword, function name, "
                                "variable name, class name, "
                                "or code pattern to search for."
                            )
                        )
                    },

                    required=[
                        "query"
                    ]
                )
            ),


            # ------------------------------------------
            # Read repository file
            # ------------------------------------------

            types.FunctionDeclaration(

                name="read_repository_file",

                description=(
                    "Read the complete contents of a "
                    "specific file from the repository. "
                    "Use this when search results identify "
                    "a relevant file that needs deeper analysis."
                ),

                parameters=types.Schema(

                    type="OBJECT",

                    properties={

                        "path": types.Schema(

                            type="STRING",

                            description=(
                                "Repository-relative "
                                "file path."
                            )
                        )
                    },

                    required=[
                        "path"
                    ]
                )
            )
        ]
    )
]


# --------------------------------------------------
# User question
# --------------------------------------------------

question = (
    "Explain how the sayMyName function works "
    "in this repository."
)


# --------------------------------------------------
# Conversation contents
# --------------------------------------------------

contents = [

    types.Content(

        role="user",

        parts=[

            types.Part.from_text(
                text=question
            )
        ]
    )
]


# --------------------------------------------------
# Agent loop
# --------------------------------------------------

while True:

    print("\nAsking Gemini...")

    response = client.models.generate_content(

        model="gemini-3.6-flash",

        contents=contents,

        config=types.GenerateContentConfig(

            tools=[
                *tools
            ],

            automatic_function_calling=
            types.AutomaticFunctionCallingConfig(
                disable=True
            )
        )
    )


    # --------------------------------------------------
    # Get Gemini's response
    # --------------------------------------------------

    model_content = (
        response
        .candidates[0]
        .content
    )


    # Add Gemini response to conversation

    contents.append(
        model_content
    )


    # --------------------------------------------------
    # Find function call
    # --------------------------------------------------

    function_call = None


    for part in model_content.parts:

        if part.function_call:

            function_call = (
                part.function_call
            )

            break


    # --------------------------------------------------
    # No function call
    # Gemini has produced final answer
    # --------------------------------------------------

    if function_call is None:

        print("\n" + "=" * 60)

        print("FINAL ANSWER")

        print("=" * 60)


        for part in model_content.parts:

            if part.text:

                print(
                    part.text
                )

        break


    # --------------------------------------------------
    # Gemini requested a tool
    # --------------------------------------------------

    print("\n" + "-" * 60)

    print("GEMINI REQUESTED TOOL")

    print("-" * 60)


    print(
        "Tool:",
        function_call.name
    )


    print(
        "Arguments:",
        function_call.args
    )


    # --------------------------------------------------
    # Execute search tool
    # --------------------------------------------------

    if function_call.name == "search_repository":

        query = function_call.args["query"]


        print(
            f"\nSearching repository for: {query}"
        )


        result = search_repository(

            loaded_files,

            query
        )


        # search_code returns a list
        # FunctionResponse requires a dictionary

        tool_response = {

            "results": result
        }


        print(
            f"Found {len(result)} matches."
        )


    # --------------------------------------------------
    # Execute file-reading tool
    # --------------------------------------------------

    elif function_call.name == "read_repository_file":

        path = function_call.args["path"]


        print(
            f"\nReading file: {path}"
        )


        tool_response = read_repository_file(

            owner,

            repo,

            path
        )


        print(
            "File successfully read."
        )


    # --------------------------------------------------
    # Unknown tool
    # --------------------------------------------------

    else:

        tool_response = {

            "error": (
                f"Unknown tool requested: "
                f"{function_call.name}"
            )
        }


    # --------------------------------------------------
    # Send tool result back to Gemini
    # --------------------------------------------------

    function_response = (
        types.Part.from_function_response(

            name=function_call.name,

            response=tool_response
        )
    )


    contents.append(

        types.Content(

            role="user",

            parts=[
                function_response
            ]
        )
    )