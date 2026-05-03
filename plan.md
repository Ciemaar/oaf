1.  **Address the inline import in `src/orbLib/main.py`**
    *   Move `from sqlalchemy import select` to the top of `src/orbLib/main.py` using `replace_with_git_merge_diff`.
    *   Ensure this doesn't break any dependencies or runtime behavior.
2.  **Fix typing errors reported by `pyright` in `src/orbLib/main.py`**
    *   Use `replace_with_git_merge_diff` to add `# type: ignore` or correct typing for `OaF.OafServer(None)`.
3.  **Run the test suite**
    *   Run `tox -e py312` and `pytest` to make sure we didn't break functionality.
4.  **Run Pre-commit Checks**
    *   Complete pre-commit steps to ensure proper testing, verification, review, and reflection are done.
5.  **Submit Changes**
    *   Submit the clean codebase to main.
