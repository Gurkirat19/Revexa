from app.github.client import get_repository_tree
from app.repository.discovery import discover_files
from app.repository.loader import load_files
from app.repository.search import search_code


owner = "Gurkirat19"
repo = "JavaScript"


tree_result = get_repository_tree(
    owner,
    repo
)

discovered_files = discover_files(
    tree_result["tree"]
)

loaded_files = load_files(
    owner,
    repo,
    discovered_files
)

results = search_code(
    loaded_files,
    "function"
)


print("Matches:", len(results))

print("\nResults:")

for result in results[:20]:

    print(
        f"{result['path']}:"
        f"{result['line']} "
        f"-> {result['content']}"
    )