from app.github.client import get_repository_tree

from app.repository.discovery import discover_files
from app.repository.context import load_repository_files

from app.agent.tools import (
    search_repository,
    read_repository_file
)


owner = "Gurkirat19"
repo = "JavaScript"


# Get repository structure

tree_result = get_repository_tree(
    owner,
    repo
)


# Discover useful files

discovered_files = discover_files(
    tree_result["tree"]
)


# Load files for searching

loaded_files = load_repository_files(
    owner,
    repo,
    discovered_files
)


# --------------------------------------------------
# Test search tool
# --------------------------------------------------

results = search_repository(
    loaded_files,
    "function"
)


print("\nSEARCH RESULTS:")

print(
    "Matches:",
    len(results)
)


for result in results[:5]:

    print(
        result["path"],
        "line",
        result["line"],
        "->",
        result["content"]
    )


# --------------------------------------------------
# Test read tool
# --------------------------------------------------

file_result = read_repository_file(
    owner,
    repo,
    "13_functions.js"
)


print("\nFILE READ:")

print(
    "Path:",
    file_result["path"]
)

print(
    "Size:",
    file_result["size"]
)

print(
    "\nFirst 10 lines:"
)

for line in file_result["content"].splitlines()[:10]:

    print(line)