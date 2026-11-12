from app.github.client import read_file


result = read_file(
    "Gurkirat19",
    "JavaScript",
    "18_truth_false_values.js"
)


print("File:", result["path"])
print("Size:", result["size"])

print("\nContent:\n")
print(result["content"])