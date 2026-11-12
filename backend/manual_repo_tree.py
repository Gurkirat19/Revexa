from app.github.client import get_repository_tree


result = get_repository_tree(
    "Gurkirat19",
    "JavaScript"
)


tree = result["tree"]

print("Total entries:", len(tree))

print("\nFirst 10 entries:")

for item in tree[:10]:
    print(
        item["type"],
        "->",
        item["path"]
    )