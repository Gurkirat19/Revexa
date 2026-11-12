from app.ai.repository_agent import repository_agent


result = repository_agent(
    owner="Gurkirat19",
    repo="JavaScript",
    question=(
        "Explain how the sayMyName function works "
        "and which file contains it."
    )
)


print("\nQUESTION:")
print(result["question"])


print("\nANSWER:")
print(result["answer"])