"""Offline unit tests for review-diff grounding (no API calls)."""
import os

# app.config validates these at import time; dummy values keep these unit tests offline.
os.environ.setdefault("GITHUB_TOKEN", "test-token")
os.environ.setdefault("GEMINI_API_KEY", "test-gemini-key")
os.environ.setdefault("GROQ_API_KEY", "test-groq-key")

from app.ai.reviewer import _changed_new_lines, build_diff_text


def test_changed_new_lines_tracks_added_lines_and_context():
    patch = """@@ -10,3 +10,4 @@
 context
-old line
+new line one
+new line two
 context after
"""
    assert _changed_new_lines(patch) == {11, 12}


def test_changed_new_lines_supports_multiple_hunks():
    patch = """@@ -1,2 +1,2 @@
-old
+new
 context
@@ -20,1 +20,2 @@
 context
+another
"""
    assert _changed_new_lines(patch) == {1, 21}


def test_build_diff_text_marks_patch_as_untrusted_and_bounds_size():
    files = [{"filename": "app.py", "status": "modified", "additions": 1, "deletions": 0, "patch": "+print('hello')"}]
    text = build_diff_text(files)
    assert "FILE: app.py" in text
    assert "untrusted source code" in text
    assert "print('hello')" in text
    assert len(build_diff_text(files, max_chars=20)) < 200


def test_build_diff_text_handles_empty_file_list():
    assert build_diff_text([]) == "No changed-file diff was provided."
