from app.github.client import read_file


def load_files(owner, repo, discovered_files):
    """
    Read the contents of discovered repository files.
    """

    loaded_files = []

    for file in discovered_files:

        result = read_file(
            owner,
            repo,
            file["path"]
        )

        loaded_files.append({
            "path": result["path"],
            "content": result["content"]
        })

    return loaded_files