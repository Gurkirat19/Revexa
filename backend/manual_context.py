from app.github.client import get_repository_tree

from app.repository.discovery import discover_files

from app.repository.context import (
    build_repository_context
)


owner = "Gurkirat19"
repo = "JavaScript"


tree_result = get_repository_tree(
    owner,
    repo
)

discovered_files = discover_files(
    tree_result["tree"]
)


query = "function"


context = build_repository_context(
    owner,
    repo,
    discovered_files,
    query
)


print("Query:")
print(context["query"])


print("\nRelevant files:")

for file in context["files"]:

    print(
        "-",
        file["path"]
    )


print("\nSearch matches:")

for result in context["search_results"][:10]:

    print(
        f"{result['path']}:"
        f"{result['line']} "
        f"-> {result['content']}"
    )


print("\nTest files:")

for file in context["test_files"]:

    print(
        "-",
        file
    )