from app.ai.repository_agent import repository_agent


result = repository_agent(
    "Gurkirat19",
    "JavaScript",
    "Explain how functions are implemented in this repository."
)


print("\nQUESTION:")
print(result["question"])


print("\nFILES USED:")

for file in result["files_used"]:
    print("-", file)


print("\nTEST FILES:")

for file in result["test_files"]:
    print("-", file)


print("\nAI ANSWER:")
print(result["answer"])