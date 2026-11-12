def search_code(files, query):
    """
    Search for a text query across repository files.
    """

    query = query.lower()

    matches = []

    for file in files:

        content = file["content"]

        lines = content.splitlines()

        for line_number, line in enumerate(
            lines,
            start=1
        ):

            if query in line.lower():

                matches.append({
                    "path": file["path"],
                    "line": line_number,
                    "content": line.strip()
                })

    return matches