from app.github.client import search_code


result = search_code(
    "Gurkirat19",
    "JavaScript",
    "function"
)


print("Total matches:", result["total_count"])

print("\nSearch results:")

for item in result["results"]:
    print(
        item["path"],
        "->",
        item["url"]
    )