from app.github.client import parse_repo_url


repo_url = "https://github.com/Gurkirat19/JavaScript"

result = parse_repo_url(repo_url)

print(result)