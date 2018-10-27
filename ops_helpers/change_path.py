from os import path
import sys


# [START manipulate file path]
def add_path(path_to_file: str, path_to_concat: str) -> None:
    "Append a path relative to the current file"
    __PATH__ = path.abspath(
        concat_path(
            path_to_file,
            path_to_concat
        )
    )
    if __PATH__ not in sys.path:
        sys.path.insert(0, __PATH__)


def remove_path(basename_to_remove: str) -> None:
    "Remove any paths with this basename; useful for handling pytest"
    sys.path = [p for p in sys.path if path.basename(p) != basename_to_remove]
# [END manipulate file path]


def concat_path(path_to_file: str, path_to_concat: str) -> str:
    "Use with __file__ to create a safe file path regardless of call source"
    return path.join(
        path.dirname(path_to_file),
        path_to_concat
    )
