from app.github.client import get_repository_tree
from app.repository.discovery import discover_files


result = get_repository_tree(
    "Gurkirat19",
    "JavaScript"
)


tree = result["tree"]

files = discover_files(tree)


print("Total repository entries:", len(tree))
print("Useful files:", len(files))

print("\nDiscovered files:")

for file in files:
    print(file["path"])