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


def remove_path(path_to_file: str, path_to_concat: str) -> None:
    __PATH__ = path.abspath(
        concat_path(
            path_to_file,
            path_to_concat
        )
    )
    if __PATH__ in sys.path:
        sys.path.remove(__PATH__)
# [END manipulate file path]


def concat_path(path_to_file: str, path_to_concat: str) -> str:
    "Use with __file__ to create a safe file path regardless of call source"
    return path.join(
        path.dirname(path_to_file),
        path_to_concat
    )
