IGNORED_DIRECTORIES = {
    ".git/",
    "node_modules/",
    "dist/",
    "build/",
    "coverage/",
    "vendor/",
    "__pycache__/",
}


IGNORED_FILES = {
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "poetry.lock",
}


ALLOWED_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".java",
    ".c",
    ".cpp",
    ".h",
    ".hpp",
    ".cs",
    ".go",
    ".rs",
    ".php",
    ".rb",
    ".swift",
    ".kt",
    ".kts",
    ".html",
    ".css",
    ".scss",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".md",
}


def discover_files(tree):
    """
    Convert the GitHub repository tree into
    a clean list of useful files.
    """

    discovered_files = []

    for item in tree:

        if item["type"] != "blob":
            continue

        path = item["path"]

        if should_ignore_file(path):
            continue

        discovered_files.append({
            "path": path,
            "sha": item.get("sha"),
            "size": item.get("size", 0)
        })

    return discovered_files


def should_ignore_file(path):
    """
    Decide whether a repository file should
    be excluded from AI analysis.
    """

    path_lower = path.lower()

    for directory in IGNORED_DIRECTORIES:
        if path_lower.startswith(directory):
            return True

    filename = path_lower.split("/")[-1]

    if filename in IGNORED_FILES:
        return True

    if filename.startswith(".env"):
        return True

    if "." not in filename:
        return False

    extension = "." + filename.rsplit(".", 1)[1]

    if extension not in ALLOWED_EXTENSIONS:
        return True

    return False