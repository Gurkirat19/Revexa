from app.ai.provider_factory import get_provider

from app.ai.provider import get_repository_tools

from app.github.client import get_repository_tree

from app.repository.discovery import discover_files

from app.agent.tools import (
    search_repository,
    read_repository_file
)


def _ask_with_fallback(provider, selected_model, *, question, context, tools):
    """Call the selected provider and optionally fall back once to the other provider."""
    try:
        return provider.ask(question=question, context=context, tools=tools), selected_model, provider
    except Exception as primary_error:
        import os
        fallback_enabled = os.getenv("AI_FALLBACK_ENABLED", "true").strip().lower() == "true"
        fallback_model = "groq" if selected_model == "gemini" else "gemini"
        if not fallback_enabled:
            raise RuntimeError(f"{selected_model.title()} provider failed: {primary_error}") from primary_error
        try:
            fallback_provider = get_provider(fallback_model)
            fallback_response = fallback_provider.ask(question=question, context=context, tools=tools)
            return fallback_response, fallback_model, fallback_provider
        except Exception as fallback_error:
            raise RuntimeError(
                f"{selected_model.title()} failed and {fallback_model.title()} fallback also failed. "
                f"Primary error: {primary_error}. Fallback error: {fallback_error}"
            ) from fallback_error


def discover_repository(owner, repo):
    """
    Discover useful files in the repository.

    Only the repository tree is downloaded here.
    File contents are loaded later when required.
    """

    tree_result = get_repository_tree(
        owner,
        repo
    )

    discovered_files = discover_files(
        tree_result["tree"]
    )

    return discovered_files


def execute_tool(
    tool_name,
    arguments,
    discovered_files,
    owner,
    repo
):
    """
    Execute a tool requested by the AI.
    """

    # -----------------------------------------
    # SEARCH REPOSITORY
    # -----------------------------------------

    if tool_name == "search_repository":

        query = arguments.get(
            "query",
            ""
        )

        if not query or not query.strip():

            return {
                "error": (
                    "Search query cannot be empty. "
                    "You must provide a meaningful "
                    "keyword, function name, class name, "
                    "variable, or code pattern."
                )
            }

        query = query.strip()

        print(
            f"Searching repository for: {query}"
        )

        result = search_repository(
            owner,
            repo,
            discovered_files,
            query
        )

        if isinstance(result, dict):

            if "error" in result:

                print(
                    "Search error:",
                    result["error"]
                )

            return result

        print(
            f"Found {len(result)} matches."
        )

        return result


    # -----------------------------------------
    # READ REPOSITORY FILE
    # -----------------------------------------

    if tool_name == "read_repository_file":

        path = arguments.get(
            "path",
            ""
        )

        if not path or not path.strip():

            return {
                "error": (
                    "File path cannot be empty."
                )
            }

        path = path.strip()

        print(
            f"Reading file: {path}"
        )

        result = read_repository_file(
            owner,
            repo,
            path
        )

        if isinstance(result, dict):

            if "error" in result:

                print(
                    "File read error:",
                    result["error"]
                )

            else:

                print(
                    "File successfully read."
                )

            return result

        return result


    # -----------------------------------------
    # UNKNOWN TOOL
    # -----------------------------------------

    return {
        "error": (
            f"Unknown tool requested: "
            f"{tool_name}"
        )
    }


def repository_agent(
    owner,
    repo,
    question,
    model="gemini"
):
    """
    Repository intelligence agent.

    Flow:

    User question
          ↓
    Repository discovery
          ↓
    AI reasoning
          ↓
    Search / Read tools
          ↓
    Tool result added to history
          ↓
    AI reasoning again
          ↓
    Final answer
    """

    # -----------------------------------------
    # SELECT AI PROVIDER
    # -----------------------------------------

    print(
        f"Selected AI model: {model}"
    )

    try:
        provider = get_provider(model)
    except Exception as error:

        return {
            "question": question,
            "answer": "",
            "error": str(error),
            "model": model
        }


    # -----------------------------------------
    # DISCOVER REPOSITORY
    # -----------------------------------------

    print(
        "Discovering repository..."
    )

    try:

        discovered_files = discover_repository(
            owner,
            repo
        )

    except Exception as error:

        print(
            "Repository discovery failed:",
            error
        )

        return {
            "question": question,
            "answer": "",
            "error": (
                "Repository discovery failed: "
                f"{str(error)}"
            ),
            "model": model
        }

    print(
        f"Discovered "
        f"{len(discovered_files)} files."
    )


    # -----------------------------------------
    # TOOLS
    # -----------------------------------------

    tools = get_repository_tools()


    # -----------------------------------------
    # AGENT HISTORY
    # -----------------------------------------

    history = []


    # -----------------------------------------
    # TRACK PREVIOUS TOOL CALLS
    # -----------------------------------------

    previous_calls = set()


    # -----------------------------------------
    # MAXIMUM STEPS
    # -----------------------------------------

    max_steps = 8


    # -----------------------------------------
    # AGENT LOOP
    # -----------------------------------------

    for step in range(max_steps):

        print(
            f"Agent step {step + 1}"
        )


        # -------------------------------------
        # BUILD COMPLETE CONTEXT
        # -------------------------------------

        context_parts = []

        context_parts.append(
            "Repository files discovered:"
        )

        for file in discovered_files[:100]:

            context_parts.append(
                f"- {file['path']}"
            )

        context_parts.append(
            "\nPrevious investigation:"
        )

        if history:

            for item in history:

                context_parts.append(
                    item
                )

        else:

            context_parts.append(
                "No source files have been read yet. You MUST inspect relevant files "
                "with search_repository/read_repository_file before answering. "
                "If no relevant evidence can be retrieved, state that clearly."
            )

        context = "\n".join(
            context_parts
        )


        # -------------------------------------
        # CURRENT QUESTION
        # -------------------------------------

        current_question = f"""
You are a senior software engineer investigating
a GitHub repository.

The user asked:

{question}

Your job is to investigate the repository and
give a clear, concise, evidence-based answer.

IMPORTANT RULES:

1. You MUST perform at least one relevant repository search or file read before making conclusions.

2. If a search returns matching files,
   read only the files that are most relevant
   to the user's question.

3. Do NOT repeat a search that has already
   been performed.

4. Do NOT call search_repository with an
   empty query.

5. If previous investigation already contains
   enough information to answer the question,
   provide the final answer instead of using
   another tool.

6. Prefer the smallest number of tool calls
   necessary to answer the user's question.

7. When a search returns matching files,
   identify which files are directly relevant
   before reading them.

8. Do NOT read unrelated files just to gather
   additional context.

9. If you have already read a relevant file,
   analyze the information from that file
   before requesting another tool call.

10. After you have enough evidence to answer
    the user's question, STOP investigating and
    provide the final answer.

11. If a previous search returned zero results,
    do NOT repeat the same search.

    Instead:

    - Try another relevant search term
    - Analyze the evidence already collected
    - Or provide the answer if enough evidence
      already exists

12. Do not invent files, functions, classes,
    variables, dependencies, or behavior.

13. Base your answer only on evidence found
    in the repository.

14. Clearly distinguish between:

    - What exists
    - What is missing
    - Potential risks or problems
    - What could be added or improved

15. Keep the final answer concise and useful.

16. Do NOT use Markdown tables.

17. Do NOT write a huge essay.

18. Use short sections and bullet points.

19. If something requested by the user does NOT
    exist in the repository, do not simply say
    "it does not exist."

    Explain:

    - what was found instead
    - what is missing
    - what would need to be added
    - a practical implementation approach

20. Do not request another tool if the previous
    investigation already provides sufficient
    evidence.

21. Do not read more than necessary to answer
    the user's specific question.

When you have enough information, structure
your final answer like this:

SUMMARY

Give a short 1-3 sentence explanation of the
main answer.

WHAT I FOUND

- Important finding
- Important finding
- Important finding

EVIDENCE

- `file/path` — relevant function, variable,
  class, or code behavior

- `file/path` — relevant function, variable,
  class, or code behavior

WHAT IS MISSING

- Missing functionality
- Missing functionality
- Missing functionality

RISKS OR CONCERNS

- Important risk
- Important risk

HOW TO ADD OR IMPROVE IT

If something is missing or needs improvement,
give a practical implementation approach:

1. First step
2. Second step
3. Third step
4. Fourth step

If nothing needs to be added, write:

"Nothing additional is required."

FINAL RECOMMENDATION

Give one concise and practical next step.

Do not repeat the same information between
sections.

Do not include unnecessary explanations.

Previous investigation is provided in the
context.

IMPORTANT:

If the previous investigation already contains
enough evidence to answer the user's question,
DO NOT call another tool.

Return the final answer.
"""


        # -------------------------------------
        # ASK AI
        # -------------------------------------

        try:

            response, active_model, provider = _ask_with_fallback(
                provider, model, question=current_question, context=context, tools=tools
            )
            model = active_model

        except Exception as error:

            print(
                "AI provider error:",
                error
            )

            return {
                "question": question,
                "answer": "",
                "error": (
                    "AI provider error: "
                    f"{str(error)}"
                ),
                "model": model
            }


        # -------------------------------------
        # FINAL ANSWER
        # -------------------------------------

        if response.text and response.text.strip():
            if not history:
                history.append(
                    "The model attempted to answer without inspecting any source file. "
                    "No repository evidence has been collected. Do not claim an analysis was completed."
                )
                continue
            print("Agent produced evidence-backed final answer.")
            return {
                "question": question,
                "answer": response.text.strip(),
                "model": model,
                "files_discovered": len(discovered_files),
                "files_inspected": len({
                    item for item in history if "read_repository_file" in item
                }),
                "analysis_status": "completed"
            }


        # -------------------------------------
        # TOOL CALL
        # -------------------------------------

        if response.tool_call:

            tool_name = (
                response.tool_call.name
            )

            arguments = (
                response.tool_call.arguments
            )

            print(
                "AI requested tool:",
                tool_name
            )

            print(
                "Arguments:",
                arguments
            )


            # ---------------------------------
            # CREATE CALL SIGNATURE
            # ---------------------------------

            call_signature = (
                tool_name,
                str(
                    sorted(
                        arguments.items()
                    )
                )
            )


            # ---------------------------------
            # PREVENT REPEATED TOOL CALLS
            # ---------------------------------

            if call_signature in previous_calls:

                print(
                    "Repeated tool call detected."
                )

                history.append(
                    f"""
The AI attempted to repeat this tool call:

Tool:

{tool_name}

Arguments:

{arguments}

This exact operation was already performed.

Do not repeat it.

Use the existing investigation results
to produce the final answer.
"""
                )

                continue


            previous_calls.add(
                call_signature
            )


            # ---------------------------------
            # EXECUTE TOOL
            # ---------------------------------

            result = execute_tool(
                tool_name,
                arguments,
                discovered_files,
                owner,
                repo
            )


            # ---------------------------------
            # SAVE RESULT TO HISTORY
            # ---------------------------------

            history.append(
                f"""
Tool used:

{tool_name}

Arguments:

{arguments}

Result:

{result}
"""
            )

            continue


    # -----------------------------------------
    # MAX STEPS
    # -----------------------------------------

    print(
        "Agent reached maximum analysis steps."
    )


    # -----------------------------------------
    # ONE LAST AI CALL WITHOUT TOOLS
    # -----------------------------------------

    try:

        final_context = "\n".join(
            history
        )

        final_question = f"""
Answer the user's original question:

{question}

You have finished the repository investigation.

Use ONLY the evidence collected below.

Repository investigation:

{final_context}

IMPORTANT:

- Do not request another tool.
- Do not search for anything else.
- Do not invent information.
- Do not assume functionality that was not found.
- If the evidence is incomplete, clearly say so.
- Give a concise engineering answer.
- Return only the final answer.
"""

        final_response, model, provider = _ask_with_fallback(
            provider, model, question=final_question, context=final_context, tools=[]
        )

        if final_response.text:

            print(
                "Final answer generated."
            )

            if not history:
                raise RuntimeError("No repository evidence was collected; refusing to return a success report.")
            return {
                "question": question,
                "answer": final_response.text.strip(),
                "model": model,
                "files_discovered": len(discovered_files),
                "analysis_status": "completed"
            }


    except Exception as error:

        print(
            "Final answer generation failed:",
            error
        )


    # -----------------------------------------
    # FALLBACK
    # -----------------------------------------

    return {
        "question": question,
        "answer": (
            "The repository investigation "
            "could not be completed."
        ),
        "error": "MAX_AGENT_STEPS",
        "model": model
    }