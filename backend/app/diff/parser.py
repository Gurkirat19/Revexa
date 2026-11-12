IGNORED_FILES = {
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "poetry.lock"
}


def parse_pr_files(files):
    parsed_files = []

    for file in files:
        filename = file.get("filename", "")

        if should_ignore_file(filename):
            continue

        parsed_files.append({
            "filename": filename,
            "status": file.get("status"),
            "additions": file.get("additions", 0),
            "deletions": file.get("deletions", 0),
            "patch": file.get("patch", "")
        })

    return parsed_files


def should_ignore_file(filename):
    if filename in IGNORED_FILES:
        return True

    if filename.startswith("node_modules/"):
        return True

    if filename.startswith("dist/"):
        return True

    if filename.startswith("build/"):
        return True

    return False