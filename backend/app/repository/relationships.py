def find_tests(files):
    """
    Find files that appear to contain tests.
    """

    test_files = []

    for file in files:

        path = file["path"].lower()
        filename = path.split("/")[-1]

        if (
            "tests/" in path
            or "test/" in path
            or filename.startswith("test.")
            or filename.startswith("test_")
            or filename.startswith("test-")
            or ".test." in filename
            or ".spec." in filename
        ):
            test_files.append(file)

    return test_files


def find_related_files(files, target_path):
    """
    Find files that appear to be related
    to a target file based on filename similarity.
    """

    target_name = target_path.split("/")[-1]

    if "." in target_name:
        target_stem = target_name.rsplit(
            ".",
            1
        )[0].lower()
    else:
        target_stem = target_name.lower()

    related_files = []

    for file in files:

        path = file["path"]

        if path == target_path:
            continue

        filename = path.split("/")[-1].lower()

        if target_stem in filename:
            related_files.append(file)

    return related_files