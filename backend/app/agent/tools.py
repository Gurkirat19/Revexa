from app.github.client import read_file


# Files loaded during this agent session.
# This prevents downloading the same file repeatedly.
from contextvars import ContextVar
file_cache_context = ContextVar("repository_file_cache", default=None)


def search_repository(
    owner,
    repo,
    discovered_files,
    query
):
    """
    Search repository source code.

    The repository is not downloaded up front.

    Files are downloaded only when the
    agent performs a search.
    """

    if not query or not query.strip():

        return {
            "error": "Search query cannot be empty."
        }


    query = query.lower().strip()


    file_cache = file_cache_context.get()
    if file_cache is None:
        file_cache = {}
        file_cache_context.set(file_cache)

    matches = []


    for file in discovered_files:

        path = file["path"]

        # ---------------------------------
        # READ FILE LAZILY
        # ---------------------------------

        if (owner, repo, path) not in file_cache:

            try:

                result = read_file(
                    owner,
                    repo,
                    path
                )

                file_cache[(owner, repo, path)] = result

            except Exception:

                continue


        content = file_cache[(owner, repo, path)]


        # ---------------------------------
        # SEARCH CONTENT
        # ---------------------------------

        lines = content["content"].splitlines()


        for line_number, line in enumerate(
            lines,
            start=1
        ):

            if query in line.lower():

                matches.append({

                    "path": path,

                    "line": line_number,

                    "content": line.strip()

                })


                if len(matches) >= 20:

                    return matches


    return matches



def read_repository_file(
    owner,
    repo,
    path
):
    """
    Read one specific repository file.
    """

    file_cache = file_cache_context.get() or {}
    if (owner, repo, path) in file_cache:
        return file_cache[(owner, repo, path)]


    result = read_file(
        owner,
        repo,
        path
    )


    file_cache[(owner, repo, path)] = result

    return result