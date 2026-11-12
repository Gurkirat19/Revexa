def calculate_risk(files):
    """
    Calculate a basic risk score for the changed files.
    """

    score = 0
    reasons = []

    for file in files:

        filename = file["filename"].lower()

        additions = file.get("additions", 0)
        deletions = file.get("deletions", 0)

        # Large changes are generally harder to review
        if additions + deletions > 100:
            score += 2
            reasons.append(
                f"Large change in {file['filename']}"
            )

        # Authentication/security related code
        if any(word in filename for word in [
            "auth",
            "login",
            "security",
            "permission"
        ]):
            score += 3
            reasons.append(
                f"Security-sensitive file: {file['filename']}"
            )

        # Database related changes
        if any(word in filename for word in [
            "database",
            "db",
            "migration",
            "schema"
        ]):
            score += 3
            reasons.append(
                f"Database-related file: {file['filename']}"
            )

        # Payment related code
        if any(word in filename for word in [
            "payment",
            "billing",
            "checkout"
        ]):
            score += 3
            reasons.append(
                f"Payment-related file: {file['filename']}"
            )

        # CI/CD changes
        if (
            filename.startswith(".github/")
            or "dockerfile" in filename
            or "docker-compose" in filename
        ):
            score += 2
            reasons.append(
                f"Infrastructure/CI change: {file['filename']}"
            )

    if score >= 7:
        level = "HIGH"
    elif score >= 3:
        level = "MEDIUM"
    else:
        level = "LOW"

    return {
        "score": score,
        "level": level,
        "reasons": reasons
    }