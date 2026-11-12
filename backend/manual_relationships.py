from app.github.client import get_repository_tree
from app.repository.discovery import discover_files
from app.repository.loader import load_files
from app.repository.relationships import (
    find_tests,
    find_related_files
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

loaded_files = load_files(
    owner,
    repo,
    discovered_files
)


tests = find_tests(
    loaded_files
)

print("Test files:")

for file in tests:
    print("-", file["path"])


print("\nRelated files:")

related = find_related_files(
    loaded_files,
    "13_functions.js"
)

for file in related:
    print("-", file["path"])