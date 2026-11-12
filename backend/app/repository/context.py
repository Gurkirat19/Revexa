import re

from app.github.client import read_file

from app.repository.search import search_code

from app.repository.relationships import (
    find_tests
)


STOP_WORDS = {
    "how",
    "what",
    "where",
    "when",
    "why",
    "which",
    "who",
    "is",
    "are",
    "the",
    "this",
    "that",
    "in",
    "on",
    "for",
    "of",
    "to",
    "and",
    "or",
    "a",
    "an",
    "does",
    "do",
    "can",
    "could",
    "explain",
    "show",
    "tell",
    "me",
    "about",
    "repository",
}


def extract_search_terms(question):
    """
    Extract useful search terms from a user question.
    """

    words = re.findall(
        r"[A-Za-z0-9_]+",
        question.lower()
    )

    search_terms = []

    for word in words:

        if word in STOP_WORDS:
            continue

        if len(word) < 3:
            continue

        if word not in search_terms:
            search_terms.append(word)

    return search_terms


def load_repository_files(
    owner,
    repo,
    discovered_files
):
    """
    Load the source code for discovered files.
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


def build_repository_context(
    owner,
    repo,
    discovered_files,
    question
):
    """
    Build repository context based on a user question.
    """

    loaded_files = load_repository_files(
        owner,
        repo,
        discovered_files
    )

    search_terms = extract_search_terms(
        question
    )

    all_search_results = []

    for term in search_terms:

        results = search_code(
            loaded_files,
            term
        )

        all_search_results.extend(
            results
        )

    unique_paths = []

    for result in all_search_results:

        path = result["path"]

        if path not in unique_paths:
            unique_paths.append(path)

    context_files = []

    for file in loaded_files:

        if file["path"] in unique_paths:

            context_files.append(file)

    test_files = find_tests(
        loaded_files
    )

    return {
        "question": question,
        "search_terms": search_terms,
        "files": context_files,
        "test_files": [
            file["path"]
            for file in test_files
        ],
        "search_results": all_search_results
    }