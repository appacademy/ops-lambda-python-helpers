from os import path
import sys


# [START manipulate file path]
def add_path(path_to_file: str, path_to_concat: str) -> None:
    __PATH__ = path.abspath(
        concat_path(
            path_to_file,
            path_to_concat
        )
    )
    sys.path.insert(0, __PATH__)
# [END manipulate file path]


def concat_path(path_to_file: str, path_to_concat: str) -> str:
    return path.join(
        path.dirname(path_to_file),
        path_to_concat
    )
